# Micelclaw Registry

Public catalogue of installable Micelclaw integrations. The catalogue format is
versioned by `schema_version`; each entry identifies one exact `.claw` release
asset by SHA-256 and byte length. Downloading a package does not install it.

Container layers live in GHCR. Packages, corresponding sources and notices live
in GitHub Releases. `sources.lock.json` binds the source archives and packaging
recipe to an actual commit in this repository. A source revision recorded as
provenance does not import the original repository or its history.

Each application retains its own licence and third-party notices. Making this
catalogue public does not relicense its applications or the software they use.
The n8n entry distributes the Micelclaw integration, not the n8n server, user
workflows, credentials or data. Its native services are provided by Micelclaw
Core; no n8n templates are included in this package.

See [licences, modified sources and correction status](LICENSING.md) before
redistributing Office. The catalogue contains **Documents, Spreadsheets,
Presentations and PDF 0.2.1**, plus the existing **n8n integration 0.1.1**.
The four corrected Office packages, exact sources and public GHCR images are
published; actual anonymous package downloads passed the official Registry
integrity, archive, provenance and safety checks. Their older 0.2.0 assets
remain unchanged. Installed-product acceptance is still pending; publication
does not establish that a particular host has installed or activated an app.

## Installing

The redesigned MicelHub separates **Registry → Download**, **Available → Install**
and **Installed → Uninstall**. Hosts need the corresponding Core and Dash changes
loaded to use that flow; downloading does not activate an application. Older
hosts retain their existing local-registry installation flow. The existing
installation authority and app permissions still apply. Local packages remain
accessible if the public catalogue is unavailable.

`catalog-display.json` is an optional companion for application icons, publisher,
plan and editorial badges, keyed by the exact package name and version. Older
hosts keep reading the unchanged `catalog.json`; companion errors must not block
downloads. It does not replace package integrity or safety checks. To refresh it
from the exact reviewed application manifests, run
`node tools/update-catalog-display.mjs CORE_DIRECTORY` (`--check` validates without
writing). Never repack an immutable release merely to change presentation metadata.

## Adding a package

Keep one catalogue entry per application. Publish an immutable versioned
release asset and its source archive; record their exact hashes and sizes.
Use HTTPS assets under `micelclaw/registry/releases/download/`. Never include
credentials, runtime databases, user documents or private Git history.

Publication is performed by the authorised agent/maintainer using a shared
local publishing profile. Git and Releases use the existing GitHub CLI keyring.
For GHCR, run `python3 tools/configure-publisher.py` once in a local WSL terminal
as the normal Windows/WSL user. Enter a classic GitHub token with
`write:packages` and **No expiration** only at its hidden prompt. The official
Docker wincred helper stores it encrypted in Windows Credential Manager;
`~/.config/micelclaw/registry-publisher/` contains only private configuration
and status metadata. No token is saved in this repository or Core.
At the local user's explicit request, `configure-publisher.py --visible` allows
normal input echo in their own terminal. Do not record or share that terminal's
contents. Hidden input remains the default.

All subsequent local agent sessions run `tools/publish-images.py` directly,
without asking the human to upload images or enter the credential again.
The current publisher validates the four reviewed Office images; new image
families require an explicitly reviewed publication recipe. Package/source
release uploads continue through the authenticated GitHub CLI. A stored
credential does not authorise unrelated publications. See [AGENTS.md](AGENTS.md)
for the shared procedure. After an interrupted first login, `configure-publisher.py
--recover` validates the stored account, scopes and authority before completing
the profile, without replacing the credential.

No expiration removes scheduled expiry; GitHub can still revoke a token,
including after a year without use. Installations download public images
anonymously and do not need registry credentials. The helper is the original
Docker `docker-credential-helpers` v0.9.13 Windows AMD64 release, pinned by SHA-256
in `tools/registry_auth.py`; its original MIT licence is retained beside the
installed binary. It is not included in application packages or images.

## Corrected Office cuts

Pass an optional `REVIEWED_CUTS_JSON` to `tools/prepare-sources.mjs` after
`WORKSPACE OUTPUT RELEASE_TAG`. It maps the four Office app names to their
actual reviewed commits. Each commit must contain a new application version;
an existing version is rejected rather than replaced. The already published
n8n source entry is retained. The image recipe derives tags from the locked
version and still requires matching reviewed source/build proofs. This does
not authorise a build, publish, installation or restart by itself.

`tools/package-office.mjs CORE_DIRECTORY APP BINDING_JSON [REVIEWED_BUILD_PROOF_JSON]`
accepts an explicit reviewed build proof so a new immutable release cannot
accidentally consume an earlier release's proof. The official helper still
validates that proof, the public source lock and the actual image inventory
before packaging.
