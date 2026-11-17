#!/usr/bin/env python3
"""One-time local setup for shared GitHub Packages publication.

--prepare installs/verifies only the official helper and a credential-free
profile. Without it, enter a classic write:packages PAT with No expiration
at the hidden LOCAL prompt. No uploads or product changes are performed.
"""
import argparse
import getpass
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request
import urllib.error
import uuid
import warnings
import fcntl
import tempfile
from registry_auth import (HELPER_SHA256, HELPER_URL, PROFILE_DIR, load_context,
                           private_path, profile_directories, publication_credential)
from importlib.util import spec_from_file_location, module_from_spec


def fail(message):
    raise SystemExit(message)


def write_private(path, value):
    if path.is_symlink():
        fail("Refusing a linked publication configuration.")
    descriptor, name = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    temp = Path(name)
    try:
        with os.fdopen(descriptor, "w") as stream:
            stream.write(json.dumps(value, indent=2) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def helper_call(helper, action, payload):
    return subprocess.run([str(helper), action], input=payload, capture_output=True, text=True)


def ghcr_targets(helper):
    listing = helper_call(helper, "list", "")
    if listing.returncode:
        fail("Could not inspect credential target metadata; nothing replaced.")
    try:
        targets = json.loads(listing.stdout)
        if not isinstance(targets, dict):
            raise ValueError()
        return {key for key in targets if "ghcr.io" in key.lower()}
    except (ValueError, TypeError):
        fail("Invalid credential target metadata; nothing replaced.")


def rollback_own_login(profile, secret):
    """Remove only this attempted login, never a changed/foreign credential."""
    targets = ghcr_targets(profile["helper_path"])
    if not targets:
        return
    if targets != {"ghcr.io"} or publication_credential(profile) != secret:
        fail("Credential changed outside setup; preserved. Use --recover to inspect setup authority safely.")
    if helper_call(profile["helper_path"], "erase", "ghcr.io\n").returncode:
        fail("Own incomplete login could not be removed. Run this setup with --recover.")


def configure(args):
    if os.geteuid() == 0:
        fail("Run as your normal user, never sudo/root.")
    if not (PROFILE_DIR / "profile.json").exists():
        ps = "/mnt/c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"
        location = subprocess.run([ps, "-NoProfile", "-NonInteractive", "-Command", "[Environment]::GetFolderPath('LocalApplicationData')"], capture_output=True, text=True)
        if location.returncode or not location.stdout.strip():
            fail("Windows profile could not be resolved.")
        local = subprocess.run(["wslpath", "-u", location.stdout.strip()], capture_output=True, text=True)
        if local.returncode:
            fail("Windows profile is unavailable from WSL.")
        helper = Path(local.stdout.strip()) / "Micelclaw" / "tools" / "docker-credential-helpers" / "0.9.13" / "docker-credential-wincred.exe"
        helper.parent.mkdir(parents=True, exist_ok=True)
        if not helper.exists():
            with urllib.request.urlopen(HELPER_URL, timeout=60) as response:
                body = response.read(5 * 1024 * 1024)
            if hashlib.sha256(body).hexdigest() != HELPER_SHA256:
                fail("Official credential helper checksum mismatch.")
            with helper.open("xb") as output:
                output.write(body)
            helper.chmod(0o755)
        if hashlib.sha256(helper.read_bytes()).hexdigest() != HELPER_SHA256:
            fail("Existing helper differs from the approved official release.")
        license_file = helper.with_name("LICENSE")
        if not license_file.exists():
            with urllib.request.urlopen("https://raw.githubusercontent.com/docker/docker-credential-helpers/v0.9.13/LICENSE", timeout=30) as response:
                licence = response.read(64 * 1024)
            if b"Permission is hereby granted" not in licence:
                fail("Could not retain the helper's original licence.")
            license_file.write_bytes(licence)
        # Own harmless fixture only; do not fetch or overwrite a real secret.
        server = "micelclaw-publisher-check-" + uuid.uuid4().hex + ".invalid"
        fixture = {"ServerURL": server, "Username": "fixture", "Secret": uuid.uuid4().hex}
        try:
            if helper_call(helper, "store", json.dumps(fixture)).returncode:
                fail("Windows credential storage is unavailable.")
            fetched = helper_call(helper, "get", server + "\n")
            if fetched.returncode or json.loads(fetched.stdout).get("Secret") != fixture["Secret"] or json.loads(fetched.stdout).get("Username") != fixture["Username"]:
                fail("Windows credential roundtrip failed.")
        finally:
            if helper_call(helper, "erase", server + "\n").returncode:
                fail("Could not remove the own credential fixture.")
        listing = helper_call(helper, "list", "")
        if listing.returncode:
            fail("Could not inspect credential target metadata.")
        targets = json.loads(listing.stdout)
        if any("ghcr.io" in key.lower() for key in targets):
            fail("An existing GHCR credential must be preserved; configure its ownership before replacing it.")
        (PROFILE_DIR / "docker").mkdir(mode=0o700, exist_ok=True)
        private_path(PROFILE_DIR / "docker", directory=True)
        write_private(PROFILE_DIR / "docker" / "config.json", {"credHelpers": {"ghcr.io": "wincred.exe"}})
        write_private(PROFILE_DIR / "profile.json", {"schema_version": 1, "username": "Titunito", "helper_path": str(helper), "helper_sha256": HELPER_SHA256, "configured": False, "credential_fixture_removed": server not in targets})
    profile, command, env = load_context("Titunito", require_configured=False)
    if args.prepare:
        print("Official Windows helper and publication-only profile verified. No publication credential changed.")
        return
    if profile.get("configured"):
        print("Publication authentication is already configured. No credential replaced.")
        return
    if profile.get("pending_setup"):
        if not args.recover:
            fail("A previous setup was interrupted. Run tools/configure-publisher.py --recover; it verifies the stored credential without replacing it.")
        targets = ghcr_targets(profile["helper_path"])
        if not targets:
            profile["pending_setup"] = False
            write_private(PROFILE_DIR / "profile.json", profile)
            print("Interrupted setup had stored no credential. State cleared; run tools/configure-publisher.py normally to configure it once.")
            return
        if targets != {"ghcr.io"}:
            fail("Unexpected existing GHCR targets preserved; recovery stopped without replacement.")
        secret = publication_credential(profile)
    else:
        if args.recover:
            fail("No interrupted setup needs recovery.")
        if ghcr_targets(profile["helper_path"]):
            fail("An existing GHCR credential must be preserved; nothing replaced.")
        if not sys.stdin.isatty() or not sys.stderr.isatty():
            fail("Use a real local terminal for the hidden credential prompt.")
        print("Create/select a GitHub CLASSIC token with write:packages and No expiration:")
        print("https://github.com/settings/tokens/new?scopes=write:packages&description=Micelclaw%20Registry%20Publisher")
        print("It will be stored encrypted in Windows Credential Manager for future sessions. No packages are uploaded here.")
        if getattr(args, "visible", False):
            print("Input is VISIBLE in this local terminal at your request. Do not share its contents.")
            secret = input("Publication credential (visible, local terminal only): ")
        else:
            warnings.simplefilter("error", getpass.GetPassWarning)
            secret = getpass.getpass("Publication credential (hidden, never paste in chat): ")
    if not secret:
        fail("No credential supplied.")
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, request, fp, code, message, headers, new_url):
            return None
    request = urllib.request.Request("https://api.github.com/user", headers={"Authorization": "Bearer " + secret, "Accept": "application/vnd.github+json"})
    attempted_login = False
    stage = "GitHub account verification"
    try:
        with urllib.request.build_opener(NoRedirect()).open(request, timeout=30) as response:
            account = json.load(response)
            scopes = {scope.strip() for scope in response.headers.get("x-oauth-scopes", "").split(",")}
            expires = response.headers.get("github-authentication-token-expiration")
        if account.get("login") != profile["username"] or "write:packages" not in scopes:
            fail("Wrong account or missing write:packages; no credential stored.")
        if expires:
            fail("This token has an expiration date. Select No expiration before configuring publication.")
        spec = spec_from_file_location("reviewed_publisher", Path(__file__).with_name("publish-images.py"))
        publisher = module_from_spec(spec)
        spec.loader.exec_module(publisher)
        stage = "GitHub organisation/package authority verification"
        publisher.publisher_packages(secret, profile["username"])
        if not args.recover:
            # Recheck after the human prompt/API verification, immediately before
            # storage. The setup lock serialises our own concurrent sessions.
            if ghcr_targets(profile["helper_path"]):
                fail("A GHCR credential appeared during setup; preserved without replacement.")
            profile["pending_setup"] = True
            write_private(PROFILE_DIR / "profile.json", profile)
            attempted_login = True
            stage = "Windows credential storage via Docker"
            login = subprocess.run(command + ["login", "ghcr.io", "--username", profile["username"], "--password-stdin"], input=secret + "\n", capture_output=True, text=True, env=env)
            if login.returncode:
                fail("Credential storage/login failed; diagnostic details are not printed.")
        # Docker may add an empty auths entry even with a native store. Persist
        # only the helper mapping; never accept a plaintext/base64 fallback.
        stored_config = json.loads((PROFILE_DIR / "docker" / "config.json").read_text())
        if (stored_config.get("credHelpers") != {"ghcr.io": "wincred.exe"}
                or any(value for value in stored_config.get("auths", {}).values())):
            write_private(PROFILE_DIR / "docker" / "config.json", {"credHelpers": {"ghcr.io": "wincred.exe"}})
            fail("Unexpected credential persistence rejected; the publication config was cleared of auth data.")
        write_private(PROFILE_DIR / "docker" / "config.json", {"credHelpers": {"ghcr.io": "wincred.exe"}})
        stage = "Publication profile finalisation"
        profile.update(configured=True, pending_setup=False, no_expiration_header=True, verified_scopes=sorted(scopes))
        write_private(PROFILE_DIR / "profile.json", profile)
    except BaseException as error:
        if attempted_login:
            rollback_own_login(profile, secret)
            profile.update(configured=False, pending_setup=False)
            write_private(PROFILE_DIR / "docker" / "config.json", {"credHelpers": {"ghcr.io": "wincred.exe"}})
            write_private(PROFILE_DIR / "profile.json", profile)
        if isinstance(error, (SystemExit, KeyboardInterrupt)):
            raise
        if isinstance(error, urllib.error.HTTPError):
            reason = "HTTP " + str(error.code)
        elif isinstance(error, FileNotFoundError):
            reason = "required local executable/file unavailable"
        elif isinstance(error, urllib.error.URLError):
            reason = "network/TLS connection failed"
        else:
            reason = type(error).__name__
        fail(stage + " failed (" + reason + "). No credential details printed. Interrupted recovery is available with --recover.")
    finally:
        del secret
    print("Publication authentication configured for all sessions of this user. No upload, Core change or runtime download credential configured.")


def main():
    if os.geteuid() == 0:
        fail("Run as your normal user, never sudo/root.")
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--prepare", action="store_true")
    mode.add_argument("--recover", action="store_true")
    parser.add_argument("--visible", action="store_true", help="Show input in your own local terminal, at your explicit request; never share its contents.")
    args = parser.parse_args()
    try:
        profile_directories(create=True)
        lock = PROFILE_DIR / "setup.lock"
        descriptor = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        with os.fdopen(descriptor, "w") as stream:
            private_path(lock)
            fcntl.flock(stream, fcntl.LOCK_EX)
            configure(args)
    except (OSError, ValueError):
        fail("Unsafe/unavailable publication profile; no secret details are printed.")


if __name__ == "__main__":
    main()
