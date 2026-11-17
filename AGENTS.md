# Registry publication

This repository owns the public catalogue, `.claw`/source release assets and
approved Micelclaw GHCR image publication. Preserve immutable versions and
exact source/checksum/image bindings. Never publish Core/Dash, private Git
history, credentials or user data through this repository.

- Publication authentication is shared across sessions of the same local user.
  It uses the official Docker wincred helper and Windows Credential Manager;
  the dedicated metadata/configuration lives under
  `~/.config/micelclaw/registry-publisher/`.
- Run `python3 tools/configure-publisher.py --prepare` to verify the helper and
  credential-free profile. A human runs `python3 tools/configure-publisher.py`
  once in a local terminal to enter a classic `write:packages` token with
  **No expiration** at its hidden prompt. Never request or paste its value in
  chat, argv, logs, environment files, repository files or reports.
- After configuration, the agent runs
  `python3 tools/publish-images.py /absolute/path/to/reviewed/images.json`.
  The publisher authenticates automatically through the shared profile. Do not
  ask the human to perform the pushes. Do not log out/erase the shared
  credential at the end, or ask for another token per session/release.
- Never run the credential helper's `get` command for inspection or display.
  Only publishing software/Docker consumes its response internally. Check
  status using profile metadata or authenticated operation results.
- Git and Releases continue using the existing authenticated GitHub CLI/keyring.
  Do not assume those scopes grant Packages access. No private download
  credential is installed in Core or users' default Docker configuration.
- A stored credential is technical capability, not approval to publish unrelated
  artefacts. Honour the current user-approved release scope and validate public
  anonymous access before advertising a package as ready.
- Do not install dependencies, change roles, restart Core, migrate databases or
  operate other services as a side effect of publication.
