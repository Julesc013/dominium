Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: REPLAY-PROOF-SLICE-01

# REPLAY-PROOF-SLICE-01 Audit

## Status

PASS_WITH_WARNINGS

## Scope

This task adds a narrow command-level replay/proof slice over:

```text
dominium.package.mount.plan.v1
```

The target was chosen because `PACKAGE-MOUNT-SLICE-01` already provides governed input/result fixtures, derived lock/report evidence, and typed refusal/diagnostic shape without needing package runtime execution.

## Added Surfaces

```text
contracts/replay/replay_input.schema.json
contracts/replay/replay_result.schema.json
contracts/replay/replay_event.schema.json
contracts/replay/replay_manifest.schema.json
contracts/replay/replay_verification_result.schema.json
contracts/proof/proof_hash.schema.json
contracts/proof/proof_manifest.schema.json
tools/validators/contracts/check_replay_proof.py
tests/contract/replay/fixtures/*
tests/app/replay_proof_slice_tests.py
```

The slice also registers replay diagnostics, replay refusals, `proof` as an artifact kind, and provisional public surfaces for replay/proof schemas, fixtures, validator, and law documentation.

## Proof Chain

```text
valid_package_mount_input.json
-> valid_replay_input_package_mount.json
-> valid_package_mount_result.json
-> valid_replay_expected_result_package_mount.json
-> valid_replay_event_log_package_mount.json
-> valid_proof_hash_package_mount.json
-> valid_proof_manifest_package_mount.json
-> valid_replay_manifest_package_mount.json
-> valid_replay_verification_result_package_mount.json
```

The proof hash uses `dominium.canonical_json.sorted_utf8.v1` with sha256 over canonical fixture material.

## Negative Coverage

Negative fixtures cover:

```text
hash mismatch
missing evidence
unknown command
noncanonical input
path-as-identity
world/runtime replay claim
fixture-only runtime support claim
expected result schema mismatch
```

## Validation

Targeted replay/proof validation passed:

```text
python -m py_compile tools/validators/contracts/check_replay_proof.py
python tools/validators/contracts/check_replay_proof.py --repo-root . --strict
python tools/validators/contracts/check_replay_proof.py --repo-root . --json
python tools/validators/contracts/check_replay_proof.py --repo-root . --fixtures
python tools/validators/contracts/check_replay_proof.py --repo-root . --inventory
py -3 tests/app/replay_proof_slice_tests.py
```

Related contract, public surface, dependency, component, portability, docs, ABI, and AIDE checks passed with known warnings only.

Fast strict was run. Early attempts failed at `t1.repox_strict` because the new replay/proof docs used incomplete status headers, then because the new architecture docs needed CANON_INDEX registration and an identity fingerprint refresh. Those metadata issues were repaired and the final fast strict run passed.

## Known Warnings

Known accepted warnings remain:

```text
full CTest remains NOT_RUN_T4_DEBT
dependency-direction strict remains PASS with 0 violations and 68 known warnings
AIDE validate keeps known review-ref warnings
stale AuditX output warning remains
replay/proof is fixture-level command proof only
package runtime is not implemented
full game/world/save replay is not implemented
broad Workbench UI, renderer, native GUI, gameplay, provider runtime, module loader, and release publication remain blocked
```

## Non-Goals Preserved

No runtime replay engine, save/load runtime, world/gameplay replay, package runtime, provider runtime, module loader, Workbench shell, renderer/native GUI, release publication, CMake target, or engine/game/runtime implementation was added.

## Next

Recommended next task:

```text
BAREBONES-CLIENT-SHELL-01
```
