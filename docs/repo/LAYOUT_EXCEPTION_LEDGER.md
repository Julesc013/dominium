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
| `meta_extensions_engine_file` | `engine/foundation/meta/extensions/core.py` | `partial_review` | Active meta extension engine imported by governance, compatibility, domain, distribution, and audit tooling. | protected ownership review before relocation | POST-CONVERGE | high | Relocation crosses governance, compatibility, and domain semantics. |
| `numeric_discipline_file` | `engine/foundation/meta/numeric.py` | `partial_review` | Active numeric discipline helper imported by domain truth/geometry/ephemeris code. | numeric ownership review before relocation | POST-CONVERGE | high | No numeric semantic change authorized by exception cleanup. |
| `performance_root` | `performance` | `partial_review` | Active helper package imported by domain performance logic. | performance ownership review before relocation | POST-CONVERGE | high | Not pure tooling or generated evidence. |
| `tool_ui_bind_cmd` | `scripts/dev/shims/tool_ui_bind.cmd` | `compatibility_shim` | Documented zero-setup developer command wrapper. | allowed root shim via `scripts/dev/tool_shim.py` | POST-CONVERGE | low | Existing workflows and policy docs still expect the shim. |
| `tool_ui_doc_annotate_cmd` | `scripts/dev/shims/tool_ui_doc_annotate.cmd` | `compatibility_shim` | Documented zero-setup developer command wrapper. | allowed root shim via `scripts/dev/tool_shim.py` | POST-CONVERGE | low | Existing workflows and policy docs still expect the shim. |
| `tool_ui_validate_cmd` | `scripts/dev/shims/tool_ui_validate.cmd` | `compatibility_shim` | Documented zero-setup developer command wrapper. | allowed root shim via `scripts/dev/tool_shim.py` | POST-CONVERGE | low | Existing workflows and policy docs still expect the shim. |
| `validation_root` | `validation` | `partial_review` | Active unified validation engine imported by runtime, tools, compatibility shims, and tests. | validation ownership review before relocation | POST-CONVERGE | high | Do not create new validation root authority. |
| `artifacts_root` | `artifacts` | `generated_exception` | Tracked toolchain-run provenance remains. | provenance/evidence policy review | POST-CONVERGE | review | POST-CONVERGE-01 found 10 tracked JSON evidence files and left the exception active. |
| `dist_root` | `dist` | `generated_exception` | Tracked distribution projection files remain. | distribution projection policy review | POST-CONVERGE | medium | POST-CONVERGE-01 found 13 tracked projection files and left the exception active. |
| `bundles_root` | `bundles` | `partial_review` | Active bundle profile source referenced by XStack control tooling, skills, and docs. | protected bundle ownership review | POST-CONVERGE | high | Bundle IDs and lock semantics unchanged. |
| `compat_root` | `compat` | `partial_review` | Active compatibility implementation, migration/refusal helpers, and shims are imported by client, server, runtime, tooling, and tests. | protected compatibility split review | POST-CONVERGE | high | POST-CONVERGE-04 made no moves; compatibility semantics and shim imports are preserved. |
| `control_root` | `control` | `partial_review` | Active deterministic control gateway, IR, negotiation, fidelity, planning, capability, view, effect, and proof engines are imported by apps/client, game domains, net policies, tools, and XStack. | protected control ownership review | POST-CONVERGE | high | POST-CONVERGE-05 made no moves; process-only mutation, authority gates, proof, and Control IR semantics are preserved. |
| `core_root` | `core` | `partial_review` | Active deterministic substrate helpers for constraints, flow, graph/routing, hazards, schedules, spatial transforms, and state machines are imported by domains, tools, and XStack. | protected core ownership review | POST-CONVERGE | high | POST-CONVERGE-05 made no moves; deterministic substrate semantics and import paths are preserved. |
| `data_root` | `data` | `partial_review` | Large mixed surface: registries, authored pack declarations, world/domain data, planning mirrors, generated evidence, baselines, release/runtime data, and XStack metadata. | file-family split review | POST-CONVERGE | high | `data/packs` remains scoped authored pack content/declaration authority and residual-quarantined for single-root convergence. |
| `lib_root` | `lib` | `partial_review` | Active Python install, instance, save, store, bundle, import/export, and artifact library implementation is imported by runtime, tools, and tests. | protected library ownership review | POST-CONVERGE | high | POST-CONVERGE-04 made no moves; Python import and install/save/store semantics are preserved. |
| `libs_root` | `libs` | `partial_review` | Build- and ABI-critical C/C++ libraries, CMake targets, and public dom_contracts headers are actively referenced. | protected build/interface ownership review | POST-CONVERGE | high | POST-CONVERGE-04 made no moves; CMake targets, include paths, and ABI surfaces are preserved. |
| `locks_root` | `locks` | `partial_review` | Concrete pack lock artifact embeds path, hash, ordered pack, profile bundle, and universal identity metadata. | protected lock artifact ownership review | POST-CONVERGE | high | POST-CONVERGE-04 made no moves; lockfile identity and distribution copy behavior are preserved. |
| `modding_root` | `modding` | `partial_review` | Active mod trust and capability policy implementation imported by product/server and XStack/tooling. | protected mod policy ownership review | POST-CONVERGE | high | Not docs-only or authored mod content. |
| `models_root` | `models` | `partial_review` | Active constitutive model engine imported by engine, game domains, meta, and tests. | protected model engine ownership review | POST-CONVERGE | high | Not authored model assets. |
| `net_root` | `net` | `partial_review` | Active network transport, server-authoritative, lockstep, SRZ hybrid, anti-cheat, shard coordination, and test-harness modules are imported by apps, tools, and XStack tests. | protected network ownership review | POST-CONVERGE | high | POST-CONVERGE-05 made no moves; network protocol, server authority, anti-cheat, SRZ, resync, and replay semantics are preserved. |
| `packs_root` | `packs` | `partial_review` | Active runtime pack substrate for packaging, activation, compatibility, trust, capabilities, and distribution descriptors. | protected pack ownership review | POST-CONVERGE | high | Preserve `packs/` runtime-packaging scope and `data/packs/` authored-content scope. |
| `profiles_root` | `profiles` | `partial_review` | Active MVP profile bundle with embedded identity, fingerprint, content hash, and rel-path metadata. | profile ownership review before relocation | POST-CONVERGE | high | Profile IDs and hashes unchanged. |
| `repo_root` | `repo` | `partial_review` | Active release policy, RepoX rulesets/exemptions, and canon state are referenced by governance, release, and planning surfaces. | protected repo control-plane split review | POST-CONVERGE | high | POST-CONVERGE-04 made no moves; release/control-plane semantics are preserved. |
| `safety_root` | `safety` | `partial_review` | Active safety engine implementation and refusal/pattern semantics are imported by domain logic and backed by safety docs/schemas. | protected safety ownership review | POST-CONVERGE | high | POST-CONVERGE-04 made no moves; safety semantics are preserved. |
| `security_root` | `security` | `partial_review` | Active trust and license-capability implementation is referenced by release, tooling, docs, and schema surfaces. | protected security/trust ownership review | POST-CONVERGE | high | POST-CONVERGE-04 made no moves; trust and signing semantics are preserved. |
| `specs_root` | `specs` | `partial_review` | Active spec engine imports and canonical specs/reality normative documents remain protected. | protected spec ownership review | POST-CONVERGE | high | POST-CONVERGE-04 made no moves; normative spec authority is preserved. |
| `templates_root` | `templates` | `partial_review` | Adapter and domain contract templates referenced by protected specs/reality and XStack/AIDE contract surfaces. | docs/templates, contracts, or tools template review | POST-CONVERGE | medium | Kept until protected references can move with review. |
| `updates_root` | `updates` | `partial_review` | Tracked RepoX-generated update feeds are referenced by release/update tooling, command registry, tests, and release docs. | protected update feed ownership review | POST-CONVERGE | high | POST-CONVERGE-04 made no moves; update identity and release semantics are preserved. |

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

