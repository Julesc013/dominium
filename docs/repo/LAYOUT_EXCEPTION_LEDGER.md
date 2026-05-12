# Layout Exception Ledger

Status: PROVISIONAL

Phase: CONVERGE-10

Machine-readable source: `contracts/repo/layout_exceptions.toml`

No hidden exceptions are allowed. The table below is explanatory; the TOML ledger is the machine-readable source.

| Exception ID | Path | Classification | Reason | Target | Retirement Phase | Risk | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `missing_external_root` | `external` | `partial_review` | Canonical root declared but currently absent. | `external/` optionality or materialization review | CONVERGE-12 | low | Strict pass is exception-backed while absence is explicit. |
| `xstack_cache_root` | `.xstack_cache` | `generated_exception` | Generated/cache evidence root remains. | ignored cache or evidence review | CONVERGE-12 | review | Not source authority. |
| `root_init_py` | `__init__.py` | `compatibility_shim` | Root package marker remains for legacy import assumptions. | remove or allowlist after review | CONVERGE-12 | medium | Do not add more root package markers. |
| `governance_root` | `governance` | `partial_review` | Governance mirror material remains outside `docs/`. | `docs/governance` or mirror review | CONVERGE-12 | review | Must not compete with AGENTS.md or canon. |
| `ide_root` | `ide` | `partial_review` | IDE projection material remains at root. | tools, cmake, docs, or generated review | CONVERGE-12 | review | No source authority here. |
| `labs_root` | `labs` | `partial_review` | Experimental material requires ownership review. | archive, tools, docs, or experiment review | CONVERGE-12 | review | Experiments are not canonical roots. |
| `meta_root` | `meta` | `partial_review` | Mixed meta/provenance/reference material remains. | contracts, tools, docs, game, or archive split | CONVERGE-12 | review | No new authority here. |
| `meta_extensions_engine_file` | `meta_extensions_engine.py` | `partial_review` | Root-level engine-like module remains. | game, engine, tools, or contracts review | CONVERGE-12 | review | Ownership unresolved. |
| `numeric_discipline_file` | `numeric_discipline.py` | `partial_review` | Root-level numeric discipline module remains. | engine, contracts, tools, or docs review | CONVERGE-12 | review | Ownership unresolved. |
| `performance_root` | `performance` | `partial_review` | Performance tooling/evidence remains at root. | tools/performance or evidence review | CONVERGE-12 | review | Evidence is not source authority. |
| `tool_ui_bind_cmd` | `tool_ui_bind.cmd` | `compatibility_shim` | Root command wrapper remains. | scripts or tools wrapper review | CONVERGE-12 | low | New wrappers should avoid root. |
| `tool_ui_doc_annotate_cmd` | `tool_ui_doc_annotate.cmd` | `compatibility_shim` | Root command wrapper remains. | scripts or tools wrapper review | CONVERGE-12 | low | New wrappers should avoid root. |
| `tool_ui_validate_cmd` | `tool_ui_validate.cmd` | `compatibility_shim` | Root command wrapper remains. | scripts or tools wrapper review | CONVERGE-12 | low | New wrappers should avoid root. |
| `validation_root` | `validation` | `partial_review` | Validation material remains at root. | tools, tests, contracts, or docs review | CONVERGE-12 | review | No new validation root authority. |
| `artifacts_root` | `artifacts` | `generated_exception` | Generated or release-adjacent artifacts remain. | generated evidence or release exception review | CONVERGE-12 | review | Not source authority. |
| `build_root` | `build` | `generated_exception` | Generated build output root is present. | ignored generated output | CONVERGE-12 | low | Not source authority. |
| `dist_root` | `dist` | `generated_exception` | Distribution output root is present. | generated distribution or release exception | CONVERGE-12 | medium | Governed by distribution projection contract. |
| `out_root` | `out` | `generated_exception` | Generated build output root is present. | ignored generated output | CONVERGE-12 | low | Not source authority. |
| `bundles_root` | `bundles` | `partial_review` | Bundle source/export/generated surfaces require review. | contracts, content, release, tests, or generated review | CONVERGE-12 | review | Distribution layout is separate. |
| `compat_root` | `compat` | `partial_review` | Compatibility material is mixed. | contracts/compatibility plus runtime/tools split | CONVERGE-12 | high | Do not move wholesale. |
| `control_root` | `control` | `partial_review` | Control surfaces are process-sensitive and mixed. | runtime, contracts, game, or tools review | CONVERGE-12 | high | Preserve process-only mutation. |
| `core_root` | `core` | `partial_review` | Core material may include universal primitives or mixed surfaces. | engine, game, runtime, contracts, or tools split | CONVERGE-12 | high | Do not classify by name alone. |
| `data_root` | `data` | `partial_review` | Data root is mixed across content, registries, mirrors, and evidence. | content, contracts, docs, tools, or evidence split | CONVERGE-12 | high | Do not promote projections to authority. |
| `lib_root` | `lib` | `partial_review` | Library root remains ambiguous. | engine, runtime, external, contracts, or tools review | CONVERGE-12 | review | No new library root authority. |
| `libs_root` | `libs` | `partial_review` | Library root remains ambiguous. | engine, runtime, external, contracts, or tools review | CONVERGE-12 | review | No new library root authority. |
| `locks_root` | `locks` | `partial_review` | Concrete lock artifacts are not pure lockfile schemas. | contracts/locks, content/store-lock, or release review | CONVERGE-12 | high | Runtime mutable locks do not belong in contracts. |
| `modding_root` | `modding` | `partial_review` | Modding material spans content, docs, contracts, tools, and package policy. | content/modding, contracts, docs, or tools review | CONVERGE-12 | review | Use ownership roots for new material. |
| `models_root` | `models` | `partial_review` | Model material needs content/generated distinction. | content/models or generated review | CONVERGE-12 | review | No generated model authority. |
| `net_root` | `net` | `partial_review` | Network material remains mixed. | runtime/network plus apps/server and contracts review | CONVERGE-12 | high | Preserve runtime and server behavior. |
| `packs_root` | `packs` | `partial_review` | Pack substrate remains review-sensitive. | content/packs plus contracts/packs and release review | CONVERGE-12 | high | Preserve pack IDs and compatibility. |
| `profiles_root` | `profiles` | `partial_review` | Profiles need content/runtime-store review. | content/profiles or runtime-store projection review | CONVERGE-12 | medium | Profiles are not mutable store by default. |
| `repo_root` | `repo` | `partial_review` | Transitional repo control-plane root remains. | contracts/repo, docs/repo, release, or tools split | CONVERGE-12 | high | Do not add new layout authority here. |
| `safety_root` | `safety` | `partial_review` | Protected safety material requires review. | contracts/safety, docs/safety, tools, or runtime policy | CONVERGE-12 | high | Safety meaning must not drift. |
| `security_root` | `security` | `partial_review` | Protected security material requires review. | contracts/security, docs/security, release, tools, or runtime policy | CONVERGE-12 | high | Trust semantics require review. |
| `specs_root` | `specs` | `partial_review` | Protected normative specs need careful split. | contracts/specs, docs/specs, or semantic spec review | CONVERGE-12 | high | Reality specs retain established authority. |
| `templates_root` | `templates` | `partial_review` | Templates may be content, contracts, tooling input, or generated projection. | content/templates, contracts, tools, or generated review | CONVERGE-12 | review | No new root-level template authority. |
| `updates_root` | `updates` | `partial_review` | Update material belongs to release/control-plane review. | release/update, contracts/distribution, or ops review | CONVERGE-12 | high | Do not change update identity here. |

Active exception count: 37.

Unexcepted violation count after CONVERGE-10 validator updates: 0.

Exception retirement should be reviewed in CONVERGE-12 unless a later scoped task retires a specific exception earlier.
