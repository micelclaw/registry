"""Shared publication profile. Credential values never have a CLI output.

Only the publishing program consumes the standard helper response in memory;
Docker uses that same official credential helper directly. Core's default
Docker configuration is never read, changed or copied by this module.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import stat

HELPER_VERSION = "0.9.13"
HELPER_SHA256 = "5d22527531c4234f8a0bca7f803cb4f8a0834a6a7913042f7bc6f462f0af2ac2"
HELPER_URL = "https://github.com/docker/docker-credential-helpers/releases/download/v0.9.13/docker-credential-wincred-v0.9.13.windows-amd64.exe"
PROFILE_DIR = Path.home() / ".config" / "micelclaw" / "registry-publisher"


def private_path(path, directory=False, private=True):
    """Reject replaceable profiles before using a native credential consumer."""
    info = path.lstat()
    expected = stat.S_ISDIR if directory else stat.S_ISREG
    if (not expected(info.st_mode) or info.st_uid != os.geteuid()
            or info.st_mode & (0o077 if private else 0o022)):
        raise ValueError("Unsafe publication profile path")


def profile_directories(create=False):
    # Validate every user-owned ancestor; do not chmod unrelated directories.
    private_path(Path.home(), directory=True, private=False)
    for path in [Path.home() / ".config", PROFILE_DIR.parent, PROFILE_DIR]:
        if create:
            path.mkdir(mode=0o700, exist_ok=True)
        private_path(path, directory=True, private=path == PROFILE_DIR)


def load_context(expected_login=None, require_configured=True):
    if os.geteuid() == 0:
        raise SystemExit("Use the normal publishing user, not sudo/root.")
    try:
        profile_directories()
        profile_file = PROFILE_DIR / "profile.json"
        private_path(profile_file)
        profile = json.loads(profile_file.read_text())
        helper = Path(profile["helper_path"])
        if hashlib.sha256(helper.read_bytes()).hexdigest() != HELPER_SHA256:
            raise ValueError("Helper integrity")
        if expected_login is not None and profile.get("username") != expected_login:
            raise ValueError("Publisher identity")
        config_dir = PROFILE_DIR / "docker"
        private_path(config_dir, directory=True)
        config_file = config_dir / "config.json"
        private_path(config_file)
        config = json.loads(config_file.read_text())
        if (config.get("credHelpers") != {"ghcr.io": "wincred.exe"}
                or set(config) - {"credHelpers", "auths"}
                or not isinstance(config.get("auths", {}), dict)
                or any(value for value in config.get("auths", {}).values())):
            raise ValueError("Unexpected Docker configuration")
        if require_configured and not profile.get("configured"):
            raise ValueError("Setup incomplete")
    except (OSError, ValueError, KeyError, TypeError):
        raise SystemExit("Publication authentication is not ready. Run tools/configure-publisher.py once in a local terminal.") from None
    env = os.environ.copy()
    env["PATH"] = str(helper.parent) + os.pathsep + env.get("PATH", "")
    return profile, ["docker", "--config", str(config_dir)], env


def publication_credential(profile):
    """Internal credential consumer; never print, persist or return via tools."""
    result = subprocess.run([profile["helper_path"], "get"], input="ghcr.io\n", capture_output=True, text=True)
    try:
        if result.returncode:
            raise ValueError("Credential unavailable")
        value = json.loads(result.stdout)
        if value.get("Username") != profile["username"] or not isinstance(value.get("Secret"), str) or not value["Secret"]:
            raise ValueError("Credential identity")
        return value["Secret"]
    except (ValueError, KeyError, TypeError):
        raise SystemExit("The publication credential is unavailable or belongs to another account. Reconfigure it locally.") from None
