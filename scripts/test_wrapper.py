"""Local sandbox checks of run.sh, with no Docker/SQL/host system writes.

An isolated copy maps all writable absolute paths into a temporary directory.
The upstream entrypoint and chown are replaced with safe test doubles.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('php') and shutil.which('jq'), 'Requires PHP CLI and jq for sandbox-only tests')
class WrapperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for folder in ('data', 'opt/kimai/var/data', 'opt/kimai/var/plugins',
                       'etc', 'usr/local/etc/php/conf.d', 'bin'):
            (self.root / folder).mkdir(parents=True, exist_ok=True)
        self.options = {
            'database_host': 'core-mariadb', 'database_port': 3306,
            'database_name': 'kimai', 'database_user': 'kimai',
            'database_password': 'UnitTest-Db:@#%!', 'database_version': 'auto',
            'admin_email': 'test@example.invalid',
            'admin_password': 'UnitTest-Admin-Only!', 'app_secret': 'a' * 64,
            'trusted_hosts': r'^(homeassistant\.local|localhost|127\.0\.0\.1)$',
            'timezone': 'Europe/Madrid',
        }
        writable = (
            '/data/options.json', '/data/kimai-data', '/data/kimai-plugins',
            '/opt/kimai/var/data', '/opt/kimai/var/plugins',
            '/etc/localtime', '/etc/timezone',
            '/usr/local/etc/php/conf.d/99-home-assistant-timezone.ini',
            '/entrypoint.sh',
        )
        pattern = re.compile('|'.join(re.escape(p) for p in sorted(writable, key=len, reverse=True)))
        text = (ROOT / 'kimai/run.sh').read_text()
        text = pattern.sub(lambda m: str(self.root / m.group(0).lstrip('/')), text)
        (self.root / 'run.sh').write_text(text)
        entrypoint = self.root / 'entrypoint.sh'
        entrypoint.write_text('''#!/usr/bin/env bash
php -r '$out=[]; foreach (["DATABASE_URL","APP_SECRET","TRUSTED_HOSTS","TIMEZONE","TZ"] as $k) { $out[$k]=getenv($k); } file_put_contents(getenv("TEST_CAPTURE"), json_encode($out));'
''')
        entrypoint.chmod(0o755)
        fake = self.root / 'bin/chown'
        fake.write_text('#!/usr/bin/env bash\nexit 0\n')
        fake.chmod(0o755)
        self.env = os.environ.copy()
        self.env['PATH'] = str(self.root / 'bin') + os.pathsep + self.env['PATH']
        self.env['TEST_CAPTURE'] = str(self.root / 'capture.json')

    def tearDown(self):
        self.tmp.cleanup()

    def run_wrapper(self):
        (self.root / 'data/options.json').write_text(json.dumps(self.options))
        return subprocess.run(['bash', str(self.root / 'run.sh')], capture_output=True,
                              text=True, env=self.env, timeout=15)

    def capture(self):
        return json.loads((self.root / 'capture.json').read_text())

    def test_auto_version_and_url_encoding(self):
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        url = self.capture()['DATABASE_URL']
        self.assertNotIn('serverVersion', url)
        self.assertIn(quote(self.options['database_password'], safe=''), url)
        self.assertIn('@core-mariadb:3306/kimai?charset=utf8mb4', url)

    def test_explicit_version_backwards_compatibility(self):
        self.options['database_version'] = '11.4.10-MariaDB'
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.capture()['DATABASE_URL'].endswith('&serverVersion=11.4.10-MariaDB'))

    def test_placeholder_password_is_rejected(self):
        self.options['database_password'] = 'CHANGE_ME_DB'
        result = self.run_wrapper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('database_password', result.stderr)
        self.assertFalse((self.root / 'capture.json').exists())

    def test_madrid_applied_to_os_and_php(self):
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.capture()['TZ'], 'Europe/Madrid')
        self.assertEqual(self.capture()['TIMEZONE'], 'Europe/Madrid')
        self.assertEqual((self.root / 'etc/timezone').read_text().strip(), 'Europe/Madrid')
        self.assertIn('Europe/Madrid', (self.root / 'usr/local/etc/php/conf.d/99-home-assistant-timezone.ini').read_text())

    def test_no_secret_printed_by_wrapper(self):
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        output = result.stdout + result.stderr
        for field in ('database_password', 'admin_password', 'app_secret'):
            self.assertNotIn(self.options[field], output)

    def test_persisted_files_survive_simulated_recreation(self):
        source = self.root / 'opt/kimai/var/data'
        (source / 'seed.txt').write_text('original')
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        target = self.root / 'data/kimai-data'
        (target / 'user-file.txt').write_text('keep-me')
        self.assertEqual((target / 'seed.txt').read_text(), 'original')
        source.unlink()
        source.mkdir()
        (source / 'seed.txt').write_text('do-not-overwrite-user-data')
        result = self.run_wrapper()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((target / 'seed.txt').read_text(), 'original')
        self.assertEqual((source / 'user-file.txt').read_text(), 'keep-me')
        self.assertTrue(source.is_symlink())

    def test_invalid_timezone_rejected(self):
        self.options['timezone'] = '../etc/passwd'
        result = self.run_wrapper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Zona horaria', result.stderr)

    def test_protocol_in_host_regex_is_rejected(self):
        self.options['trusted_hosts'] = 'http://homeassistant.local:8001'
        result = self.run_wrapper()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('trusted_hosts', result.stderr)


if __name__ == '__main__':
    unittest.main()