## POST-CONVERGE-03 Content / Pack / Profile / Bundle Cleanup

POST-CONVERGE-03 narrowed content, pack, profile, bundle, modding, model, and template exceptions after file-shape and reference review.

- Active exception count: 32.
- Retired exception count: 5.
- Retired in this task: none.
- Active target exceptions kept for review: `data_root`, `packs_root`, `profiles_root`, `bundles_root`, `modding_root`, `models_root`, `templates_root`.
- Identity-sensitive paths were not moved: pack IDs, profile IDs, bundle IDs, embedded hashes, and rel-path metadata remain unchanged.
- Unexcepted strict violation count: 0.
- Cleanup audit: `docs/repo/audits/POST_CONVERGE_03_CONTENT_PACK_CLEANUP.md`.

## POST-CONVERGE-04 Compat / Lib / Specs / Security / Update Cleanup

POST-CONVERGE-04 narrowed high-risk contract, compatibility, library, lock, repo, safety, security, spec, and update exceptions after reference and ownership review.

- Active exception count: 32.
- Retired exception count: 5.
- Retired in this task: none.
- Active target exceptions kept for protected review: `compat_root`, `lib_root`, `libs_root`, `locks_root`, `repo_root`, `safety_root`, `security_root`, `specs_root`, `updates_root`.
- Compatibility, security, safety, update, lockfile, ABI, and build semantics were not changed.
- Unexcepted strict violation count: 0.
- Cleanup audit: `docs/repo/audits/POST_CONVERGE_04_COMPAT_LIB_SPEC_SECURITY_CLEANUP.md`.

## POST-CONVERGE-05 Core / Control / Net Ownership Review

POST-CONVERGE-05 narrowed the final high-risk `core`, `control`, and `net` exceptions after protected ownership review.

- Active exception count: 32.
- Retired exception count: 5.
- Retired in this task: none.
- Active target exceptions kept for protected review: `core_root`, `control_root`, `net_root`.
- Process-only mutation, authority/control, network protocol, server, anti-cheat/integrity, SRZ/shard/resync, ABI, and build semantics were not changed.
- Ownership note: `docs/repo/CORE_CONTROL_NET_OWNERSHIP.md`.
- Unexcepted strict violation count: 0.
- Cleanup audit: `docs/repo/audits/POST_CONVERGE_05_CORE_CONTROL_NET_REVIEW.md`.
