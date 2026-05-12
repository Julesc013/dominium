# Layout Exception Ledger

Status: PROVISIONAL

Phase: CONVERGE-10

Machine-readable source: `contracts/repo/layout_exceptions.toml`

No hidden exceptions are allowed. The table below is explanatory; the TOML ledger is the machine-readable source.

| Exception ID | Path | Classification | Reason | Target | Retirement Phase | Risk | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `missing_external_root` | `external` | `partial_review` | Canonical root declared but currently absent. | `external/` optionality or materialization review | POST-CONVERGE | low | Strict pass is exception-backed while absence is explicit. |
| `governance_root` | `governance` | `partial_review` | Active deterministic governance profile helper imported by release and tooling surfaces. | protected governance ownership review | POST-CONVERGE | high | Not a canonical doctrine source; AGENTS.md and canon remain authoritative. |
| `ide_root` | `ide` | `partial_review` | Intentional IDE projection boundary with tracked README, manifest schema, and examples. | keep root projection boundary until policy relocation | POST-CONVERGE | medium | Generation and quarantine checks still reference `ide/`. |
| `meta_root` | `meta` | `partial_review` | Mixed semantic, provenance, reference, and tooling helpers remain active. | protected ownership split review | POST-CONVERGE | high | Do not bind new authority here without contract update. |
| `meta_extensions_engine_file` | `meta_extensions_engine.py` | `partial_review` | Active meta extension engine imported by governance, compatibility, domain, distribution, and audit tooling. | protected ownership review before relocation | POST-CONVERGE | high | Relocation crosses governance, compatibility, and domain semantics. |
| `numeric_discipline_file` | `numeric_discipline.py` | `partial_review` | Active numeric discipline helper imported by domain truth/geometry/ephemeris code. | numeric ownership review before relocation | POST-CONVERGE | high | No numeric semantic change authorized by exception cleanup. |
| `performance_root` | `performance` | `partial_review` | Active helper package imported by domain performance logic. | performance ownership review before relocation | POST-CONVERGE | high | Not pure tooling or generated evidence. |
| `tool_ui_bind_cmd` | `tool_ui_bind.cmd` | `compatibility_shim` | Documented zero-setup developer command wrapper. | allowed root shim via `scripts/dev/tool_shim.py` | POST-CONVERGE | low | Existing workflows and policy docs still expect the shim. |
| `tool_ui_doc_annotate_cmd` | `tool_ui_doc_annotate.cmd` | `compatibility_shim` | Documented zero-setup developer command wrapper. | allowed root shim via `scripts/dev/tool_shim.py` | POST-CONVERGE | low | Existing workflows and policy docs still expect the shim. |
| `tool_ui_validate_cmd` | `tool_ui_validate.cmd` | `compatibility_shim` | Documented zero-setup developer command wrapper. | allowed root shim via `scripts/dev/tool_shim.py` | POST-CONVERGE | low | Existing workflows and policy docs still expect the shim. |
| `validation_root` | `validation` | `partial_review` | Active unified validation engine imported by runtime, tools, compatibility shims, and tests. | validation ownership review before relocation | POST-CONVERGE | high | Do not create new validation root authority. |
| `artifacts_root` | `artifacts` | `generated_exception` | Tracked toolchain-run provenance remains. | provenance/evidence policy review | POST-CONVERGE | review | POST-CONVERGE-01 found 10 tracked JSON evidence files and left the exception active. |
| `dist_root` | `dist` | `generated_exception` | Tracked distribution projection files remain. | distribution projection policy review | POST-CONVERGE | medium | POST-CONVERGE-01 found 13 tracked projection files and left the exception active. |
| `bundles_root` | `bundles` | `partial_review` | Bundle source/export/generated surfaces require review. | contracts, content, release, tests, or generated review | POST-CONVERGE | review | Distribution layout is separate. |
| `compat_root` | `compat` | `partial_review` | Compatibility material is mixed. | contracts/compatibility plus runtime/tools split | POST-CONVERGE | high | Do not move wholesale. |
| `control_root` | `control` | `partial_review` | Control surfaces are process-sensitive and mixed. | runtime, contracts, game, or tools review | POST-CONVERGE | high | Preserve process-only mutation. |
| `core_root` | `core` | `partial_review` | Core material may include universal primitives or mixed surfaces. | engine, game, runtime, contracts, or tools split | POST-CONVERGE | high | Do not classify by name alone. |
| `data_root` | `data` | `partial_review` | Data root is mixed across content, registries, mirrors, and evidence. | content, contracts, docs, tools, or evidence split | POST-CONVERGE | high | Do not promote projections to authority. |
| `lib_root` | `lib` | `partial_review` | Library root remains ambiguous. | engine, runtime, external, contracts, or tools review | POST-CONVERGE | review | No new library root authority. |
| `libs_root` | `libs` | `partial_review` | Library root remains ambiguous. | engine, runtime, external, contracts, or tools review | POST-CONVERGE | review | No new library root authority. |
| `locks_root` | `locks` | `partial_review` | Concrete lock artifacts are not pure lockfile schemas. | contracts/locks, content/store-lock, or release review | POST-CONVERGE | high | Runtime mutable locks do not belong in contracts. |
| `modding_root` | `modding` | `partial_review` | Modding material spans content, docs, contracts, tools, and package policy. | content/modding, contracts, docs, or tools review | POST-CONVERGE | review | Use ownership roots for new material. |
| `models_root` | `models` | `partial_review` | Model material needs content/generated distinction. | content/models or generated review | POST-CONVERGE | review | No generated model authority. |
| `net_root` | `net` | `partial_review` | Network material remains mixed. | runtime/network plus apps/server and contracts review | POST-CONVERGE | high | Preserve runtime and server behavior. |
| `packs_root` | `packs` | `partial_review` | Pack substrate remains review-sensitive. | content/packs plus contracts/packs and release review | POST-CONVERGE | high | Preserve pack IDs and compatibility. |
| `profiles_root` | `profiles` | `partial_review` | Profiles need content/runtime-store review. | content/profiles or runtime-store projection review | POST-CONVERGE | medium | Profiles are not mutable store by default. |
| `repo_root` | `repo` | `partial_review` | Transitional repo control-plane root remains. | contracts/repo, docs/repo, release, or tools split | POST-CONVERGE | high | Do not add new layout authority here. |
| `safety_root` | `safety` | `partial_review` | Protected safety material requires review. | contracts/safety, docs/safety, tools, or runtime policy | POST-CONVERGE | high | Safety meaning must not drift. |
| `security_root` | `security` | `partial_review` | Protected security material requires review. | contracts/security, docs/security, release, tools, or runtime policy | POST-CONVERGE | high | Trust semantics require review. |
| `specs_root` | `specs` | `partial_review` | Protected normative specs need careful split. | contracts/specs, docs/specs, or semantic spec review | POST-CONVERGE | high | Reality specs retain established authority. |
| `templates_root` | `templates` | `partial_review` | Templates may be content, contracts, tooling input, or generated projection. | content/templates, contracts, tools, or generated review | POST-CONVERGE | review | No new root-level template authority. |
| `updates_root` | `updates` | `partial_review` | Update material belongs to release/control-plane review. | release/update, contracts/distribution, or ops review | POST-CONVERGE | high | Do not change update identity here. |

