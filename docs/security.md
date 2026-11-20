# Security boundaries and validation

## Threat model

The design separates an untrusted download staging area, a playback service,
private management endpoints and host-owned storage. Main concerns are hostile
sidecars/media, unintended library writes, VPN bypass, management exposure,
credential disclosure and incomplete verification presented as a clean result.

Containers share the host kernel and are not virtual machines. A read-only
library bind, a commercial VPN and a clean scan each solve only part of that
problem. The operator still needs maintained software and a reviewed host.

## Access paths and firewall placement

Keep playback accounts separate from administration. Do not forward management
ports through the router or enable automatic port mapping. Tailscale access
should be limited to approved devices/users with appropriate account controls;
do not allow the whole carrier-grade NAT range as if it were a trusted client.

Host-networked Jellyfin traffic is evaluated on the host input path. Docker
published bridge traffic can traverse forwarding/NAT instead. The reference
rules show both cases and scope forwarded drops to named example bridges.
Rules in another table/chain may still deny traffic after an earlier accept;
an example accept is not proof of final reachability.

The template is not a full firewall policy and is never automatically applied.
Review existing Docker, Tailscale, IPv4 and IPv6 rules and test both approved
and rejected clients. Loopback publishing is the default for a fresh example;
changing a bind address is an exposure change that requires that review.

## VPN checks are separate questions

| Question | Evidence needed |
| --- | --- |
| Is the client in the gateway namespace? | Docker network-mode relationship, not similar container names. |
| Is the application bound to the tunnel? | Installed-version interface settings and actual transfer behavior. |
| Is egress using the intended provider? | Private comparison of host and client egress plus provider confirmation. |
| Is DNS following the intended path? | Resolver/configuration inspection and appropriate packet-level evidence. |
| Is IPv6 handled safely? | Effective routes/firewall behavior and explicit IPv6 tests. |
| Does failure block bypass? | Controlled outage while a test transfer/connection remains meaningful, then recovery. |
| What address do peers observe? | An authorized torrent-observed test; HTTP egress alone does not answer this. |

Do not print public IPs, resolver payloads or VPN account information in shared
reports. A different HTTP address and a green healthcheck do not establish all
of these properties. Killing the whole client makes a bypass test meaningless;
tests must leave the relevant process/path observable.

DNS-over-TLS is a resolver transport choice within the intended path. It is not
a substitute for the WireGuard tunnel, application binding or firewall checks.

## Media and service containment

Keep storage `noexec,nosuid,nodev`; mount libraries read-only in Jellyfin; do not
mount staging there. Limit host mounts and service privileges. Grant the render
device only to the playback service, and network administration only to the VPN
gateway that needs it. Keep media parsers and scanner definitions maintained.

The reference downloader adds dropped capabilities and `no-new-privileges`;
those are deliberate example hardening beyond the observed client's Docker
settings. They have configuration validation here, not a fresh production soak
test. Do not silently describe reference improvements as deployed facts.

Follow the [intake gate](media-intake.md). No public report should call a file
guaranteed safe, equate a signature match with source trust, or label skipped
scanner content as a complete clean scan.

## Secrets and privacy

The repository excludes VPN profiles/keys, login state, session cookies,
application databases, torrent state, actual media, library artwork, account
identifiers, device addresses and original logs. It does not inspect or export
calendar data or private conversations.

The audit selects fixed control results from in-memory observations and discards
raw Docker data. Its report intentionally does not contain image labels,
environment values, container names, bind paths or local exception details.
Installed scanner software is reported separately from any particular scan.

Backups inherit the sensitivity of live state. Keep them encrypted/restricted
off-repository, and rotate exposed credentials rather than merely deleting
their latest source-file occurrence. A file/history secret scan supplements
manual review; it cannot find every sensitive value.

## Incident handling

If content is suspicious, leave it outside the library and do not open or
execute it. Preserve private evidence and unrelated files. If management
exposure or VPN bypass is suspected, contain the affected path with a documented
recovery method, then inspect the effective controls before resuming transfers.
Changes to networking, active sessions or running services require separate
operational planning; this publication performs none of them.
