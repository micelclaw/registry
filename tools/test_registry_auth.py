"""Publication safeguards using synthetic data only; no network/native store."""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
import urllib.error
from unittest.mock import patch

import registry_auth as auth

spec = importlib.util.spec_from_file_location("configure_publisher", Path(__file__).with_name("configure-publisher.py"))
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


class ProfileTests(unittest.TestCase):
    def test_safe_profile_and_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            directory = home / ".config/micelclaw/registry-publisher"
            with patch.object(Path, "home", return_value=home), patch.object(auth, "PROFILE_DIR", directory):
                auth.profile_directories(create=True)
                (directory / "docker").mkdir(mode=0o700)
                helper = home / "synthetic-helper"
                helper.write_bytes(b"not an executable")
                digest = hashlib.sha256(helper.read_bytes()).hexdigest()
                setup.write_private(directory / "profile.json", {"configured": True, "username": "fixture", "helper_path": str(helper)})
                config = directory / "docker/config.json"
                setup.write_private(config, {"credHelpers": {"ghcr.io": "wincred.exe"}})
                with patch.object(auth, "HELPER_SHA256", digest):
                    self.assertEqual(auth.load_context("fixture")[0]["username"], "fixture")
                    setup.write_private(config, {"credHelpers": {"ghcr.io": "wincred.exe"}, "auths": {"ghcr.io": {"auth": "synthetic"}}})
                    with self.assertRaises(SystemExit):
                        auth.load_context()
                    setup.write_private(config, {"credHelpers": {"ghcr.io": "wincred.exe"}})
                    directory.chmod(0o777)
                    with self.assertRaises(SystemExit):
                        auth.load_context()
                    directory.chmod(0o700)
                    original = directory / "docker-safe"
                    (directory / "docker").rename(original)
                    (directory / "docker").symlink_to(original, target_is_directory=True)
                    with self.assertRaises(SystemExit):
                        auth.load_context()


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        (self.directory / "docker").mkdir()
        self.profile = {"configured": False, "username": "fixture", "helper_path": "synthetic-helper"}
        setup.write_private(self.directory / "profile.json", self.profile)
        setup.write_private(self.directory / "docker/config.json", {"credHelpers": {"ghcr.io": "wincred.exe"}})
        self.output = io.StringIO()
        self.output.isatty = lambda: True
        self.secret = "synthetic-test-value"
        self.response = io.StringIO('{"login":"fixture"}')
        self.response.headers = {"x-oauth-scopes": "write:packages, read:packages"}
        self.patches = [
            patch.object(setup, "PROFILE_DIR", self.directory),
            patch.object(setup, "load_context", return_value=(self.profile, ["synthetic-docker"], {})),
            patch.object(setup.sys.stdin, "isatty", return_value=True),
            patch.object(setup.sys.stderr, "isatty", return_value=True),
            patch.object(setup.getpass, "getpass", return_value=self.secret),
            patch.object(setup.urllib.request, "build_opener", return_value=SimpleNamespace(open=lambda *args, **kwargs: self.response)),
            patch.object(setup, "module_from_spec", return_value=SimpleNamespace(publisher_packages=lambda *args: set())),
            patch.object(setup, "spec_from_file_location", return_value=SimpleNamespace(loader=SimpleNamespace(exec_module=lambda module: None))),
            contextlib.redirect_stdout(self.output), contextlib.redirect_stderr(self.output),
        ]
        for mocked in self.patches:
            mocked.__enter__()
            self.addCleanup(mocked.__exit__, None, None, None)

    def run_setup(self, recover=False):
        setup.configure(SimpleNamespace(prepare=False, recover=recover))

    def tearDown(self):
        self.assertNotIn(self.secret, self.output.getvalue())

    def test_collision_after_prompt_preserves_existing(self):
        with patch.object(setup, "ghcr_targets", side_effect=[set(), {"ghcr.io"}]), patch.object(setup.subprocess, "run") as run:
            with self.assertRaisesRegex(SystemExit, "appeared"):
                self.run_setup()
            run.assert_not_called()

    def test_partial_login_failure_removes_only_own_credential(self):
        with patch.object(setup, "ghcr_targets", side_effect=[set(), set(), {"ghcr.io"}]), patch.object(setup.subprocess, "run", return_value=SimpleNamespace(returncode=1)), patch.object(setup, "publication_credential", return_value=self.secret), patch.object(setup, "helper_call", return_value=SimpleNamespace(returncode=0)) as helper:
            with self.assertRaisesRegex(SystemExit, "storage/login failed"):
                self.run_setup()
            helper.assert_called_once_with("synthetic-helper", "erase", "ghcr.io\n")
            self.assertFalse(json.loads((self.directory / "profile.json").read_text())["pending_setup"])

    def test_changed_credential_is_never_erased(self):
        with patch.object(setup, "ghcr_targets", return_value={"ghcr.io"}), patch.object(setup, "publication_credential", return_value="different-synthetic-value"), patch.object(setup, "helper_call") as helper:
            with self.assertRaisesRegex(SystemExit, "preserved"):
                setup.rollback_own_login(self.profile, self.secret)
            helper.assert_not_called()

    def test_success_stores_no_plaintext_and_no_logout(self):
        with patch.object(setup, "ghcr_targets", return_value=set()), patch.object(setup.subprocess, "run", return_value=SimpleNamespace(returncode=0)) as run:
            self.run_setup()
            self.assertEqual(run.call_count, 1)
            self.assertIn("--password-stdin", run.call_args.args[0])
            self.assertNotIn(self.secret, " ".join(run.call_args.args[0]))
            self.assertTrue(json.loads((self.directory / "profile.json").read_text())["configured"])
            self.assertNotIn(self.secret, (self.directory / "profile.json").read_text())
            self.assertEqual(json.loads((self.directory / "docker/config.json").read_text()), {"credHelpers": {"ghcr.io": "wincred.exe"}})

    def test_explicit_visible_input_uses_terminal_input_without_printing_secret(self):
        with patch.object(setup, "ghcr_targets", return_value=set()), patch.object(setup.subprocess, "run", return_value=SimpleNamespace(returncode=0)), patch("builtins.input", return_value=self.secret) as visible, patch.object(setup.getpass, "getpass") as hidden:
            setup.configure(SimpleNamespace(prepare=False, recover=False, visible=True))
            visible.assert_called_once()
            hidden.assert_not_called()
            self.assertTrue(json.loads((self.directory / "profile.json").read_text())["configured"])

    def test_expiring_token_is_not_stored(self):
        self.response.headers["github-authentication-token-expiration"] = "2030-01-01"
        with patch.object(setup, "ghcr_targets", return_value=set()), patch.object(setup.subprocess, "run") as run:
            with self.assertRaisesRegex(SystemExit, "expiration date"):
                self.run_setup()
            run.assert_not_called()

    def test_auth_failure_exposes_only_stage_and_status(self):
        unsafe = urllib.error.HTTPError("https://api.github.com/user", 401, self.secret, {}, None)
        with patch.object(setup, "ghcr_targets", return_value=set()), patch.object(setup.urllib.request, "build_opener", return_value=SimpleNamespace(open=lambda *args, **kwargs: (_ for _ in ()).throw(unsafe))), patch.object(setup.subprocess, "run") as run:
            with self.assertRaisesRegex(SystemExit, "GitHub account verification failed \\(HTTP 401\\)") as caught:
                self.run_setup()
            self.assertNotIn(self.secret, str(caught.exception))
            run.assert_not_called()

    def test_interrupted_setup_recovers_without_new_login_or_prompt(self):
        self.profile["pending_setup"] = True
        with patch.object(setup, "ghcr_targets", return_value={"ghcr.io"}), patch.object(setup, "publication_credential", return_value=self.secret), patch.object(setup.subprocess, "run") as run, patch.object(setup.getpass, "getpass") as prompt:
            self.run_setup(recover=True)
            prompt.assert_not_called()
            run.assert_not_called()
            self.assertTrue(json.loads((self.directory / "profile.json").read_text())["configured"])

    def test_interruption_before_store_clears_pending_without_read_or_login(self):
        self.profile["pending_setup"] = True
        with patch.object(setup, "ghcr_targets", return_value=set()), patch.object(setup, "publication_credential") as read, patch.object(setup.subprocess, "run") as run, patch.object(setup.getpass, "getpass") as prompt:
            self.run_setup(recover=True)
            prompt.assert_not_called()
            read.assert_not_called()
            run.assert_not_called()
            self.assertFalse(json.loads((self.directory / "profile.json").read_text())["pending_setup"])


if __name__ == "__main__":
    unittest.main()
