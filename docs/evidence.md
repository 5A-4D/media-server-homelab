# Evidence, provenance and limits

Prepared November 20, 2026. This is an integration case study derived from an
existing local deployment, not a claim to authorship of the upstream services.

## Evidence categories

| Category | What it supports |
| --- | --- |
| Read-only current observation | A configuration/state fact observed during publication, within the stated scope. |
| Original deployment/helper source | Authored implementation or diagnostic procedure exists; not proof every path succeeded. |
| Historical planning/SOP | Design intent and operational rules; not proof of deployment or a passed test. |
| Portfolio reference/demo | Newly generalized examples and fictional fixtures created for review; not live configuration. |

## Directly observed

- Jellyfin and the VPN gateway were running with healthy Docker health status;
  the download client was running.
- The download client's Docker network mode referenced the gateway container's
  actual ID. It had no independently published ports.
- Movies, shows and music were separate read-only Jellyfin media binds. Download
  staging was not mounted into Jellyfin, and the download client had no writable
  bind reaching the library sources.
- The data filesystem was NTFS3 with `noexec,nosuid,nodev`.
- Jellyfin ran as a configured service identity, dropped capabilities and used
  `no-new-privileges`; a selected render device and supplementary groups were
  mapped. This establishes GPU access configuration, not measured performance.
- Tailscale and the original streaming/download startup units were active and
  enabled. Effective external client reachability was not retested.
- The gateway was configured for a custom WireGuard tunnel; the profile was a
  read-only bind. The client was a small local qBittorrent image.
- Antivirus clients were installed. The standard ClamAV daemon unit was inactive
  at inspection, so no always-on scanner or current item scan is implied.
- The selected read-only audit produced 16 passes and six manual checks left
  unverified. The private original report is not included.

Observed artifact labels included Jellyfin `12.2.20261005-225228`, Gluetun
`v3.41.3` and qBittorrent package `5.2.3-1`. They describe this inspection;
they are not generic installation requirements or recommendations to freeze
these versions indefinitely.

## Original work reviewed

The source material included installation and post-install helpers, a GPU
mapping correction, private-client authorization, non-root downloader image and
Compose templates, systemd/firewall references, configuration/IPv4 repair
helpers, VPN diagnostics with recovery, a generated playback sample, and a
media-intake SOP. There were also dated audit/import artifacts.

The original media-intake collection covered magic/media probing, torrent-piece
integrity, antivirus coverage, containment checks, selected release operations
and Jellyfin indexing receipts. Those item-specific scripts and records are
not uploaded because they contain real paths, content metadata and operational
details. Their existence is not a new pass for every check today.

The original handoff began as a planning document. Proposed RustDesk, public
hosting, BIOS changes and future recovery tests are not promoted to completed
features in this repository.

## Reference changes made for publication

| Reference choice | Relationship to the observed deployment |
| --- | --- |
| Fictional paths, IDs and networks | Replaces original host/account/device values. |
| Loopback bridge publishing for Jellyfin | Conservative fresh-checkout default; original used host networking. |
| Loopback download UI | Replaces selected real private bindings. |
| `unless-stopped` in Jellyfin example | Reference change; observed original policy was `no`. |
| Dropped client capabilities and no-new-privileges | Added reference hardening, not claimed as an observed live client setting. |
| Pinned Kali base for Dockerfile | Newly resolved reference artifact; original local build used a moving base. |
| Read-only audit and synthetic fixture | New portfolio tooling derived from the operational checks. |

Compose syntax validation is not a full deployment test of these generalized
references. No new stack, GPU session, private VPN profile, firewall change,
library release, client login, network outage or power test was performed.
The restricted live downloader configuration and effective privileged firewall
rules were not opened; saved templates and Docker metadata supplied the
available evidence. No privileged changes were made.

## Publication validation

- All 16 regression tests passed in a network-isolated, read-only container.
  They exercise network isolation failures, writable/overlapping
  library mounts, staging exposure, missing observations and report privacy.
- The default fixture/report is synthetic and runs without host inspection.
- All three Compose combinations passed validation without starting containers.
- Documentation links, SVG rendering and source syntax are checked locally.
- Original reference file hashes are compared before publication.
- Publication files and new Git history are scanned for secrets and reviewed
  against privately obtained deployment identifiers before upload.

Final check results are recorded outside this repository and verified against
the uploaded commit. Scans and private-literal comparisons cannot guarantee
detection of every possible sensitive value.

## Excluded material

Actual media/subtitles/artwork, media titles, torrent metadata and tracker
details, library exports/screenshots, account identifiers, device addresses,
VPN keys/profiles, cookies, credentials, databases, logs and private receipts
remain outside the snapshot. No calendar or conversation content was accessed.

The repository remains private for owner review. The original installation and
source files stay separate, and publication adds no automatic sync or future
commit workflow.
