Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# Validation Inventory

This inventory enumerates the significant validation surfaces currently present in the repository and maps each one to the unified validation pipeline.

| Path | Purpose | Inputs / Outputs | Overlaps | Unified Suite | Adapter | Status |
| --- | --- | --- | --- | --- | --- | --- |
| `src/compat/capability_negotiation.py` | Capability negotiation and record verification engine. | endpoint descriptors, contract bundle hash / negotiation record, verification result | `validate.negotiation` | `validate.negotiation` | `direct_python` | `active_adapter` |
| `src/lib/artifact/artifact_validator.py` | Artifact manifest validator. | artifact.manifest.json / structured validation report | `validate.library` | `validate.library` | `direct_python` | `active_adapter` |
| `src/lib/install/install_validator.py` | Install manifest and install registry validator. | install.manifest.json, install registry / structured validation report | `validate.library` | `validate.library` | `direct_python` | `active_adapter` |
| `src/lib/instance/instance_validator.py` | Instance manifest validator. | instance.manifest.json / structured validation report | `validate.library` | `validate.library` | `direct_python` | `active_adapter` |
| `src/lib/save/save_validator.py` | Save manifest validator. | save.manifest.json, contract bundle, pack lock / structured validation report | `validate.library` | `validate.library` | `direct_python` | `active_adapter` |
| `src/meta/stability/stability_validator.py` | META-STABILITY registry and pack.compat validation surface. | registry JSON, pack.compat manifests / structured validation report | `validate.registries` | `validate.registries` | `direct_python` | `active_adapter` |
| `src/packs/compat/pack_verification_pipeline.py` | PACK-COMPAT verification and pack lock generation surface. | dist root, bundle selection, contract bundle / pack compatibility report, pack lock | `validate.packs` | `validate.packs` | `coverage_adapter` | `deprecated` |
| `tools/audit/tool_run_arch_audit.py` | ARCH-AUDIT constitutional architecture validator. | repo tree, registry reports / markdown report, json report | `validate.arch_audit`, `validate.determinism` | `validate.arch_audit` | `direct_python` | `active_adapter` |
| `tools/ci/validate_all.py` | Legacy wrapper that locates and shells out to validate_all. | compiled validate_all binary / subprocess exit code, stdout passthrough | `validate.determinism` | `validate.determinism` | `coverage_adapter` | `deprecated` |
| `tools/compatx/compatx.py` | Legacy compatibility validation CLI for schema, pack, and semantic contract checks. | compat registries, bundle paths / json to stdout, audit docs | `validate.contracts`, `validate.packs` | `validate.contracts` | `direct_python` | `active_adapter` |
| `tools/core/tool_graph_validate.py` | Legacy graph payload validator. | graph payloads, schema ids / json report | `validate.schemas` | `validate.schemas` | `coverage_adapter` | `deprecated` |
| `tools/coredata_validate/coredata_validate_main.cpp` | Legacy coredata validation executable. | authoring roots, pack roots / process exit code, stdout report | `validate.schemas`, `validate.registries` | `validate.schemas` | `coverage_adapter` | `deprecated` |
| `tools/data_validate/data_validate_main.c` | Legacy data TLV validation entrypoint. | binary payload, schema id, schema version / process exit code, stdout report | `validate.schemas` | `validate.schemas` | `coverage_adapter` | `deprecated` |
| `tools/domain/tool_domain_validate.py` | Domain/contract/solver structural registry validator. | domain registries / structured pass/fail report | `validate.registries` | `validate.registries` | `coverage_adapter` | `deprecated` |
| `tools/fab/fab_validate.py` | Legacy fabrication authoring validator. | fabrication JSON payload / json to stdout | `validate.schemas`, `validate.registries` | `validate.registries` | `coverage_adapter` | `deprecated` |
| `tools/time/tool_compaction_anchor_check.py` | TIME-ANCHOR compaction boundary verifier. | provenance windows, anchor rows / json compaction report | `validate.time_anchor` | `validate.time_anchor` | `direct_python` | `active_adapter` |
| `tools/time/tool_verify_longrun_ticks.py` | TIME-ANCHOR long-run verification entrypoint. | time anchor policy, anchor artifacts / json verification report | `validate.time_anchor` | `validate.time_anchor` | `direct_python` | `active_adapter` |
| `tools/validate/hygiene_validate_cli.cpp` | Legacy hygiene validation CLI entrypoint. | workspace tree / process exit code, stdout report | `validate.arch_audit` | `validate.arch_audit` | `coverage_adapter` | `deprecated` |
| `tools/validation/validate_all_main.cpp` | Legacy compiled aggregate validator entrypoint. | workspace tree, validation fixtures / process exit code, stdout report | `validate.determinism`, `validate.arch_audit` | `validate.determinism` | `coverage_adapter` | `deprecated` |
| `tools/validation/validators_registry.cpp` | Legacy validator registration table for compiled aggregate validation. | compiled validator set / validator registry wiring | `validate.determinism` | `validate.determinism` | `coverage_adapter` | `deprecated` |
| `tools/validator/validator_main.cpp` | Legacy standalone validator main focused on schema-style checks. | authored payloads / process exit code, stdout report | `validate.schemas` | `validate.schemas` | `coverage_adapter` | `deprecated` |
| `tools/worldgen_offline/validation_checker.py` | Legacy output comparison validator for offline worldgen tooling. | expected JSON, actual JSON / mismatch report | `validate.determinism` | `validate.determinism` | `coverage_adapter` | `deprecated` |
| `tools/xstack/compatx/check.py` | Deterministic schema/version check surface. | schemas, CompatX version registry / structured pass/fail report | `validate.schemas` | `validate.schemas` | `direct_python` | `active_adapter` |

## Summary

- Surface count: `23`
- Active adapters: `11`
- Coverage adapters: `12`
- Deprecated surfaces: `12`
