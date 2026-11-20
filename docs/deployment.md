# Deployment reference

These examples document a rebuild path. Publication validation runs `config`
and offline tests only; it does not launch or replace the installed stack.

## Configuration inventory

| File | Purpose |
| --- | --- |
| `examples/.env.example` | Fictional IDs, paths, loopback addresses and GPU defaults. |
| `examples/compose.jellyfin.yaml` | Persistent Jellyfin configuration/cache, read-only media and loopback playback. |
| `examples/compose.jellyfin-gpu.yaml` | Optional selected render device and supplemental group. |
| `examples/compose.downloads.yaml` | Gluetun gateway plus qBittorrent sharing its network namespace. |
| `examples/qbittorrent/Dockerfile` | Small non-root downloader image derived from the original deployment. |
| `examples/qbittorrent/preferences.example.json` | Settings to review through the application's own UI/API. |
| `examples/firewall/media-access.nft` | Separate host-input and Docker-forward management boundaries. |
| `examples/systemd/` | Mount-aware service startup using example installation paths. |

The observed Jellyfin and Gluetun artifacts are pinned by digest in the
examples. These identify the publication baseline; they are not a promise that
the images remain current or vulnerability-free. The downloader reference pins
a newly resolved official Kali base, but its APT packages still come from a
rolling archive. It is not a bit-for-bit reproduction of the running image.

## Prepare the destination

1. Inventory disks, mount persistence, ownership, Docker, private access and
   effective firewall rules. Keep an independent recovery path.
2. Choose dedicated service UIDs/GIDs and a shared data-access group. The
   numeric examples are not the original installation's identities.
3. Mount a data disk with `noexec,nosuid,nodev`. Create complete/incomplete and
   library directories separately. Confirm the real mounted filesystem before
   enabling services; a directory existing on the root disk is insufficient.
4. Create private configuration/cache directories owned by the selected
   services. Do not recursively change ownership of an existing library.
5. Copy `examples/.env.example` to an ignored local `.env` and set real paths and
   IDs there. Relative paths in Compose are based on the Compose project directory
   (`examples/` in the supplied validation commands).
6. Put a private WireGuard profile in the ignored secret location with restrictive
   permissions. The repository intentionally includes no sample private key.

Missing bind paths fail rather than being silently created. State should live
on a filesystem suitable for application databases; the data disk can have a
different filesystem and permission model.

## Bring up streaming in a reviewed environment

Validate Compose first. Choose whether clients will use an SSH forwarding path
to the loopback port or a selected private host address with access controls.
The examples do not open the service to the whole LAN automatically.

The original Jellyfin configuration used host networking. The reference uses
loopback bridge publishing to keep a fresh checkout local by default; discovery
and direct private-client access may require deliberate network changes.
If switching to host networking, remove conflicting port publishing and review
the input firewall as well as existing Docker/Tailscale rules.

Finish Jellyfin's setup privately: use separate administration/playback roles,
disable automatic router mapping, add libraries by container path and verify a
synthetic test item. Do not copy a running database while it is being written.

## Add GPU access separately

Identify the Intel render node from host hardware and inspect its numeric group.
Do not assume the first render node is the intended GPU. Add the GPU override,
set `RENDER_DEVICE` and `RENDER_GID`, then configure Jellyfin's acceleration mode
for that device. The device is mapped at the same path inside the container.

Check device accessibility as the container user, then run the supplied Jellyfin
`vainfo` diagnostic against the selected node. Finally exercise an actual
transcoding session with generated media. A device mapping alone does not prove
that playback uses hardware acceleration.

## Add the download stack

Review the WireGuard profile and Gluetun options locally. Keep the gateway
firewall enabled and the private profile mount read-only. The gateway needs the
TUN device and network administration capability; neither is granted to the
download client.

The client waits for gateway health and shares its namespace. Configure the
actual tunnel interface in qBittorrent, disable UPnP/NAT-PMP and Web UI auth
bypasses, and set distinct complete/incomplete paths. Review preferences in the
installed version's UI/API rather than copying an entire private configuration.
Do not export credentials or session cookies while doing so.

`FIREWALL_INPUT_PORTS=8080` permits the management listener inside the gateway's
local-network boundary. It is distinct from VPN-provider inbound peer-port
forwarding; no provider forwarding is configured here.

## Enable startup last

The systemd examples use `/opt/media-homelab` and `/srv/example-media-data`.
Set the ignored `.env` paths to match that reviewed installation. If GPU access
is required, add its override to both the start and stop commands. These units
do not install or load the firewall reference; establish the effective access
policy before any private-interface binding is enabled.

Check the mount, validate configurations, establish access controls, and only
then enable the service units. A `oneshot` unit with `RemainAfterExit` records
that Compose ran; inspect container health separately. Reboot and power-loss
tests belong to a scheduled maintenance window, not an offline portfolio check.
