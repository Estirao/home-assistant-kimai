#!/usr/bin/env python3
"""Release helper. Standard library only; never connects to Home Assistant.

Commands: detect, prepare, branding, verify-manifest <file>, release.
This full repository contains its app configuration and startup script.
Publication only changes the top-level version and generated release/presentation
files; it never reads credentials from, or connects to, a Home Assistant server.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "kimai"


def repository_name() -> str:
    value = os.environ.get("GITHUB_REPOSITORY", "")
    if not value:
        metadata = (ROOT / "repository.yaml").read_text(encoding="utf-8")
        found = re.search(r"https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", metadata)
        if not found:
            raise ValueError("repository.yaml must contain a GitHub repository URL.")
        value = found.group(1)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", value):
        raise ValueError("Invalid GitHub repository name.")
    return value


REPO = repository_name()
UPSTREAM = "kimai/kimai"
REGISTRY_PREFIX = f"ghcr.io/{REPO.split('/')[0].lower()}"
IMAGE = f"{REGISTRY_PREFIX}/kimai-ha"
VERSION = re.compile(r"v?((?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*))\Z")
CONFIG_VERSION = re.compile(
    r"(?m)^version:[ \t]*([\"']?)([0-9]+\.[0-9]+\.[0-9]+)\1[ \t]*(?:#.*)?$"
)
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

# GitHub user/team mentions are stripped from copied upstream release notes so
# publishing this downstream package never @-mentions or notifies upstream
# contributors. Email addresses and URL paths containing /@ are left alone.
GITHUB_MENTION = re.compile(
    r"(?<![A-Za-z0-9._%+/\-])@([A-Za-z0-9][A-Za-z0-9-]{0,38}(?:/[A-Za-z0-9][A-Za-z0-9-]{0,38})?)"
)


def sanitize_mentions(text: str) -> str:
    return GITHUB_MENTION.sub(lambda match: match.group(1), text)


def contains_mentions(text: str) -> bool:
    return GITHUB_MENTION.search(text) is not None


def normalized_version(value: str) -> str:
    match = VERSION.fullmatch(value)
    if not match:
        raise ValueError(f"Not a stable X.Y.Z version: {value!r}")
    return match.group(1)


def version_key(value: str) -> tuple[int, int, int]:
    return tuple(int(part) for part in normalized_version(value).split("."))  # type: ignore[return-value]


def stable_version(release: dict[str, Any]) -> str:
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("The upstream release is a draft or prerelease; refusing to publish it.")
    return normalized_version(str(release["tag_name"]))


def current_version(text: str) -> str:
    matches = list(CONFIG_VERSION.finditer(text))
    if len(matches) != 1:
        raise ValueError("kimai/config.yaml needs exactly one top-level version: X.Y.Z line.")
    return normalized_version(matches[0].group(2))


def replace_version(text: str, target: str) -> str:
    current_version(text)
    target = normalized_version(target)
    return CONFIG_VERSION.sub(lambda _: f'version: "{target}"', text, count=1)


def compute_plan(current: str, target: str, release_exists: bool,
                 recorded: bool, presentation_missing: bool) -> dict[str, bool]:
    if version_key(target) < version_key(current):
        raise ValueError(
            f"Upstream returned {target}, older than config.yaml ({current}). "
            "No automatic downgrade is permitted. Check the upstream release/API."
        )
    # A durable record allows retrying release creation without replacing an
    # image already advertised to Home Assistant by a previous successful push.
    build = not (release_exists or recorded)
    publish = build or not release_exists or current != target or presentation_missing
    return {"build": build, "publish": publish}


def api(path: str, *, allow_404: bool = False, method: str = "GET",
        payload: dict[str, Any] | None = None) -> Any:
    url = f"https://api.github.com/{path.lstrip('/')}"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "kimai-ha-release"}
    token = os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = json.dumps(payload).encode() if payload is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    # Retry reads only. POSTs are not blindly retried: the next scheduled run
    # inspects the published release before doing anything else.
    attempts = 4 if method == "GET" else 1
    for attempt in range(attempts):
        try:
            req = Request(url, headers=headers, data=data, method=method)
            with urlopen(req, timeout=40) as response:
                return json.load(response)
        except HTTPError as error:
            if error.code == 404 and allow_404:
                return None
            if error.code not in (429, 500, 502, 503, 504) or attempt + 1 == attempts:
                raise RuntimeError(f"GitHub API returned HTTP {error.code} for {path}") from error
        except URLError as error:
            if attempt + 1 == attempts:
                raise RuntimeError(f"GitHub API connection failed for {path}") from error
        time.sleep(2 ** (attempt + 1))
    raise RuntimeError("GitHub API request failed")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_outputs(values: dict[str, str | bool]) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    lines = [f"{key}={str(value).lower() if isinstance(value, bool) else value}" for key, value in values.items()]
    if output:
        with open(output, "a", encoding="utf-8") as stream:
            stream.write("\n".join(lines) + "\n")
    print("\n".join(lines))


def check_files() -> str:
    for name in ("config.yaml", "Dockerfile", "run.sh"):
        if not (APP / name).is_file():
            raise ValueError(f"Missing kimai/{name}. Upload the full repository, not just the workflow.")
    dockerfile = (APP / "Dockerfile").read_text(encoding="utf-8")
    if "FROM kimai/kimai2:${BUILD_VERSION}" not in dockerfile:
        raise ValueError("Dockerfile must use FROM kimai/kimai2:${BUILD_VERSION}, not :2 or :stable.")
    text = (APP / "config.yaml").read_text(encoding="utf-8")
    image_match = re.search(r'^image:[ \t]*[\"\']?([^\s\"\'#]+)', text, re.MULTILINE)
    if not image_match or image_match.group(1) != IMAGE:
        raise ValueError(f"config.yaml must contain image: \"{IMAGE}\"")
    return text


def own_release(version: str) -> dict[str, Any] | None:
    return api(f"repos/{REPO}/releases/tags/v{normalized_version(version)}", allow_404=True)


def detect() -> None:
    text = check_files()
    current = current_version(text)
    latest = api(f"repos/{UPSTREAM}/releases/latest")
    target = stable_version(latest)
    existing = own_release(target)
    released = bool(existing and not existing.get("draft") and not existing.get("prerelease"))
    state = read_json(APP / "release.json")
    recorded = state.get("version") == target and state.get("image") == f"{IMAGE}:{target}"
    changelog = (APP / "CHANGELOG.md").read_text(encoding="utf-8") if (APP / "CHANGELOG.md").exists() else ""
    missing = any(not (APP / name).is_file() for name in ("icon.png", "logo.png", "BRANDING.md"))
    missing = missing or not re.search(rf"(?m)^## {re.escape(target)}(?:\s|$)", changelog)
    # Also republish metadata when an existing downstream release still contains
    # actionable @mentions copied from Kimai's upstream notes.
    missing = missing or bool(existing and contains_mentions(str(existing.get("body") or "")))
    plan = compute_plan(current, target, released, recorded, missing)
    write_outputs({"version": target, "upstream_tag": latest["tag_name"],
                   "registry_prefix": REGISTRY_PREFIX, "image": IMAGE, **plan})
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        message = f"## Kimai\n\nVersion in repository: **{current}**. Latest stable: **{target}**.\n\n"
        message += "Build and basic tests are required.\n" if plan["build"] else "No new image build is needed.\n"
        if version_key(target)[0] > version_key(current)[0]:
            message += "\n**New major release detected. It is NOT blocked, but upgrading Home Assistant remains manual.**\n"
        with open(summary, "a", encoding="utf-8") as stream:
            stream.write(message)


def png_size(data: bytes) -> tuple[int, int]:
    if len(data) < 33 or not data.startswith(PNG_SIGNATURE) or data[12:16] != b"IHDR":
        raise ValueError("The official branding download is not a PNG image.")
    return struct.unpack(">II", data[16:24])


def download_branding(tag: str) -> None:
    # Copy original PNGs unchanged. HA recommends 128px icons, but accepts other
    # square sizes. These official assets are 192px and 512px respectively.
    sources: list[tuple[str, str]] = []
    for destination, source in (("icon.png", "public/touch-icon-192x192.png"),
                                ("logo.png", "public/touch-icon-512x512.png")):
        path = APP / destination
        if path.exists():
            png_size(path.read_bytes())
            continue
        metadata = None
        selected_ref = tag
        for ref in (tag, "main"):
            metadata = api(f"repos/{UPSTREAM}/contents/{source}?{urlencode({'ref': ref})}", allow_404=True)
            if metadata is not None:
                selected_ref = ref
                break
        if not metadata or metadata.get("encoding") != "base64":
            raise ValueError(f"Could not download the official {source}; add the PNG manually.")
        data = base64.b64decode(metadata["content"])
        width, height = png_size(data)
        if width != height or width < 64 or len(data) > 5_000_000:
            raise ValueError(f"Unexpected dimensions or size for {source}.")
        path.write_bytes(data)
        url = f"https://github.com/{UPSTREAM}/blob/{quote(selected_ref, safe='')}/{source}"
        sources.append((destination, url))
    notice = APP / "BRANDING.md"
    if not notice.exists():
        text = "# Kimai branding\n\nThe Kimai name and artwork belong to the Kimai project and their respective owners.\n"
        text += "They identify the third-party software packaged here; this repository is not an official Kimai app.\n\n"
        text += "Original PNG images are copied unchanged from the official Kimai repository.\n\n"
        for filename, url in sources:
            text += f"- {filename}: {url}\n"
        text += "\nUpstream source and licensing: https://github.com/kimai/kimai\n"
        notice.write_text(text, encoding="utf-8")


def release_notes(release: dict[str, Any], previous: str) -> str:
    target = stable_version(release)
    text = f"Kimai **{target}** packaged for Home Assistant OS.\n\n"
    text += f"Image: `{IMAGE}:{target}`. Architectures: `amd64` and `aarch64`.\n\n"
    text += f"[Official Kimai release]({release['html_url']}).\n\n"
    if version_key(target)[0] > version_key(previous)[0]:
        text += "**Major-version change: review the upstream migration and plugin requirements before updating.**\n\n"
    text += "Updating the repository does not upgrade Home Assistant. Keep automatic updates disabled.\n\n"
    text += "Back up Kimai and MariaDB together before updating. A container downgrade does not reverse database migrations.\n\n"
    text += "Basic startup, fresh MariaDB initialization and app-container recreation were tested on both architectures. "
    text += "This is not a test of migration from your existing database or of installed plugins.\n\n"
    text += "## Official Kimai release notes\n\n"
    upstream_body = (release.get("body") or "See the official release linked above.").strip()
    text += sanitize_mentions(upstream_body) + "\n"
    return text


def prepare() -> None:
    target = normalized_version(os.environ["TARGET_VERSION"])
    tag = os.environ["UPSTREAM_TAG"]
    if normalized_version(tag) != target:
        raise ValueError("The upstream tag and selected version do not agree.")
    text = check_files()
    previous = current_version(text)
    if version_key(target) < version_key(previous):
        raise ValueError("Refusing to reduce the version in config.yaml.")
    upstream = api(f"repos/{UPSTREAM}/releases/tags/{quote(tag, safe='')}")
    if stable_version(upstream) != target:
        raise ValueError("The selected upstream release changed unexpectedly.")
    download_branding(tag)
    old_state = read_json(APP / "release.json")
    baseline = old_state.get("previous_version", previous) if old_state.get("version") == target else previous
    normalized_version(baseline)
    notes = release_notes(upstream, baseline)
    work = ROOT / ".release-work"
    work.mkdir(exist_ok=True)
    (work / "notes.md").write_text(notes, encoding="utf-8")
    (APP / "config.yaml").write_text(replace_version(text, target), encoding="utf-8")
    changelog_path = APP / "CHANGELOG.md"
    old = changelog_path.read_text(encoding="utf-8") if changelog_path.exists() else ""
    # Historical copied notes are also cleaned so the repository itself does not
    # retain actionable GitHub mentions from upstream release text.
    sanitized_old = sanitize_mentions(old)
    if sanitized_old != old:
        changelog_path.write_text(sanitized_old, encoding="utf-8")
        old = sanitized_old
    if not re.search(rf"(?m)^## {re.escape(target)}(?:\s|$)", old):
        # Keep version headings at level 2; demote upstream headings.
        details = re.sub(r"(?m)^(#{1,5})(?= )", lambda match: "##" + match.group(1), notes)
        old = re.sub(r"\A# (?:Changelog|CHANGELOG)[^\n]*\n*", "", old)
        changelog_path.write_text(f"# Changelog\n\n## {target}\n\n{details}\n{old}".rstrip() + "\n", encoding="utf-8")
    state = {"version": target, "previous_version": baseline, "upstream_tag": tag, "image": f"{IMAGE}:{target}"}
    (APP / "release.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def verify_manifest(path: Path) -> None:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    platforms = {(entry.get("platform", {}).get("os"), entry.get("platform", {}).get("architecture"))
                 for entry in manifest.get("manifests", [])}
    if not {("linux", "amd64"), ("linux", "arm64")}.issubset(platforms):
        raise ValueError(f"Final manifest does not contain both supported architectures: {platforms}")
    print("Final manifest contains linux/amd64 and linux/arm64.")


def create_release() -> None:
    target = normalized_version(os.environ["TARGET_VERSION"])
    existing = own_release(target)
    body = (ROOT / ".release-work" / "notes.md").read_text(encoding="utf-8")
    if existing:
        if existing.get("draft") or existing.get("prerelease"):
            raise ValueError(f"v{target} already exists as draft/prerelease. Review it manually; it was not overwritten.")
        # Existing releases are updated only when their generated body differs.
        # This lets a workflow update remove old @mentions without duplicating the
        # release or moving its tag.
        if str(existing.get("body") or "").strip() != body.strip():
            updated = api(f"repos/{REPO}/releases/{existing['id']}", method="PATCH", payload={
                "name": f"Kimai {target} - Home Assistant",
                "body": body,
                "draft": False,
                "prerelease": False,
                "make_latest": "true",
            })
            print(f"Updated {updated['html_url']}")
        else:
            print(f"Release v{target} already exists and is already sanitized.")
        return
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    # Refuse to silently attach a release to a different pre-existing Git tag.
    tag_ref = api(f"repos/{REPO}/git/ref/tags/v{target}", allow_404=True)
    if tag_ref is not None and (tag_ref["object"]["type"] != "commit" or tag_ref["object"]["sha"] != sha):
        raise ValueError(f"Tag v{target} already points elsewhere. Review it manually; it was not moved.")
    created = api(f"repos/{REPO}/releases", method="POST", payload={
        "tag_name": f"v{target}", "target_commitish": sha,
        "name": f"Kimai {target} - Home Assistant", "body": body,
        "draft": False, "prerelease": False, "make_latest": "true",
    })
    print(f"Published {created['html_url']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("detect", "prepare", "branding", "verify-manifest", "release"))
    parser.add_argument("file", nargs="?")
    args = parser.parse_args()
    if args.command == "detect":
        detect()
    elif args.command == "prepare":
        prepare()
    elif args.command == "branding":
        tag = api(f"repos/{UPSTREAM}/releases/latest")["tag_name"]
        normalized_version(tag)
        download_branding(tag)
    elif args.command == "verify-manifest":
        if not args.file:
            parser.error("verify-manifest requires a JSON file")
        verify_manifest(Path(args.file))
    else:
        create_release()


if __name__ == "__main__":
    try:
        main()
    except (KeyError, ValueError, RuntimeError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
