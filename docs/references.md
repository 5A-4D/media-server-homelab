# Upstream references and ownership

These primary sources informed the generalized references. The local evidence
register establishes deployment facts; upstream documentation explains the
underlying products and options.

- [Jellyfin container installation](https://jellyfin.org/docs/general/installation/container/)
  — official image, persistent storage and container configuration.
- [Jellyfin Intel GPU acceleration](https://jellyfin.org/docs/general/post-install/transcoding/hardware-acceleration/intel/)
  — device access and acceleration diagnostics.
- [Gluetun container namespace sharing](https://github.com/qdm12/gluetun-wiki/blob/main/setup/connect-a-container-to-gluetun.md)
  — attaching the downloader to the gateway network stack.
- [Gluetun WireGuard options](https://github.com/qdm12/gluetun-wiki/blob/main/setup/options/wireguard.md)
  — private profile mount and tunnel configuration.
- [Gluetun port mapping](https://github.com/qdm12/gluetun-wiki/blob/main/setup/port-mapping.md)
  — distinguish management publishing from VPN-provider port forwarding; review
  the options for the actual installed gateway version.
- [Docker Compose service reference](https://docs.docker.com/reference/compose-file/services/)
  — network mode, bind mounts, capabilities and service dependencies.
- [qBittorrent upstream wiki](https://github.com/qbittorrent/qBittorrent/wiki)
  — installed-version preferences, interface binding and Web API behavior.
- [Tailscale documentation](https://tailscale.com/docs/)
  — private access and identity/device policy.
- [ClamAV scanning documentation](https://docs.clamav.net/manual/Usage/Scanning.html)
  — scanner operation, limits and interpretation.
- [FFprobe documentation](https://ffmpeg.org/ffprobe.html)
  — read-only media stream/container inspection.

The repository distributes original integration documentation, examples and
helpers, not upstream binaries or a copy of anyone's media. Upstream services,
images and tools retain their own ownership and license terms.
