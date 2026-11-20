# Storage, persistence and release paths

The live data mount was observed using NTFS3 with `noexec,nosuid,nodev`.
Those options apply to both staging and the library. Application configuration
and cache are persisted separately from container images.

The generalized layout is:

```text
/srv/example-media-data/            # mounted data disk
  downloads/
    incomplete/                     # never a library source
    complete/                       # candidate input, not automatically trusted
  media/
    movies/
    shows/
    music/

state/                              # ignored, suitable application-state FS
  jellyfin/config/
  jellyfin/cache/
  qbittorrent/
  gluetun/
secrets/                            # ignored, tightly restricted
  wireguard.conf
```

## Controls and their limits

| Control | Purpose | Limit |
| --- | --- | --- |
| `noexec` | Blocks ordinary direct execution from the data mount. | Does not prevent an interpreter or vulnerable media parser from consuming a file. |
| `nosuid` | Prevents set-ID bits from granting privileges there. | Does not replace service isolation or permissions. |
| `nodev` | Prevents treating device files there as devices. | Does not validate file contents. |
| Jellyfin read-only binds | Prevents that container from editing library bytes. | Other host processes may still write those bytes. |
| Separate staging | Prevents download completion from automatically publishing an item. | An explicit release still needs inspection and approval. |
| Mount-aware startup | Avoids writing into an unmounted data directory at boot. | The configured path and actual mount must still be correct. |

Use a stable disk identifier privately for persistent mounting. No UUID, disk
serial or real mount configuration is published. NTFS mount-wide ownership
options may control access differently from ext4 file ownership; verify the
effective behavior rather than assuming `chown` changes each stored file.

## Permissions

Jellyfin needs writable configuration/cache and readable libraries. The download
client needs writable configuration and staging, not a writable library parent.
An authorized host-side release process is the only intended bridge. Avoid
binding an entire disk or host root into either service.

This snapshot's audit checks bind overlap in both directions, so mounting a
library's parent into the downloader is detected even if the visible container
target has another name. It is a selected topology check, not a complete host
permission or container-escape assessment.

## Naming and conflicts

Use fictional examples when documenting structure:

```text
movies/Example Film (2026)/Example Film (2026).mkv
shows/Example Series (2026)/Season 01/Example Series S01E01.mkv
music/Example Artist/Example Album/01 - Example Track.flac
```

Resolve the exact source and destination before changing anything. Reject
symlinks or unexpected special files, inspect the entire selected item for
sidecars, check free space, and stop on a destination conflict. Do not overwrite
or recursively merge unrelated directories.

## Copy, move and hardlinks

Historical release helpers used different mechanisms, including copies, moves
and some same-filesystem hardlinks. They are not equivalent:

- A copy separates library bytes from the download client's writable copy,
  at the cost of extra space. Verify destination size/hash before removing any
  approved source.
- A move changes the source location and may interfere with ongoing seeding.
  Across filesystems it may behave as copy-then-delete; plan it explicitly.
- A hardlink shares an inode. A writable staging alias can still modify library
  content even while Jellyfin's mount is read-only. Hardlinks also require the
  same filesystem and must not be treated as a containment boundary.

The repository includes no automatic release script. Preserve current torrents
and unrelated files; select a mechanism only for the item actually authorized.
After a release, verify destination type/hash, containment flags, Jellyfin's
indexed path and playable streams. Keep any receipts private.
