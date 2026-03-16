Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# EXPORT_IMPORT_BASELINE

## Scope

LIB-6 establishes deterministic clone/export/import tooling for:

- instances
- saves
- packs

It builds on:

- LIB-0 content-addressed storage
- LIB-1 install manifests
- LIB-2 instance manifests
- LIB-3 save manifests
- LIB-5 provides resolution

## Bundle Formats

Canonical bundle kinds:

- `bundle.instance.portable`
- `bundle.instance.linked`
- `bundle.save`
- `bundle.pack`
- `bundle.modpack`

Canonical bundle layout:

```text
<bundle_root>/
  bundle.manifest.json
  content/
  hashes/
    content.sha256.json
```

Deterministic rules:

- bundle items are ordered lexicographically by `relative_path`, then `item_kind`, then `item_id_or_hash`
- `bundle_hash` is computed from the ordered item projection only
- filesystem timestamps and directory enumeration order do not affect the hash
- imports verify `bundle.manifest.json`, `hashes/content.sha256.json`, every `content_hash`, and the recomputed `bundle_hash`
- exporters refuse pre-existing output paths; importers refuse pre-existing target roots

## Export Flows

Instance export:

- validates `instance.manifest.json`
- vendors pinned lock/profile artifacts and any referenced pack artifacts
- writes a linked or portable bundle manifest deterministically
- preserves save references without embedding saves

Save export:

- validates `save.manifest.json`
- vendors save state, patches, and contract bundle payload
- vendors lock artifacts always
- vendors pack artifacts only when `--vendor-packs yes`

Pack export:

- materializes the pack into canonical CAS form
- exports the canonical store artifact for offline verification/import

## Import Flows

Instance import:

- verifies bundle structure and hashes before writing
- previews pack compatibility and provides resolution
- imports as linked or portable mode deterministically
- re-materializes bundled store artifacts into the destination store for linked imports

Save import:

- verifies bundle structure and hashes before writing
- previews bundled pack compatibility when a bundled pack set exists
- writes the save payload deterministically
- inserts bundled lock and pack artifacts into the destination store when configured

Pack import:

- verifies bundle structure and hashes before writing
- previews offline pack compatibility against the bundled payload
- inserts canonical pack artifacts into the destination store
- may also materialize the pack payload to a chosen output root

## Tooling Surfaces

Setup surfaces:

- `setup instance clone`
- `setup instance export`
- `setup instance import`
- `setup save export`
- `setup save import`
- `setup pack export`
- `setup pack import`

Verification surface:

- `tools/lib/tool_verify_bundle.py --bundle <bundle_root>`

Launcher integration:

- imported instance roots can be passed directly to `launcher start --instance <dir>`
- imported save roots or `save.manifest.json` paths can be passed through `--save` and resolve to `save_id`
- degradation and compat preview remain explicit through launcher compat reports

## Compatibility Checks

Instance import runs:

1. bundle verification
2. instance manifest validation
3. pack compat verification
4. provides resolution preview
5. destination manifest validation

Save import runs:

1. bundle verification
2. save manifest validation
3. bundled lock verification
4. bundled pack compat preview when a bundled pack set exists
5. destination manifest validation

Pack import runs:

1. bundle verification
2. bundled pack compat preview
3. CAS insertion verification

## Proof / Replay Hooks

DIAG repro capture now copies related LIB-6 `bundle.manifest.json` and `hashes/content.sha256.json` files when capture inputs are inside a bundle tree. This preserves the transport-level proof surface for later replay/audit.

## Invariants

LIB-6 enforces:

- `INV-BUNDLES-DETERMINISTIC`
- `INV-NO-TIMESTAMPS-IN-ARCHIVES`
- `INV-IMPORT-VALIDATES-HASHES`

AuditX coverage includes:

- `NondeterministicArchiveSmell`
- `ImportWithoutHashCheckSmell`

## Readiness For LIB-7

LIB-6 is ready for LIB-7 stress/regression work because:

- bundle hashing and verification are deterministic
- export/import paths are available as direct library calls and setup CLI commands
- proof/replay bundles can capture related LIB-6 bundle metadata
- dedicated LIB-6 export/import tests exist for stability, refusal, roundtrip, and cross-platform path normalization