Active exception count: 32.

Unexcepted violation count after CONVERGE-10 validator updates: 0.

Exception retirement was reviewed in CONVERGE-12; active exceptions remain POST-CONVERGE follow-up items unless a later scoped task retires a specific exception earlier.

## CONVERGE-12 Review

CONVERGE-12 did not perform broad physical moves, so no active exceptions were retired in this task. All 37 active exceptions remain explicit and were retargeted to `POST-CONVERGE` retirement metadata.

There are zero unexcepted strict layout violations after validator review.

Final audit: `docs/repo/audits/CONVERGE_12_FINAL_AUDIT.md`.

## POST-CONVERGE-00 Triage

POST-CONVERGE-00 rechecked the active exception ledger against live `main`.

- Active exception count: 37.
- Unexcepted strict violation count: 0.
- Exceptions are now post-CONVERGE retirement items.
- Triage report: `docs/repo/audits/POST_CONVERGE_EXCEPTION_TRIAGE.md`.
- Retirement queue: `docs/repo/EXCEPTION_RETIREMENT_QUEUE.md`.

No exceptions were retired in POST-CONVERGE-00.

## POST-CONVERGE-01 Generated Output Cleanup

POST-CONVERGE-01 retired the ignored, untracked generated/cache exceptions for `.xstack_cache/`, `build/`, and `out/`.

- Active exception count: 34.
- Retired generated/output exceptions: 3.
- Active generated/output exceptions: `artifacts_root` and `dist_root`.
- Unexcepted strict violation count: 0.
- Cleanup audit: `docs/repo/audits/POST_CONVERGE_01_GENERATED_OUTPUT_CLEANUP.md`.

Retired entries remain in `contracts/repo/layout_exceptions.toml` under `retired_exceptions.*` for audit history. They are not active strict-validation exceptions.

## POST-CONVERGE-02 Wrapper / Tooling / Governance Cleanup

POST-CONVERGE-02 retired the unused root package marker and moved quarantined labs documentation out of the source root while narrowing the remaining wrapper/tooling/governance exceptions.

- Active exception count: 32.
- Retired exception count: 5.
- Retired in this task: `root_init_py`, `labs_root`.
- Compatibility shims kept: `tool_ui_bind_cmd`, `tool_ui_doc_annotate_cmd`, `tool_ui_validate_cmd`.
- Protected review exceptions kept: `governance_root`, `ide_root`, `meta_root`, `meta_extensions_engine_file`, `numeric_discipline_file`, `performance_root`, `validation_root`.
- Unexcepted strict violation count: 0.
- Cleanup audit: `docs/repo/audits/POST_CONVERGE_02_WRAPPER_TOOLING_CLEANUP.md`.
