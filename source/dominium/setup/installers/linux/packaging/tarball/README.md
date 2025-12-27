# Linux Tarball Packaging

This directory contains the deterministic tarball packaging helper for the
Linux installer suite.

## Output

- `Dominium-linux-<arch>-<version>.tar.gz`

The archive contains the canonical `artifact_root/` layout.

## Usage

Run from a CMake target or manually:

```
cmake -P build_tarball.cmake \
  -DARTIFACT_ROOT=/path/to/artifact_root \
  -DOUT_DIR=/path/to/dist/linux \
  -DVERSION=1.2.3 \
  -DARCH=x64 \
  -DREPO_ROOT=/path/to/repo
```

The script also performs a dry-run plan/apply validation using the bundled
`dominium-setup` CLI before writing the archive.
