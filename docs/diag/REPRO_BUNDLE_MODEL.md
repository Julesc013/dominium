Status: CANONICAL
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `docs/appshell/LOGGING_AND_TRACING.md`, `docs/appshell/SUPERVISOR_MODEL.md`, `docs/contracts/SEMANTIC_CONTRACT_MODEL.md`, and `docs/packs/PACK_VERIFICATION_PIPELINE.md`.

# Repro Bundle Model

## Purpose

DIAG-0 makes reproducibility a first-class offline artifact.

Every product may capture a deterministic repro bundle that is portable across
machines and sufficient to verify the captured replay window without network
access or repository-only runtime dependencies.

## Bundle Contents

Bundle directory ordering is deterministic and uses stable relative paths.

Required bundle surfaces:

- `manifest.json`
- `bundle_index.json`
- `descriptors/`
- `session/`
- `packs/`
- `proofs/`
- `events/`
- `logs/`
- `replay/`

Optional surfaces:

- `run/`
- `views/`

`manifest.json` contains:

- `bundle_version`
- `created_by_product_id`
- `build_id`
- `seed`
- `session_id`
- `session_template_id`
- `contract_bundle_hash`
- `semantic_contract_registry_hash`
- `pack_lock_hash`
- `overlay_manifest_hash`
- `proof_window_hash`
- `canonical_event_hash`
- `log_window_hash`
- `included_artifacts`
- `bundle_hash`

## Privacy

Bundles must exclude:

- account secrets
- auth tokens
- signing keys
- machine identifiers beyond coarse host meta

Bundles may include coarse host meta only:

- OS family
- OS version
- CPU architecture

These fields are host-meta only and must never influence replay or truth.

## Deterministic Hashing

Bundle hashing is defined as:

1. collect deterministic file rows for every captured artifact except
   `manifest.json` and `bundle_index.json`
2. sort by relative path
3. hash canonical JSON of:
   - `rel_path`
   - `content_hash`
   - `size_bytes`
4. store the result as `bundle_hash`

`bundle_index.json` records the sorted file rows and the same `bundle_hash`.

## Replay

`tool_replay_bundle` verifies:

- bundle file ordering and content hashes
- bundle hash equivalence
- proof-anchor window hash equivalence
- canonical event-window hash equivalence
- structured log-window hash equivalence
- negotiation records if present

If the bundle is valid but the runtime does not support mutation-compatible
loading, the bundle may still be inspected in read-only mode. No silent
reinterpretation is allowed.

## Integration

- AppShell `diag capture` is the canonical user-facing capture command.
- Supervisor crash handling may auto-capture a repro bundle by policy.
- Server and client may expose capture over IPC console.
- Bundles are offline-only and portable.
