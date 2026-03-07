Status: BASELINE
Last Reviewed: 2026-03-06
Version: 1.0.0
Scope: COMPILE-0 CompiledModel equivalence framework

# Compiled Model Baseline

## Summary
COMPILE-0 establishes a universal, deterministic compiled-model framework for reusable compilation across SYS/PROC/LOGIC-adjacent workloads without changing authoritative semantics.

Delivered capabilities:
- canonical compile request submission (`process.compile_request_submit`) through runtime process discipline,
- derived compiled artifacts with deterministic fingerprints and hash chains,
- required equivalence proof linkage for successful compiled models,
- validity-domain checks with refusal fallback to uncompiled execution contracts,
- replay/recompile verification tooling for hash stability.

## Schema and Registry Summary

New schemas:
- `schema/meta/compiled_model.schema`
- `schema/meta/equivalence_proof.schema`
- `schema/meta/validity_domain.schema`
- `schema/meta/compile_request.schema`
- `schema/meta/compile_result.schema`

Registered artifacts and policies:
- `data/registries/compiled_type_registry.json`
  - `compiled.automaton`
  - `compiled.lookup_table`
  - `compiled.reduced_graph`
  - `compiled.ir`
- `data/registries/verification_procedure_registry.json`
  - `verify.exact_structural`
  - `verify.bounded_sampling`
  - `verify.symbolic_stub`
- `data/registries/compile_policy_registry.json`
  - `compile.default`
  - `compile.rank_strict`
  - `compile.lab_aggressive`

## Deterministic Compilation Guarantees

Compilation behavior guarantees:
- stable source hashing and row normalization order,
- deterministic reduced-graph skeleton compile path (prune + constant fold),
- deterministic verification procedure selection by policy and support declarations,
- deterministic proof/compiled/validity/result hash chains in runtime state,
- explicit refusal codes on invalid/missing/unsupported compile conditions.

Runtime execution contract:
- compiled models may execute only when:
  - equivalence proof exists and is linked,
  - validity domain checks pass for current inputs.
- validity violations return deterministic refusal and preserve uncompiled fallback contract.

## Proof and Replay

Proof surfaces integrated:
- `compiled_model_hash_chain`
- `equivalence_proof_hash_chain`
- `validity_domain_hash_chain`
- `compile_result_hash_chain`
- `compile_request_hash_chain`

Tooling:
- `tools/meta/tool_verify_compiled_model.py`
- wrappers:
  - `tools/meta/tool_verify_compiled_model`
  - `tools/meta/tool_verify_compiled_model.cmd`

Compaction:
- compile artifacts are derived and compactable via PROV compaction window handling.

## Gate Snapshot

- TestX (COMPILE-0 required subset): PASS
  - `test_compile_engine_deterministic`
  - `test_equivalence_proof_required`
  - `test_validity_domain_checked`
  - `test_recompile_matches_hash`
  - `test_compiled_artifacts_compactable`

- topology map update: PASS
  - `python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`
  - `deterministic_fingerprint=36a176ec5de8acb9fb908b700296a9530c5db8c1f57a3d722d6c7decb2f6b3f4`

- AuditX STRICT: PASS (`promoted_blockers=0`)

- RepoX STRICT: REFUSAL due repository-wide pre-existing blockers outside COMPILE-0 scope
  - pre-existing SYS hard-fail analyzer promotion findings
  - pre-existing RWAM declaration gaps (`COMPILE`, `COUPLE`)
  - worktree hygiene refusals from unrelated uncommitted COUPLE/SYS paths

- strict build (`python tools/xstack/run.py strict --repo-root . --cache on`): REFUSAL due repository-global strict lane blockers outside COMPILE-0 scope
  - `compatx.check`, `pack.validate`, `registry.compile`, `lockfile.validate`, `session_boot.smoke`, full-lane `testx`, `securex`, `packaging`

## Readiness

COMPILE-0 readiness for STATEVEC-0 and PROC/LOGIC usage:
- universal compiled-model artifact and proof contracts: complete
- deterministic runtime hook surface (`compiled_model_is_valid`, `compiled_model_execute`): complete
- compile-request process path and replay verification tool: complete
- no domain-specific bespoke compiler required for initial integration: complete
