Status: PROVISIONAL
Phase: CONVERGE-04
Machine-Readable Authority: `contracts/distribution/layout.contract.toml`

# Media Layout

Offline or burn-to-media payloads are read-only by default. Runtime, setup, and launcher flows must not assume they can write to the media root.

Writable roots must be selected, copied, or projected externally before mutation.

## Example Tree

```text
DOMINIUM_MEDIA/
  media.manifest.json
  release.manifest.json
  package.index.json
  checksums.sha256
  signatures/
  README_FIRST.txt
  LICENSES/
  packages/
    <platform>/
      <arch>/
  portable/
    <platform>/
      <arch>/
  bootstrap/
    <platform>/
  docs/
  rearchive/generated/dist/
  symbols/
  source/
  writable_template/
```

## Rules

- `media.manifest.json` describes media identity, contents, and intended projections.
- `packages/<platform>/<arch>/` contains package artifacts and indexes.
- `portable/<platform>/<arch>/` contains portable install projections if shipped.
- `bootstrap/<platform>/` contains setup/bootstrap helpers for that platform.
- `docs/`, `LICENSES/`, and `README_FIRST.txt` provide offline operator guidance.
- `rearchive/generated/dist/` contains redistributables, not Dominium-owned source.
- `symbols/` and `source/` are optional and separate from runtime payload.
- `writable_template/` may provide a copy target pattern, but it is not itself a mutable runtime root.

Media layout is a projection of logical roots. It is not a source repository layout and does not authorize root-level media folders in the source repo.
