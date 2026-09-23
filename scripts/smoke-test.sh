#!/usr/bin/env bash
# Runs ONLY on a disposable GitHub runner, never against your Home Assistant.
set -Eeuo pipefail
IMAGE="${1:?Usage: smoke-test.sh IMAGE}"
WORK="$(mktemp -d)"
SUFFIX="${GITHUB_RUN_ID:-local}-${RANDOM}"
NETWORK="kimai-ci-${SUFFIX}"
DB="kimai-db-${SUFFIX}"
APP="kimai-app-${SUFFIX}"

cleanup() {
  status=$?
  trap - EXIT
  if [ "$status" -ne 0 ]; then
    echo "::group::Kimai test log"
    docker logs --tail 120 "$APP" 2>&1 || true
    echo "::endgroup::"
    echo "::group::MariaDB test log"
    docker logs --tail 60 "$DB" 2>&1 || true
    echo "::endgroup::"
  fi
  docker rm -fv "$APP" "$DB" >/dev/null 2>&1 || true
  docker network rm "$NETWORK" >/dev/null 2>&1 || true
  # WORK is created by mktemp above, not taken from app configuration.
  sudo rm -rf -- "$WORK"
  exit "$status"
}
trap cleanup EXIT

DB_PASSWORD="$(openssl rand -hex 24)"
ROOT_PASSWORD="$(openssl rand -hex 24)"
ADMIN_PASSWORD="$(openssl rand -hex 24)"
APP_SECRET="$(openssl rand -hex 32)"
for secret in "$DB_PASSWORD" "$ROOT_PASSWORD" "$ADMIN_PASSWORD" "$APP_SECRET"; do
  echo "::add-mask::$secret"
done
export DB_PASSWORD ADMIN_PASSWORD APP_SECRET

mkdir -p "$WORK/data"
chmod 755 "$WORK" "$WORK/data"
python3 - "$WORK/data/options.json" <<'PY'
import json, os, pathlib, sys
options = {
    "database_host": "core-mariadb", "database_port": 3306,
    "database_name": "kimai", "database_user": "kimai",
    "database_password": os.environ["DB_PASSWORD"],
    "database_version": "auto",
    "admin_email": "ci@example.invalid",
    "admin_password": os.environ["ADMIN_PASSWORD"],
    "app_secret": os.environ["APP_SECRET"],
    "trusted_hosts": r"localhost|127\.0\.0\.1",
    "timezone": "Europe/Madrid",
}
pathlib.Path(sys.argv[1]).write_text(json.dumps(options), encoding="utf-8")
PY
chmod 644 "$WORK/data/options.json"

docker pull "$IMAGE"
docker network create "$NETWORK" >/dev/null
docker run -d --name "$DB" --network "$NETWORK" --network-alias core-mariadb \
  -e MARIADB_DATABASE=kimai -e MARIADB_USER=kimai \
  -e "MARIADB_PASSWORD=$DB_PASSWORD" -e "MARIADB_ROOT_PASSWORD=$ROOT_PASSWORD" \
  mariadb:11.4 >/dev/null

sql() {
  docker exec -e "MYSQL_PWD=$DB_PASSWORD" "$DB" \
    mariadb --user=kimai --database=kimai --batch --skip-column-names --execute "$1"
}

ready=false
for attempt in $(seq 1 60); do
  if sql 'SELECT 1;' >/dev/null 2>&1; then
    ready=true
    break
  fi
  sleep 3
done
if [ "$ready" != true ]; then
  echo "::error::Temporary MariaDB did not become ready."
  exit 1
fi
# database_version stays "auto": test real Doctrine detection, not a fixed version.

start_app() {
  docker run -d --name "$APP" --network "$NETWORK" \
    --publish 127.0.0.1:18001:8001 \
    --volume "$WORK/data:/data" "$IMAGE" >/dev/null
}

wait_for_login() {
  for attempt in $(seq 1 120); do
    if [ "$(docker inspect --format '{{.State.Running}}' "$APP")" != true ]; then
      echo "::error::Kimai exited during startup."
      return 1
    fi
    status="$(curl -sS -L --max-time 10 -o "$WORK/login.html" \
      -w '%{http_code}' http://127.0.0.1:18001/en/login 2>/dev/null || true)"
    if [ "$status" = 200 ] && grep -qi 'password' "$WORK/login.html"; then
      return 0
    fi
    sleep 5
  done
  echo "::error::The Kimai login page did not become available."
  return 1
}

start_app
wait_for_login
users_before="$(sql "SELECT COUNT(*) FROM kimai2_users WHERE email='ci@example.invalid';")"
if [ "$users_before" != 1 ]; then
  echo "::error::The test administrator was not found in MariaDB."
  exit 1
fi

# Write unique probes that the automatic admin bootstrap cannot recreate.
PROBE="$(openssl rand -hex 12)"
sql "CREATE TABLE ci_ha_persistence_probe (value VARCHAR(64) NOT NULL);" >/dev/null
sql "INSERT INTO ci_ha_persistence_probe VALUES ('$PROBE');" >/dev/null
docker exec "$APP" sh -c 'printf "%s" "$1" > /opt/kimai/var/data/ci-ha-persistence.txt' sh "$PROBE"

# Recreate the app container, retaining /data and the separate MariaDB container.
docker stop --time 30 "$APP" >/dev/null
docker rm "$APP" >/dev/null
start_app
wait_for_login
users_after="$(sql "SELECT COUNT(*) FROM kimai2_users WHERE email='ci@example.invalid';")"
if [ "$users_after" != "$users_before" ]; then
  echo "::error::The administrator did not persist across container recreation."
  exit 1
fi

if [ "$(sql 'SELECT value FROM ci_ha_persistence_probe;')" != "$PROBE" ]; then
  echo "::error::The database persistence probe did not survive."
  exit 1
fi
if [ "$(docker exec "$APP" cat /opt/kimai/var/data/ci-ha-persistence.txt)" != "$PROBE" ]; then
  echo "::error::The /data persistence probe did not survive."
  exit 1
fi

echo "PASS: login page, MariaDB administrator, database and /data persistence."
