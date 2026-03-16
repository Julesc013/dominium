Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Software Pipeline Baseline

Status: BASELINE  
Last Updated: 2026-03-07  
Scope: PROC-8 software/firmware pipeline modeling as deterministic process execution (build/test/package/sign/deploy), including compile/sign/deploy integration, quality/QC, capsule/drift hooks, proof/replay, enforcement, and TestX closure.

## 1) Pipeline Template and Runtime Path

Implemented pipeline template:

- `proc.pipeline.build_test_package_sign_deploy`

Implemented runtime process:

- `process.software_pipeline_execute`
- runtime wiring in `tools/xstack/sessionx/process_runtime.py`
- deterministic helpers in `src/process/software/pipeline_engine.py`

Step coverage:

1. input verification (source/toolchain/config/signing/deploy policy)
2. compile (`process.compile_request_submit` integration)
3. test subset execution (deterministic selection)
4. package artifact generation
5. signing artifact generation (credential-gated)
6. deployment via SIG/deployment records

## 2) Determinism Guarantees

Build identity and cache key are deterministic and content-addressed:

- cache key: `H(source_hash, toolchain_version, config_hash)`
- deterministic output hashes:
  - `binary_hash`
  - `package_hash`
  - `signature_hash`

No wall-clock dependency is used in authoritative output computation.

## 3) Compile/Sign/Deploy Integration

Compile:

- compile request rows and equivalence proof rows are recorded.
- compiled model hashes are chained (`compiled_model_hash_chain`).

Signing:

- sign step requires signing-key credential token.
- refusal path is explicit when signing key is absent/invalid.

Deploy:

- deploy emits canonical deployment records and SIG outbound rows.
- deploy fails deterministically if required records are not emitted.

## 4) Yield/Defect/QC, Capsules, and Drift

PROC-2/3 integration in pipeline execution:

- deterministic quality and defect metadata emitted per run.
- deterministic test subset/QC chain updates:
  - `software_quality_hash_chain`
  - `software_qc_hash_chain`
  - `software_test_sampling_hash_chain`

PROC-5/6 hooks:

- pipeline profile drift checks (toolchain/config/QC-failure spike).
- matching process capsules are invalidated deterministically on drift triggers.
- forced-expand event rows emitted for invalidated capsule paths.

## 5) Proof and Replay

Replay tool:

- `tools/process/tool_replay_pipeline_window.py`

Replay verification run:

- command: `python tools/process/tool_replay_pipeline_window.py --state-path build/process/proc8_report.json`
- status: `complete`
- deterministic_fingerprint: `5e5ef12e089952ab7f4b7ca6a4d9448812bda905680ceb3ee3bf27ef81886c55`
- observed chains:
  - `build_artifact_hash_chain`: `79c33900e2ed354499d08b97a85f16214dadb11ab10e4fea33d071fcf7807692`
  - `compiled_model_hash_chain`: `5c6d297505de3486ddbe8f49c427bdb21af9c70a75b523c354e856241db80ca6`
  - `signature_hash_chain`: `4a0b62715e2b60999928c79bdbe692a652c94244478783e1a896c8e3dc5f2579`
  - `deployment_hash_chain`: `3b7f18b9c6b5abfa28682c4a4820f94bb75dd96caee1e42f983f87935ee34b56`

## 6) TestX Coverage (PROC-8)

Required tests:

- `test_pipeline_deterministic_given_hashes`
- `test_compile_cache_hit`
- `test_signature_required_for_deploy`
- `test_qc_sampling_tests_subset_deterministic`
- `test_replay_pipeline_hash_match`

Command:

- `python tools/xstack/testx/runner.py --repo-root . --profile FAST --cache off --subset test_pipeline_deterministic_given_hashes,test_compile_cache_hit,test_signature_required_for_deploy,test_qc_sampling_tests_subset_deterministic,test_replay_pipeline_hash_match`
- status: `pass` (`selected_tests=5`)

## 7) Stress Harness Snapshot (Many Builds)

Deterministic stress sweep was executed through the authoritative pipeline process path and stored at:

- `build/process/proc8_stress_report.json`

Scenario and result:

- scenario: `proc8_pipeline_many_builds_160`
- status: `pass`
- deterministic_match: `true`
- suite hash: `f1bf014b51d51e480c208d701a9440be92ba5473f29c9712032c87d543e19ead`
- metrics:
  - executions: `160`
  - completed: `160`
  - refused: `0`
  - compile_cache_hits: `120`
  - signature_artifacts: `160`
  - deployment_records: `160`

## 8) Gate Status Snapshot

Topology map:

- command: `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
- status: `complete`
- deterministic_fingerprint: `50e51ed77d236cd4f68492ecd6144c846ec82e88ff7d70aa422888e76bc2b832`

RepoX STRICT:

- command: `python tools/xstack/repox/check.py --repo-root . --profile STRICT`
- status: `refusal` (`findings=38`)
- blockers include pre-existing/global findings outside PROC-8 scope (RWAM declaration gaps, provenance classification coverage, worktree hygiene, existing promoted AuditX blockers).

AuditX STRICT:

- command: `python tools/xstack/auditx/check.py --repo-root . --profile STRICT`
- status: `fail` (`promoted_blockers=6`)
- promoted blockers include pre-existing/global blockers (`E240`, `E293`) plus existing PROC path smells under current repository analyzer policy.

Strict build:

- command: `python tools/xstack/run.py strict --repo-root . --cache on`
- status: `timeout` (did not complete within local command time budget)
- strict build remains blocked by repository-wide STRICT gate state.

## 9) Contract/Invariant Summary

Relevant invariants/docs upheld for PROC-8 implementation:

- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `INV-NO-MAGIC-BUILD`
- `INV-SIGN-REQUIRES-KEY`
- `INV-DEPLOY-THROUGH-SIG`

Contract/schema impact for this completion pass:

- changed: none (phase-12 report + gate evidence + topology refresh only)
- unchanged: deterministic process-only mutation discipline, schema versions, compatibility semantics.

## 10) Readiness for PROC-9 and LOGIC-0

- [x] Deterministic software pipeline process template and runtime path
- [x] Compile/sign/deploy integrated with provenance and replay chains
- [x] Deterministic TestX subset passing for PROC-8 scope
- [x] Many-build deterministic stress sweep evidence captured
- [ ] Repository-wide STRICT gates globally green (blocked by pre-existing/global findings outside PROC-8 delta)
