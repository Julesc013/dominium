Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# LIB7_LIBRARY_ENVELOPE

## Changed

- `tools/lib/lib_stress_common.py`
- `tools/lib/tool_generate_lib_stress.py`
- `tools/lib/tool_run_lib_stress.py`
- `tools/lib/tool_replay_save_open.py`
- `tools/launcher/launcher_cli.py`
- `lib/import/import_engine.py`
- `tools/xstack/repox/check.py`
- `tools/auditx/analyzers/e444_nondeterministic_bundle_smell.py`
- `tests/ops/lib_stress_envelope_tests.py`
- `tests/launcher/launcher_cli_tests.py`
- `data/regression/lib_full_baseline.json`
- `docs/audit/LIB7_RETRO_AUDIT.md`
- `docs/audit/LIB_FINAL_BASELINE.md`

## Demand IDs

- `surv.knap_stone_tools`

## Contract Meaning

- LIB-7 adds a deterministic stress/proof/regression envelope for installs, instances, saves, providers, and bundle flows
- launcher preflight now reruns PACK-COMPAT against resolved instance payloads instead of trusting lock presence alone
- save-open read-only fallback, provider ambiguity refusal, and export/import roundtrips are pinned into one regression lock
- cross-platform path spelling is normalized out of bundle hashes and stress projections
- product descriptor emission is anchored to the repo root so in-repo and external stress workspaces produce identical install and instance bundle hashes

## Unchanged

- authoritative simulation semantics remain unchanged
- prior LIB-0 through LIB-6 schemas stay in force
- no network dependency is introduced
- no silent migration or silent provider selection is introduced
