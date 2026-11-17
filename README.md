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
redistributing Office. The initial Office release is still under correction and
has not completed installed-product acceptance. The current discoverable
entry is n8n. The four Office release assets remain public, with their
licence correction notice, while corrected immutable packages are prepared;
they will enter the catalogue after that correction.

## Installing

In MicelHub → Registry, search, add the package to the local registry, then use
Install. The existing installation authority and app permissions still apply.
Local packages remain accessible if the public catalogue is unavailable.

## Adding a package

Keep one catalogue entry per application. Publish an immutable versioned
release asset and its source archive; record their exact hashes and sizes.
Use HTTPS assets under `micelclaw/registry/releases/download/`. Never include
credentials, runtime databases, user documents or private Git history.

Publication is performed by an authorised maintainer. `tools/publish-images.py`
uses a temporary Docker configuration for publishing; installations download
public images anonymously and do not need registry credentials.

## Corrected Office cuts

Pass an optional `REVIEWED_CUTS_JSON` to `tools/prepare-sources.mjs` after
`WORKSPACE OUTPUT RELEASE_TAG`. It maps the four Office app names to their
actual reviewed commits. Each commit must contain a new application version;
an existing version is rejected rather than replaced. The already published
n8n source entry is retained. The image recipe derives tags from the locked
version and still requires matching reviewed source/build proofs. This does
not authorise a build, publish, installation or restart by itself.
