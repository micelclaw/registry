# Office licences and corresponding sources

Review and correction notice: **17 November 2026**. This page distinguishes
verified provenance from outstanding distribution requirements. Public access
to a package is not a statement that every licensing obligation has been met.

## Office 0.2.3 sources

[Office 0.2.3](https://github.com/micelclaw/registry/releases/tag/2026.11.17-office-0.2.3)
contains the current four packages and their exact modified application sources.
[The immutable 0.2.3 source lock](https://github.com/micelclaw/registry/blob/da59adac5846183aef5592868e4c7e4cb2b15110/sources.lock.json)
records real source revisions, archive hashes and packaging recipes. Each package's
manifest, `SOURCE.json` and generated runtime inventory agree on the actual
registry/source/image binding. The two obsolete inventory fields described in
the historical 0.2.2 erratum below are corrected in 0.2.3.

Original licences, attribution and component notices are retained. Binary
versions and components match the already reviewed inventories; the source
availability and qualifications below still apply. This update is not a legal
compliance verdict or installed-product acceptance. Historical releases and the
n8n integration remain unchanged.

## Office 0.2.2 provenance notice

[Office 0.2.2](https://github.com/micelclaw/registry/releases/tag/2026.11.17-office-0.2.2)
provides the historical four application sources and packages.
[The immutable 0.2.2 source lock](https://github.com/micelclaw/registry/blob/5f51ee7fb93122b06195f921d2ce2560d82114f7/sources.lock.json) binds their real revisions, hashes and
public images; licensing scopes and outstanding qualifications below remain.

**Metadata erratum:** two informational fields in each package's
`runtime-notices/manifest.json` (`registry_revision` and `source_revision`)
inadvertently retain 0.2.1 values. They are obsolete and must not be used to
attribute 0.2.2 code or images. The authoritative `SOURCE.json`, package manifest,
embedded corresponding-source archive and source lock contain the correct
0.2.2 bindings. [Hash-bound corrections for all four packages](https://github.com/micelclaw/registry/releases/download/2026.11.17-office-0.2.2/ERRATA-PROVENANCE.json)
identify the obsolete and correct values explicitly. Published package bytes
remain immutable. Inventories were extracted from the actual new images;
the already reviewed binary versions and notices are unchanged. This notice
is not a compliance verdict or installed-product acceptance.

## Application sources and attribution

The [corrected 0.2.1 release](https://github.com/micelclaw/registry/releases/tag/2026.11.17-office-0.2.1)
contains the modified application sources, build/packaging files, licences and
third-party notices. Exact revisions, SHA-256 digests and sizes are recorded in
[the immutable 0.2.1 source lock](https://github.com/micelclaw/registry/blob/2b2ab73da75944eff90b632f7f50e9b6337a568e/sources.lock.json). Sources are provided without a login or
payment. The original private Git histories and Micelclaw Core/Dash are not
included. Each `.claw` also contains its corresponding application source.
The historical [0.2.0 release](https://github.com/micelclaw/registry/releases/tag/2026.11.17)
and its hashes remain unchanged; the corrections below do not overwrite it.

| Application | Licence scope | Modified source |
| --- | --- | --- |
| Documents 0.2.1 | Puter engine and its bounded adaptations: MIT. New Micelclaw wrapper/tools: BUSL-1.1. Third-party materials retain their licences. | [Download](https://github.com/micelclaw/registry/releases/download/2026.11.17-office-0.2.1/documents-0.2.1-source.tar.gz) |
| Spreadsheets 0.2.1 | AGPL-3.0-only application and Micelclaw modifications; separately licensed dependencies/assets retain their terms. | [Download](https://github.com/micelclaw/registry/releases/download/2026.11.17-office-0.2.1/spreadsheets-0.2.1-source.tar.gz) |
| Presentations 0.2.1 | AGPL-3.0-only application and Micelclaw modifications; separately licensed dependencies/assets retain their terms. | [Download](https://github.com/micelclaw/registry/releases/download/2026.11.17-office-0.2.1/presentations-0.2.1-source.tar.gz) |
| PDF 0.2.1 | AGPL-3.0-only application and Micelclaw modifications; separately licensed dependencies/assets retain their terms. See the font-source correction below. | [Download](https://github.com/micelclaw/registry/releases/download/2026.11.17-office-0.2.1/pdf-0.2.1-source.tar.gz) |

Upstream: Puter Technologies Inc.,
[HeyPuter/everything at 2c593c5be59294690baf0a69b62fa64c1fd3628f](https://github.com/HeyPuter/everything/tree/2c593c5be59294690baf0a69b62fa64c1fd3628f).
Documents' README explicitly refers to the repository's root MIT licence;
there is no separate `src/documents/LICENSE` in that revision. The retained
MIT text and Puter copyright match that root licence. The other three apps
have their own AGPL licence in their respective upstream directories.

The catalogue/tools licence in this repository does **not** relicense Puter,
the three AGPL derivatives, their modifications, fonts or other third-party
materials. Registry publication does not grant rights to the Micelclaw host.
The host authorises storage and invokes separate app services using the
documented protocol; its general-purpose APIs and iframe hosting do not import
an AGPL engine into Core. This technical separation is not a legal opinion on
every possible deployment or combined-work question.

See [dated modification notices](licenses/office-0.2.0/MODIFICATIONS.md).
Preserve original copyright and licence notices when redistributing.
Each corrected source cut includes its dated `MODIFICATIONS.md` and a direct
editor source offer. The build and image recipes retain that modification
notice; these source/build checks do not establish installed-product acceptance.

## Correction: Liberation Sans source in PDF 0.2.0

The historical PDF archive contains
`liberation-fonts-ttf-1.07.4.tar.gz`, SHA-256
`61a7e2b6742a43c73e8762cdfeaf6dfcf9abdd2cfa0b099a9854d69bc4cfee5c`.
Contrary to its accompanying README/engine review/notices, that archive
contains **TTF binaries and notices, not editable FontForge source**. Those
claims are corrected here; the published historical archive is not overwritten.

The actual upstream Liberation Fonts 1.07.4 source, as retained by Debian, is
`fonts-liberation_1.07.4.orig.tar.gz`: 2,937,949 bytes, SHA-256
`ad98b7498dc2992f7f0868f79b65ce4a720a3acdb63ab3f1f1cb6881117a5406`.
It contains 16 SFD files, Makefile, build scripts and original licences.
[Download retained editable source](https://github.com/micelclaw/registry/releases/download/2026.11.17/fonts-liberation_1.07.4.orig.tar.gz);
[upstream source archive](https://deb.debian.org/debian/pool/main/f/fonts-liberation/fonts-liberation_1.07.4.orig.tar.gz).

The four Liberation Sans TTFs are supplied by Mozilla PDF.js 6.3.289,
[revision 1c8020a7d4e43668ac287a3ecf9a8dbea17e4c56](https://github.com/mozilla/pdf.js/tree/1c8020a7d4e43668ac287a3ecf9a8dbea17e4c56/external/standard_fonts),
under GPL-2.0 with the retained font exception. Their embedding exception does
not remove obligations when distributing the fonts themselves. They differ
from the TTF-only archive. No specific PDF.js recompilation/optimisation recipe
was verified; the historical assertion that such a recipe exists is withdrawn.
Supplying the upstream SFD/build source is a correction, not proof that the
exact distributed font transformation has been fully documented.

Historical statements that the PDF application is private/unlicensed predate
the current upstream AGPL licence. They do not override that licence. An
upstream written offer is not automatically an offer made by Micelclaw.

## Runtime binaries

Each Office package contains actual binary versions, Debian copyright notices,
common licences, Node notices and an inventory bound to its image digest.
The npm inventories alone do not cover Chromium, LibreOffice or the OS.
The four 0.2.1 image inventories were extracted from their actual built images:
all 393 Debian binary-package versions per image match the retained 0.2.0
inventories. The source assets below therefore also cover those exact versions;
no new operating-system source version is inferred from an image tag. A source
archive's historical runtime inventory identifies its earlier image; the final
installable package records its own actual image digest separately.

[Exact runtime source index](licenses/office-0.2.0/runtime-source-index.json)
maps the four images' Debian binary packages to source packages/versions,
complete `.dsc` components and SHA-256 checksums. Read its verification fields:
locating a file or verifying its descriptor is distinct from verifying its
archive bytes, retaining a copy and checking anonymous public download.
Third-party links alone are not a guarantee of continued availability.
All 797 files across 250 exact Debian source versions have now been retained,
SHA-256 checked and published in these four source shards. Complete anonymous
downloads of each shard matched the recorded SHA-256 and byte length.

| Retained source shard | Size (bytes) | Download |
| --- | ---: | --- |
| office-0.2.0-debian-sources-01.tar | 1068881920 | [Download](https://github.com/micelclaw/registry/releases/download/2026.11.17/office-0.2.0-debian-sources-01.tar) |
| office-0.2.0-debian-sources-02.tar | 1068062720 | [Download](https://github.com/micelclaw/registry/releases/download/2026.11.17/office-0.2.0-debian-sources-02.tar) |
| office-0.2.0-debian-sources-03.tar | 1066332160 | [Download](https://github.com/micelclaw/registry/releases/download/2026.11.17/office-0.2.0-debian-sources-03.tar) |
| office-0.2.0-debian-sources-04.tar | 184125440 | [Download](https://github.com/micelclaw/registry/releases/download/2026.11.17/office-0.2.0-debian-sources-04.tar) |

Use the index to locate each `.dsc` and every associated component. Inside a
shard each file is at its `retained_path`; place components of one source
package together under their original filenames before using Debian source
tools. Archives contain source and build instructions; they are not executed
as part of verification. Keep the source assets available while distributing
the corresponding binaries; do not delete them as ordinary build temporaries.

Node 22.23.5 source is available from
[the official distribution](https://nodejs.org/dist/v22.23.5/), alongside its
SHA-256 list. The Node source tar.xz checksum is
`6cce7c58bf058700c643944903d60a325e8c9ceede1f5c2c088b435f2ada091a`.
[Download the retained Node source](https://github.com/micelclaw/registry/releases/download/2026.11.17/node-v22.23.5.tar.xz).
The Node and Liberation source assets also passed complete anonymous downloads
and exact SHA-256 checks. No three-year source offer or blanket compliance
conclusion is asserted here.

## Dependency review and remaining gates

Existing npm inventories cover 109 Documents, 186 Spreadsheets, 25 Presentations
and 31 PDF packages. No unknown/unlicensed declaration or missing referenced
notice file was found. This is an inventory result, not an exhaustive legal
audit. JSZip's dual licence is used under **MIT**. Asset licences, including
OFL, Apache, dictionary and PDF.js notices, remain attached to their files.

`@pdf-lib/fontkit` 1.1.1 declares MIT but its upstream standalone licence file
is absent. The preserved declaration, embedded attributions and recovered MIT
text do not independently establish notice completeness. The older `binary`,
`buffers` and `chainsaw` notices likewise record declaration-based recovery.
These require further upstream attribution verification, not relabelling as
unlicensed packages.

A complete original Joyent/string_decoder MIT comment was also recovered from
the exact `@pdf-lib/fontkit` bundle. It was absent from the inspected compiled
browser UI and browser notice file. The [verbatim recovered notice](licenses/office-0.2.0/fontkit-string-decoder-MIT.txt)
is supplied here. The corrected 0.2.1 source generator and compiled browser UI
now include that comment verbatim. It does not replace the fork-wide licence
declaration or resolve the separate attribution uncertainties above.

The distribution corrections apply to the images already public, independently
of installed-product acceptance. Runtime-source retention and public access for
the inventoried Debian, Node and Liberation archives are now verified. Remaining
work includes installed-product acceptance. The immutable 0.2.1 packages and
images are published; actual anonymous package downloads passed the official
Registry integrity, archive, provenance and safety checks. Corrected
editable-font/dated notices and direct source offers are present in those
packages, the four published source cuts and verified builds; the Micelclaw
host source-offer UI also passed compiled UI checks. These results are not
evidence that an installed editor already displays it. The font transformation
recipe and older attribution uncertainties remain as described above. Existing
0.2.0 assets remain identifiable by their original hashes during this correction.

## n8n integration

The n8n entry distributes Micelclaw integration code (BUSL-1.1) and separately
licensed MIT/Apache materials with their notices. It does not distribute or
relicense the n8n server, which retains n8n's applicable licence. No user
workflows, credentials or installation data are included.

## Applicable primary texts

- [GNU AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html): modified-work notices,
  corresponding source and the prominent network source offer.
- [GNU GPLv2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.html): source
  obligations for materials distributed under that licence.
- [GNU GPL FAQ](https://www.gnu.org/licenses/gpl-faq.html): corresponding source
  and source availability on different servers.

This is a factual engineering review and correction record. Unresolved items
above remain open; it is not a warranty or a legal compliance opinion.
