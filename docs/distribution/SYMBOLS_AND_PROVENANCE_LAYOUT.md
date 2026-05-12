Status: PROVISIONAL
Phase: CONVERGE-04
Machine-Readable Authority: `contracts/distribution/layout.contract.toml`

# Symbols And Provenance Layout

Symbols and build provenance are separate from runtime payload packages.

## Distribution Output Roles

```text
dist/
  sym/<platform>/<arch>/
  meta/
```

- `dist/sym/<platform>/<arch>/` contains symbols, debug packages, symbol indexes, and source-link metadata.
- `dist/meta/` contains release manifests, package indexes, build metadata, checksums, signatures, provenance records, and verification reports.

Symbols are never merged into runtime payload packages unless an explicit symbols package class is being produced.

## Provenance Rules

- Release identity is manifest-driven.
- Checksums and signatures are explicit artifacts.
- Signing is additive and must not change content hashes.
- Build provenance must not depend on host paths, wall-clock timestamps, usernames, hostnames, or filesystem traversal order.
- Source archives may exist separately when release policy allows them.

## Debug Packages

Debug packages may be emitted as separate `.dompkg` artifacts or side-channel archives. They export into `SYMBOL_ROOT` or an explicit symbols projection, not into normal runtime roots.

## Relationship To Release Manifests

Release manifests enumerate shipped artifacts. They describe runtime payloads, symbols, metadata, signatures, and source archives as separate artifacts so verification can decide exactly what is present.
