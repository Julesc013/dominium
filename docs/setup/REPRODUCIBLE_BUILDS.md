# Reproducible Builds (Plan S-8/S-9)

Setup Core and packaging pipelines are designed for deterministic, byte-identical outputs when given identical inputs.

## Deterministic execution

- CLI deterministic mode is **on by default** (`--deterministic 1`).
- Deterministic mode forces:
  - timestamps to `0`
  - canonical ordering in JSON outputs
  - stable plan/log/state serialization

Example:

`dominium-setup plan --manifest <artifact_root>/setup/manifests/product.dsumanifest --op install --scope portable --components core --out out.dsuplan --format json --deterministic 1`

## Packaging reproducibility

Packaging scripts accept `--reproducible` and require `SOURCE_DATE_EPOCH`:

```
set SOURCE_DATE_EPOCH=946684800
python scripts/packaging/pipeline.py assemble --build-dir build/debug --out dist/artifacts/dominium-0.1.0 --version 0.1.0 --manifest-template assets/setup/manifests/product.template.json --reproducible
python scripts/packaging/pipeline.py portable --artifact dist/artifacts/dominium-0.1.0 --out dist/portable --version 0.1.0 --reproducible
```

Wrapper scripts:

```
scripts/setup/build_packages.bat build\debug 0.1.0
scripts/setup/build_packages.sh build/debug 0.1.0
```

## Verification checklist

- Rebuild twice with the same inputs and `SOURCE_DATE_EPOCH`.
- Compare archive hashes (`sha256`) under `dist/portable/`.
- Compare `setup/SHA256SUMS` and `setup/artifact_manifest.json` inside `artifact_root/`.

## Invariants and prohibitions

- Reproducible mode must not read the current time.
- Output ordering must be deterministic (sorted paths, stable IDs).
- Any non-deterministic source (random UUIDs, hostnames) is prohibited.

## See also

- `docs/setup/PACKAGING_PIPELINES.md`
- `docs/setup/ARTIFACT_LAYOUT.md`
- `docs/setup/CLI_REFERENCE.md`
