# Updated reference derived from the original small, non-root Kali image.
# The base is pinned; APT package selection still depends on the rolling archive.
FROM kalilinux/kali-rolling@sha256:1ff4a2be3849333687b3ed2b31bb5af0cd1b7c0a11ec7713feb5abe5a6b2795c
ARG DOWNLOAD_UID=10002
ARG DOWNLOAD_GID=10002
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y \
        ca-certificates curl qbittorrent-nox tini \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid "$DOWNLOAD_GID" downloader \
    && useradd --uid "$DOWNLOAD_UID" --gid "$DOWNLOAD_GID" \
        --home-dir /config --shell /usr/sbin/nologin downloader
USER ${DOWNLOAD_UID}:${DOWNLOAD_GID}
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["/usr/bin/qbittorrent-nox", "--profile=/config", "--webui-port=8080", "--confirm-legal-notice"]
