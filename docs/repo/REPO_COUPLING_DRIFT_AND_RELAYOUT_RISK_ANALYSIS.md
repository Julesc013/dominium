Status: DERIVED
Last Reviewed: 2026-04-08
Supersedes: none
Superseded By: none
Stability: stable
Series Scope: repo-structure discovery and design
Series Role: risk and coupling packet for later topology-option, preferred-target, shim-design, migration-sequencing, and ownership-reconciliation prompts; downstream of stronger canon, the Omega0 constraint packet, the Omega1 topology reality map, audit evidence, and live implementation evidence
Replacement Target: later explicit repo-structure follow-up after approved topology decisions or new playable-baseline evidence
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/repo/REPO_NON_NEGOTIABLES_AND_CURRENT_REALITY.md`, `data/repo/repo_non_negotiables_and_current_reality.json`, `docs/repo/REPO_TOPOLOGY_PATHS_AND_OWNERSHIP_REALITY_MAP.md`, `data/repo/repo_topology_paths_and_ownership_reality_map.json`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `data/planning/checkpoints/checkpoint_c_zeta_mega_validation_and_closure.json`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `data/planning/next_execution_order_post_zeta.json`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`, `docs/audit/ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_PLAYTEST_READINESS.md`, `docs/audit/ULTRA_REPO_AUDIT_GAPS_AND_TODOS.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_BUILD_RUN_TEST_MATRIX.md`, `docs/audit/ULTRA_REPO_AUDIT_WIRING_MAP.md`, `docs/audit/ULTRA_REPO_AUDIT_DOC_VS_CODE_MISMATCHES.md`, `data/audit/install_discovery_report.json`, `data/audit/ui_surface_report.json`, `docs/xstack/CHECKPOINT_C_XSTACK_AIDE_CLOSURE.md`, `data/xstack/checkpoint_c_xstack_aide_closure.json`, `docs/xstack/NEXT_EXECUTION_ORDER_POST_XSTACK_AIDE.md`, `data/xstack/next_execution_order_post_xstack_aide.json`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`, `docs/xstack/XSTACK_TO_AIDE_EXTRACTION_MAP.md`, `appshell/paths/virtual_paths.py`, `appshell/mode_dispatcher.py`, `appshell/tui_stub.py`, `appshell/supervisor/supervisor_engine.py`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/sessionx/creator.py`, `tools/xstack/sessionx/runner.py`, `tools/mvp/runtime_entry.py`, `tools/mvp/runtime_bundle.py`, `tools/xstack/registry_compile/constants.py`, `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, `server/server_main.py`, `server/net/loopback_transport.py`, `release/release_manifest_engine.py`, `release/component_graph_resolver.py`, `release/update_resolver.py`, `security/trust/trust_verifier.py`, `validation/validation_engine.py`, `tools/validation/tool_run_validation.py`, `tools/import_bridge.py`, `data/registries/virtual_root_registry.json`

# Repo Coupling, Drift, And Relayout Risk Analysis

## A. Purpose And Scope

This artifact measures the structural risk of future repo relayout work before any target topology or migration sequence is chosen.

It exists because Omega0 already froze what must not break and Omega1 already mapped what exists. What later design prompts still need is the risk layer:

- which subsystems are tightly coupled now
- which roots only look separate but are operationally entangled
- which path and ownership narratives have drifted away from live implementation
- which roots are safe to move later, likely need shims, or should not move before the canonical playable baseline is stabilized

Its relationship to Omega0 is strict:

- Omega0 freezes the non-negotiable survival rules
- this artifact identifies which live seams make those survival rules hard to preserve during relayout

Its relationship to Omega1 is also strict:

- Omega1 maps roots, ownership classes, and path contracts
- this artifact ranks the coupling strength and move risk of those same roots and contracts

Its relationship to the playable-baseline priority is central rather than incidental:

- the strongest relayout risk is not aesthetic untidiness
- the strongest relayout risk is breaking the repo-local session-plus-loopback authority path before one canonical playtest command is hardened
- baseline-critical startup ambiguity, repo-root math, save-root coupling, supervision fragility, and wrapper confusion are therefore treated as first-order risk findings

For later repo-structure work, the direct answers are:

- Which subsystems are tightly coupled right now:
  the critical and high-coupling findings in Sections D and H.
- Which docs and path narratives have drifted away from implementation reality:
  Section E.
- What is safe to move later, what likely needs shims, and what should not move yet:
  Sections F and G.
- What structural risks threaten the canonical playable-baseline path:
  Section H.
- What prompt this enables next:
  a topology-option generation prompt that compares candidate target shapes against the recorded coupling and relayout risk packet instead of against abstract cleanliness goals.

This is a risk analysis packet, not a relayout decision and not a migration plan.

## B. Coupling-Analysis Method

This artifact uses the following working definitions.

### What Counts As Structural Coupling

Structural coupling exists when a root or subsystem cannot be relocated safely without changing how other roots import it, include it, spawn it, validate it, or derive identity from its physical location.

Examples in this repo:

- cross-root imports from `tools/launcher/launch.py` and `tools/setup/setup_cli.py` into `appshell/`, `release/`, and `security/trust/`
- `client/local_server/local_server_controller.py` importing `runtime.process_spawn`, `server.*`, and `server.net.loopback_transport`
- validation entrypoints and reports depending on both `tools/validation/` and `validation/`

### What Counts As Path Coupling

Path coupling exists when code, scripts, or machine-readable registries expect specific relative or absolute layout conventions.

Examples in this repo:

- `REPO_ROOT_HINT` math in Python entrypoints
- `server/server_main.py` escaping the repo root
- `tools/xstack/session_boot.py` documenting `saves/<save_id>/session_spec.json`
- `tools/xstack/sessionx/runner.py` hardcoding `repo_root/saves/<save_id>`
- SessionX compile outputs depending on `build/registries/` and `build/lockfile.json`
- launcher and setup flows expecting `dist/manifests/release_manifest.json`

### What Counts As Ownership Coupling

Ownership coupling exists when two roots look distinct but a live subsystem only works because both participate in one shared contract or truth family.

Examples in this repo:

- `schema/` versus `schemas/`
- `packs/` versus `data/packs/`
- authored MVP assets versus registry-compiled default bundle ids
- `launcher/` and `setup/` native wrappers versus the stronger Python/AppShell shells under `tools/`

### What Counts As Documentation Drift

Documentation drift exists when prose or machine-readable mirrors:

- refer to stale paths
- overstate maturity or portability
- understate already-live implementation
- hide compatibility scaffolding that keeps stale narratives operational
- describe cleaner boundaries than the code actually exposes

### How Move Risk Is Judged

Move risk is judged conservatively from five factors:

1. whether the root sits on an Omega0 survival path
2. how many live entrypoints or data contracts depend on its current location
3. whether generated intermediates or virtual paths hide the dependency
4. whether a compatibility bridge already exists and would need to be preserved
5. whether the audit already identifies the surface as blocked, fragile, or wrapper-heavy

### Operational Meaning Of The Risk Labels

- Safe to move later:
  later relayout work could plausibly move the surface after ordinary review because the current baseline does not depend on it heavily.
- Needs shim:
  later relayout work would probably need path adapters, import bridges, mirror regeneration, or compatibility wrappers to preserve current flows.
- Do not move yet:
  later relayout work should not move the surface before the canonical playable-baseline path is hardened and the current blocker class is removed.

## C. Coupling Classes

| Class ID | Class | Real meaning |
| --- | --- | --- |
| `low_coupling_easy_to_isolate` | Low coupling / easy to isolate | The surface has narrow dependencies and does not currently sit on the strongest baseline path. Moving it later would still need review, but not major protection work. |
| `moderate_coupling_review_required` | Moderate coupling / likely needs review | The surface has noticeable cross-root dependencies or build ties, but the baseline would probably survive careful movement if reviewed explicitly. |
| `high_coupling_likely_needs_shim` | High coupling / likely needs shim | The surface participates in live boot, validation, release, or data-location contracts. Relayout would likely require shims, adapters, or bridge preservation. |
| `critical_coupling_do_not_move_before_baseline_stabilization` | Critical coupling / do not move before baseline stabilization | The surface sits directly on the current playable-baseline path or its proof surface, and moving it early would risk breaking build, session, boot, attach, validation, or operator continuity. |
| `ambiguous_coupling_investigate_later` | Ambiguous coupling / investigate later | The surface is visibly entangled or split across roots, but the repo has not yet resolved which side is the future owner. Treat it as a design hazard, not as a clean move candidate. |

## D. Concrete Subsystem Coupling Ledger

### `CRA-001 - appshell_core_and_virtual_paths`

- Root/path or subsystem:
  `appshell/` core shell, command, mode-dispatch, and virtual-root path surfaces
- Coupling class:
  `critical_coupling_do_not_move_before_baseline_stabilization`
- What it is coupled to:
  `tools/launcher/`, `tools/setup/`, `server/server_main.py`, `appshell/supervisor/`, `data/registries/virtual_root_registry.json`, `dist/`, `profiles/`, `locks/`, `packs/`, `saves/`, `runtime/`
- Nature of the coupling:
  import, runtime, path, data, entrypoint, policy
- Why it matters:
  this is the current canonical repo-local shell/bootstrap substrate, and many other roots rely on its virtual-root and mode-dispatch assumptions rather than resolving paths independently
- Baseline-critical:
  yes
- Likely safe to move later:
  no
- Likely needs shims:
  yes
- Should not move yet:
  yes
- Evidence notes:
  `appshell/paths/virtual_paths.py`, `data/registries/virtual_root_registry.json`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `server/server_main.py`

### `CRA-002 - appshell_supervisor_and_ipc`

- Root/path or subsystem:
  `appshell/supervisor/` and related IPC orchestration
- Coupling class:
  `high_coupling_likely_needs_shim`
- What it is coupled to:
  `runtime/process_spawn.py`, `tools/appshell/supervisor_service.py`, `tools/appshell/supervised_product_host.py`, `VROOT_IPC`, `profiles/bundles/bundle.mvp_default.json`, `locks/pack_lock.mvp_default.json`, `data/session_templates/session.mvp_default.json`
- Nature of the coupling:
  runtime, path, data, policy
- Why it matters:
  the supervisor path is not the whole playable baseline, but the audit already identifies supervision fragility as a blocker for repeatable internal sessions
- Baseline-critical:
  yes
- Likely safe to move later:
  no
- Likely needs shims:
  yes
- Should not move yet:
  yes
- Evidence notes:
  `appshell/supervisor/supervisor_engine.py`, `docs/audit/ULTRA_REPO_AUDIT_GAPS_AND_TODOS.md`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`

### `CRA-003 - launcher_and_setup_python_shells`

- Root/path or subsystem:
  `tools/launcher/launch.py` and `tools/setup/setup_cli.py`
- Coupling class:
  `critical_coupling_do_not_move_before_baseline_stabilization`
- What it is coupled to:
  `appshell/`, `release/`, `security/trust/`, `data/registries/`, `dist/`, install discovery, repo-local `saves/`, compiled wrapper expectations
- Nature of the coupling:
  import, runtime, path, data, entrypoint, policy
- Why it matters:
  these are the strongest live operator shells now, so a relayout that destabilizes them would directly weaken the path Omega0 says must survive
- Baseline-critical:
  yes
- Likely safe to move later:
  no
- Likely needs shims:
  yes
- Should not move yet:
  yes
- Evidence notes:
  `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`

### `CRA-004 - native_launcher_and_setup_wrappers`

- Root/path or subsystem:
  `launcher/` and `setup/` native wrapper roots, especially GUI/TUI leaves
- Coupling class:
  `moderate_coupling_review_required`
- What it is coupled to:
  verify build graph, include surfaces, packaging expectations, wrapper parity narratives
- Nature of the coupling:
  build, include, wrapper, maturity
- Why it matters:
  these roots are not the strongest baseline path, but moving them still affects compiled build topology and can confuse operator-facing narratives
- Baseline-critical:
  no
- Likely safe to move later:
  yes
- Likely needs shims:
  no
- Should not move yet:
  no
- Evidence notes:
  `launcher/CMakeLists.txt`, `setup/CMakeLists.txt`, `launcher/gui/launcher_gui_stub.c`, `launcher/tui/launcher_tui_stub.c`, `setup/cli/setup_cli_main.c`

### `CRA-005 - client_local_server_and_loopback_authority`

- Root/path or subsystem:
  `client/local_server/` plus the local loopback authority path
- Coupling class:
  `critical_coupling_do_not_move_before_baseline_stabilization`
- What it is coupled to:
  `runtime/process_spawn.py`, `server/server_main.py`, `server/net/loopback_transport.py`, `server.runtime.*`, repo-local `saves/`, `build/client/local_singleplayer/<save_id>/diag/`
- Nature of the coupling:
  import, runtime, path, data, entrypoint
- Why it matters:
  this is the strongest evidence-backed local singleplayer path and is central to the current playable-baseline target
- Baseline-critical:
  yes
- Likely safe to move later:
  no
- Likely needs shims:
  yes
- Should not move yet:
  yes
- Evidence notes:
  `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, `server/net/loopback_transport.py`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`

### `CRA-006 - server_python_boot_and_process_spawn`

- Root/path or subsystem:
  `server/server_main.py` plus `runtime/process_spawn.py`
- Coupling class:
  `critical_coupling_do_not_move_before_baseline_stabilization`
- What it is coupled to:
  `appshell/`, `client/local_server/`, `server.runtime.*`, `server.net.loopback_transport`, repo-root path math, `saves/`
- Nature of the coupling:
  import, runtime, path, entrypoint
- Why it matters:
  this is the current Python server boot seam, and it is already fragile because the repo-root hint is wrong while local singleplayer still spawns it explicitly
- Baseline-critical:
  yes
- Likely safe to move later:
  no
- Likely needs shims:
  yes
- Should not move yet:
  yes
- Evidence notes:
  `runtime/process_spawn.py`, `server/server_main.py`, `docs/audit/ULTRA_REPO_AUDIT_GAPS_AND_TODOS.md`

### `CRA-007 - session_create_boot_and_runner_pipeline`

- Root/path or subsystem:
  `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/sessionx/creator.py`, and `tools/xstack/sessionx/runner.py`
- Coupling class:
  `critical_coupling_do_not_move_before_baseline_stabilization`
- What it is coupled to:
  `profiles/`, `locks/`, `data/session_templates/`, `data/registries/`, `build/registries/`, `build/lockfile.json`, repo-local `saves/`, registry-compile defaults
- Nature of the coupling:
  import, runtime, path, data, entrypoint
- Why it matters:
  the pipeline both materializes and boots the current baseline session artifacts, but the create and boot sides still disagree about alternate save roots
- Baseline-critical:
  yes
- Likely safe to move later:
  no
- Likely needs shims:
  yes
- Should not move yet:
  yes
- Evidence notes:
  `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/sessionx/creator.py`, `tools/xstack/sessionx/runner.py`, `docs/audit/ULTRA_REPO_AUDIT_DOC_VS_CODE_MISMATCHES.md`

### `CRA-008 - release_trust_install_discovery_cluster`

- Root/path or subsystem:
  `release/`, `security/trust/`, install discovery, and manifest-resolution paths
- Coupling class:
  `high_coupling_likely_needs_shim`
- What it is coupled to:
  `tools/setup/setup_cli.py`, `tools/launcher/launch.py`, `data/registries/component_graph_registry.json`, `data/registries/install_profile_registry.json`, `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `dist/`, `store/`, `manifests/`
- Nature of the coupling:
  import, runtime, path, data, policy
- Why it matters:
  the release, trust, and install-discovery surfaces are already wired into the stronger operator shells, so a relayout here would need explicit compatibility preservation
- Baseline-critical:
  yes
- Likely safe to move later:
  no
- Likely needs shims:
  yes
- Should not move yet:
  no
- Evidence notes:
  `release/release_manifest_engine.py`, `release/component_graph_resolver.py`, `release/update_resolver.py`, `security/trust/trust_verifier.py`, `tools/setup/setup_cli.py`

### `CRA-009 - validation_testx_ctest_and_report_pipeline`

- Root/path or subsystem:
  `validation/`, `tools/validation/`, `tools/xstack/testx_all.py`, `tests/`, `docs/audit/`, `data/audit/`
- Coupling class:
  `high_coupling_likely_needs_shim`
- What it is coupled to:
  `data/registries/validation_suite_registry.json`, `tools/import_bridge.py`, validation reports under `docs/audit/` and `data/audit/`, verify build/test lane
- Nature of the coupling:
  import, path, data, report, build, validation
- Why it matters:
  this is the proof surface later relayout work must still use honestly, and it currently spans code roots, report roots, and compatibility bridging
- Baseline-critical:
  yes
- Likely safe to move later:
  no
- Likely needs shims:
  yes
- Should not move yet:
  yes
- Evidence notes:
  `validation/validation_engine.py`, `tools/validation/tool_run_validation.py`, `tools/xstack/testx_all.py`, `CMakePresets.json`

### `CRA-010 - schema_vs_schemas_split`

- Root/path or subsystem:
  `schema/` versus `schemas/`
- Coupling class:
  `ambiguous_coupling_investigate_later`
- What it is coupled to:
  validation, compatibility narratives, schema-facing tooling, authority-order doctrine
- Nature of the coupling:
  ownership, data, validation, doctrine
- Why it matters:
  the split is explicit governance law, so later relayout work cannot treat the roots as casually interchangeable just because both look schema-like
- Baseline-critical:
  indirect yes
- Likely safe to move later:
  no
- Likely needs shims:
  yes
- Should not move yet:
  yes
- Evidence notes:
  `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `schema/README.md`, `schemas/README.md`

### `CRA-011 - packs_vs_data_packs_split`

- Root/path or subsystem:
  `packs/` versus `data/packs/`
- Coupling class:
  `ambiguous_coupling_investigate_later`
- What it is coupled to:
  pack layout, pack content declarations, compatibility validation, virtual-root discovery, doctrine
- Nature of the coupling:
  ownership, data, runtime, validation
- Why it matters:
  runtime packaging and authored pack-content declarations are intentionally split today, so a later relayout cannot collapse them by convenience
- Baseline-critical:
  indirect yes
- Likely safe to move later:
  no
- Likely needs shims:
  yes
- Should not move yet:
  yes
- Evidence notes:
  `AGENTS.md`, `.agentignore`, `packs/README.md`, inspection of `data/packs/`

### `CRA-012 - profiles_locks_templates_and_registry_default_seam`

- Root/path or subsystem:
  `profiles/`, `locks/`, `data/session_templates/`, `data/registries/`, and the default-bundle seam between authored MVP assets and `bundle.base.lab`
- Coupling class:
  `high_coupling_likely_needs_shim`
- What it is coupled to:
  SessionX create and runner paths, `tools/mvp/runtime_bundle.py`, AppShell virtual roots, release/install projections, baseline recipe docs
- Nature of the coupling:
  data, path, runtime, ownership
- Why it matters:
  these roots are live input roots today, but the repo still has a real default-selection seam between authored baseline assets and registry-driven bundle defaults
- Baseline-critical:
  yes
- Likely safe to move later:
  no
- Likely needs shims:
  yes
- Should not move yet:
  yes
- Evidence notes:
  `tools/xstack/registry_compile/constants.py`, `tools/xstack/session_create.py`, `tools/mvp/runtime_bundle.py`, `data/registries/bundle_profiles.json`

### `CRA-013 - planning_audit_xstack_packet_cluster`

- Root/path or subsystem:
  `docs/planning/`, `docs/repo/`, `docs/xstack/`, `docs/audit/`, `data/planning/`, `data/xstack/`, `data/audit/`
- Coupling class:
  `moderate_coupling_review_required`
- What it is coupled to:
  authority-order doctrine, downstream prompt consumers, machine-readable mirrors, validation outputs, audit evidence, stale path mirrors
- Nature of the coupling:
  doctrine, report, mirror, planning, path
- Why it matters:
  these packet families are not the runtime baseline themselves, but later repo-structure prompts depend on them and stale path vocabulary can create false confidence about relayout safety
- Baseline-critical:
  no for runtime boot, yes for planning discipline
- Likely safe to move later:
  no
- Likely needs shims:
  yes
- Should not move yet:
  no
- Evidence notes:
  `docs/planning/AUTHORITY_ORDER.md`, `docs/repo/REPO_NON_NEGOTIABLES_AND_CURRENT_REALITY.md`, `docs/repo/REPO_TOPOLOGY_PATHS_AND_OWNERSHIP_REALITY_MAP.md`, `docs/audit/ULTRA_REPO_AUDIT_DOC_VS_CODE_MISMATCHES.md`

### `CRA-014 - import_bridge_and_src_alias_compat_layer`

- Root/path or subsystem:
  `tools/import_bridge.py` and the stale `src/...`-path consumers it keeps functioning
- Coupling class:
  `high_coupling_likely_needs_shim`
- What it is coupled to:
  `tools/validation/tool_run_validation.py`, older report paths in `data/audit/install_discovery_report.json`, `data/audit/ui_surface_report.json`, path-equivalence lookups from older restructure locks
- Nature of the coupling:
  import, path, compatibility, report
- Why it matters:
  this bridge masks structural drift by making older `src.` imports and path narratives continue to resolve, so later relayout work must treat it as compatibility scaffolding rather than as proof that old layouts remain canonical
- Baseline-critical:
  no for direct playtest boot, yes for honest validation and drift accounting
- Likely safe to move later:
  no
- Likely needs shims:
  yes
- Should not move yet:
  no
- Evidence notes:
  `tools/import_bridge.py`, `tools/validation/tool_run_validation.py`, `data/audit/install_discovery_report.json`, `data/audit/ui_surface_report.json`

## E. Path-Drift And Doc-Drift Findings

### `DRIFT-001 - server_cli_path_and_readiness_drift`

- Drift type:
  path and readiness drift
- Doc or mirror narrative:
  derived audit docs still describe `src/server/server_main.py` as the authoritative server CLI surface
- Live implementation reality:
  the live file is `server/server_main.py`, and direct invocation is still blocked because `REPO_ROOT_HINT` resolves outside the repo root
- Why it matters:
  this is not just stale naming; it overstates a broken boot path
- Evidence notes:
  `docs/audit/ULTRA_REPO_AUDIT_DOC_VS_CODE_MISMATCHES.md`, `server/server_main.py`

### `DRIFT-002 - legacy_src_prefix_drift_in_docs_and_json_mirrors`

- Drift type:
  structural and naming drift
- Doc or mirror narrative:
  multiple derived docs and machine-readable audit payloads still point at `src/...` paths as if they were the active live tree
- Live implementation reality:
  the active repo uses top-level roots such as `appshell/`, `client/`, `server/`, `launcher/`, `setup/`, and `schema/`
- Why it matters:
  this drift can make a candidate relayout look cheaper than it is because the packet appears already abstracted from the old-to-new root transition
- Evidence notes:
  `docs/audit/ULTRA_REPO_AUDIT_DOC_VS_CODE_MISMATCHES.md`, `data/audit/install_discovery_report.json`, `data/audit/ui_surface_report.json`

### `DRIFT-003 - portability_overclaim_versus_stub_reality`

- Drift type:
  maturity drift
- Doc or mirror narrative:
  older derived docs still imply existing runtime/bootstrap portability across CLI, GUI, and headless entrypoints
- Live implementation reality:
  native launcher and setup GUI/TUI leaves remain explicit stubs, and AppShell mode dispatch still returns stub payloads for TUI and rendered native modes
- Why it matters:
  later topology work must not infer that wrapper roots are mature enough to anchor the canonical path
- Evidence notes:
  `docs/audit/ULTRA_REPO_AUDIT_DOC_VS_CODE_MISMATCHES.md`, `appshell/mode_dispatcher.py`, `appshell/tui_stub.py`, `launcher/gui/launcher_gui_stub.c`, `launcher/tui/launcher_tui_stub.c`

### `DRIFT-004 - runtime_entry_bootstrap_overclaim`

- Drift type:
  behavioral drift
- Doc or mirror narrative:
  `tools/mvp/runtime_entry.py` is still described in some derived narratives as the practical MVP bootstrap surface
- Live implementation reality:
  the audit recorded that local-singleplayer invocation fell back to an AppShell/TUI path rather than a clear playable operator flow, so the file remains transitional rather than canonical
- Why it matters:
  this is a wrapper-versus-canonical confusion point and a relayout hazard if the transitional wrapper is treated as the stable target
- Evidence notes:
  `docs/audit/ULTRA_REPO_AUDIT_DOC_VS_CODE_MISMATCHES.md`, `tools/mvp/runtime_entry.py`, `docs/audit/ULTRA_REPO_AUDIT_PLAYTEST_READINESS.md`

### `DRIFT-005 - session_boot_availability_overclaim`

- Drift type:
  integration drift
- Doc or mirror narrative:
  session-pipeline doctrine and reports often frame session boot as available once a SessionSpec exists
- Live implementation reality:
  the practical boot path is narrower because `tools/xstack/sessionx/runner.py` still forces `repo_root/saves/<save_id>` even if creation used another root
- Why it matters:
  this is a true relayout blocker, not a cosmetic mismatch
- Evidence notes:
  `docs/audit/ULTRA_REPO_AUDIT_DOC_VS_CODE_MISMATCHES.md`, `tools/xstack/session_boot.py`, `tools/xstack/sessionx/runner.py`

### `DRIFT-006 - src_alias_bridge_masks_remaining_structural_drift`

- Drift type:
  compatibility-scaffolding drift
- Doc or mirror narrative:
  some older path consumers continue working well enough that the remaining `src` drift is easy to underestimate
- Live implementation reality:
  `tools/validation/tool_run_validation.py` installs `src` aliases through `tools/import_bridge.py`, and `validation/validation_engine.py` still emits checked paths such as `src/time`
- Why it matters:
  later relayout work must treat the bridge as an active shim that preserves stale consumers, not as evidence that current ownership is already normalized
- Evidence notes:
  `tools/import_bridge.py`, `tools/validation/tool_run_validation.py`, `validation/validation_engine.py`

### `DRIFT-007 - naming_suggests_cleaner_boundaries_than_live_code`

- Drift type:
  ownership and structural drift
- Doc or mirror narrative:
  top-level root names suggest cleaner subsystem boundaries than the implementation actually exposes
- Live implementation reality:
  `launcher/` and `setup/` look canonical but the stronger shells live in `tools/`; `runtime/` looks central but only hosts a thin spawn helper; `validation/` looks isolated but the CLI, report paths, and src-alias bridge live elsewhere; `dist/` looks derived-only but sits on live install-discovery paths
- Why it matters:
  later topology prompts must reason from live couplings, not from tidy names
- Evidence notes:
  `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `runtime/process_spawn.py`, `validation/validation_engine.py`, `tools/import_bridge.py`

### `DRIFT-008 - stale_mirrors_understate_current_top_level_root_reality`

- Drift type:
  understate-implemented-reality drift
- Doc or mirror narrative:
  some machine-readable audit outputs still describe the repo through old `src/...` containers
- Live implementation reality:
  the top-level-root restructure is already real, and the current authoritative topology is what Omega1 recorded
- Why it matters:
  this understates how much current tooling already depends on the new root family and can obscure which compatibility layers must survive a future relayout
- Evidence notes:
  `data/audit/install_discovery_report.json`, `data/audit/ui_surface_report.json`, `docs/repo/REPO_TOPOLOGY_PATHS_AND_OWNERSHIP_REALITY_MAP.md`

## F. Move-Risk Classes

| Move Risk ID | Move risk class | Real meaning |
| --- | --- | --- |
| `safe_to_redesign_conceptually_now` | Safe to redesign conceptually now | Later prompts may redesign the conceptual grouping or target ownership story without creating immediate baseline risk, because the live surface is not the strongest current baseline dependency. |
| `safe_to_move_only_after_shim_design` | Safe to move only after shim design | Later prompts may consider physical movement only if they first design explicit adapters, path shims, mirror regeneration, or import bridges. |
| `do_not_move_before_canonical_playtest_path_hardened` | Do not move before canonical playtest path is hardened | The live surface sits on the current build, session, loopback, validation, or operator path that Omega0 requires to survive. |
| `do_not_redesign_until_later_architecture_clarification` | Do not redesign until later architecture clarification | The root family has unresolved ownership or canonical-versus-derived meaning, so later prompts must defer structural cleanup until the owner story is clarified explicitly. |
| `mixed_defer` | Mixed / defer | The root family contains both easier and riskier portions at once, so later prompts should avoid one blanket move judgment. |

## G. Safe-To-Move, Needs-Shim, And Do-Not-Move-Yet Map

### Safe To Move Later

- Native launcher UI leaves:
  `launcher/gui/`, `launcher/tui/`
  Rationale: they are compiled wrapper leaves, still stub-heavy, and not on the strongest repo-local baseline path.
- Native setup UI leaves:
  `setup/gui/`, `setup/tui/`
  Rationale: same posture as launcher UI leaves; baseline work already prefers the Python/AppShell setup shell.

### Likely Needs Shim

- Release, trust, and install-discovery cluster:
  `release/`, `security/trust/`, `dist/`, manifest and store path conventions
  Rationale: the stronger operator shells already depend on manifest, registry, and store projections.
- Validation and proof cluster:
  `validation/`, `tools/validation/`, `tools/xstack/testx_all.py`, `docs/audit/`, `data/audit/`
  Rationale: relayout would need report-path preservation, mirror regeneration, or validation-path updates.
- Data-location cluster:
  `profiles/`, `locks/`, `data/session_templates/`, `data/registries/`
  Rationale: these are live input roots with many current consumers.
- Compatibility-bridge cluster:
  `tools/import_bridge.py` plus stale `src/...` consumers in reports and some validation flows
  Rationale: old path narratives still survive behind active compatibility scaffolding.

### Do Not Move Yet

- AppShell shell substrate:
  `appshell/`
  Rationale: it is the current canonical repo-local shell/bootstrap owner and sits directly on launcher/setup/server operator continuity.
- Python operator shells:
  `tools/launcher/`, `tools/setup/`
  Rationale: these are the strongest live launcher/setup surfaces today.
- Local authority cluster:
  `client/local_server/`, `runtime/process_spawn.py`, `server/server_main.py`, `server/net/loopback_transport.py`
  Rationale: this is the strongest local singleplayer and loopback-authority path.
- Session pipeline cluster:
  `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/sessionx/creator.py`, `tools/xstack/sessionx/runner.py`
  Rationale: create and boot still depend on fragile current path contracts.
- Operational save and generated-intermediate contracts:
  repo-local `saves/`, `build/registries/`, `build/lockfile.json`
  Rationale: current boot and creation flows still assume these exact locations.

### Mixed / Defer

- `tools/` as a whole
  Rationale: some subroots are baseline-critical while others are wrappers, review tooling, or dist helpers.
- `launcher/` and `setup/` as whole top-level roots
  Rationale: the native UI leaves are easier to move than the compiled wrapper identity or build graph around them.
- `schema/` versus `schemas/`
  Rationale: unresolved ownership split, not a clean move target.
- `packs/` versus `data/packs/`
  Rationale: unresolved authored-content versus runtime-packaging split, not a clean move target.
- `docs/audit/` and `data/audit/`
  Rationale: some leaves are stale mirrors, but others are live validation or proof outputs.

## H. Baseline-Critical Structural Risks

The following are the structural issues most dangerous to the canonical playable-baseline path.

### Highest-Risk Findings

- Startup ambiguity across wrappers and shells:
  too many surfaces still look official at once, including `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `tools/mvp/runtime_entry.py`, `tools/xstack/session_boot.py`, `server/server_main.py`, and compiled verify binaries.
- Repo-root resolution bug:
  `server/server_main.py` still computes the wrong default repo root while `runtime/process_spawn.py` still targets it.
- Session save-root coupling:
  `session_create.py` accepts alternate save roots, but `session_boot.py` plus `sessionx/runner.py` still effectively require canonical repo-local `saves/<save_id>`.
- Supervision instability:
  audit evidence already records exited-child and attach-refusal behavior, so relayout work must not assume the supervisor path is robust enough to absorb churn.
- Wrapper-versus-canonical confusion:
  native launcher/setup wrappers and `runtime_entry.py` still look more canonical than they are, while the stronger live path sits in the Python/AppShell shells and local authority controller.
- Generated-intermediate dependency:
  current session and validation flows still depend on `build/registries/`, `build/lockfile.json`, and report outputs under `docs/audit/` and `data/audit/`.

### Truly Baseline-Critical Rather Than Merely Annoying

- repo-root misresolution in `server/server_main.py`
- save-root disagreement between create and boot flows
- operator-shell ambiguity around launcher/setup/runtime/session entrypoints
- launcher supervision fragility
- dist/manifest and virtual-root discovery ties that the stronger shells already consume

### Annoying But Not First-Baseline Blockers

- stale `src/...` path mirrors in derived docs and JSON reports
- native GUI/TUI stubs when the baseline already prefers Python/AppShell shells
- root names that imply cleaner boundaries than the implementation actually has
- stale portability or maturity language in retro audits

## I. Boundaries On Redesign Freedom

### What Later Design Prompts Are Free To Vary Conceptually

- the eventual target grouping of product roots, tool roots, and support-data roots
- how to document stronger versus weaker entrypoints more clearly
- how to collapse wrapper confusion after the baseline path is stable
- how to converge created versus booted session semantics later
- how to eventually retire stale `src/...` path narratives and bridge scaffolding

### What Later Design Prompts Must Treat As Hard Migration Risks

- any surface on the current session-plus-loopback playable path
- AppShell virtual-root and shell-bootstrap assumptions
- launcher/setup Python shell continuity
- release/trust/install discovery and dist-manifest discovery
- validation/TestX/CTest continuity
- generated `build/registries/` and `build/lockfile.json` intermediates that current flows still expect
- current `saves/<save_id>` boot assumptions
- import-bridge compatibility for remaining `src`-style consumers

### What Later Migration Planning Must Assume Needs Protection

- `appshell/`
- `tools/launcher/` and `tools/setup/`
- `client/local_server/`, `runtime/process_spawn.py`, `server/server_main.py`, `server/net/loopback_transport.py`
- `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/sessionx/creator.py`, `tools/xstack/sessionx/runner.py`
- `profiles/`, `locks/`, `data/session_templates/`, `data/registries/`
- `release/`, `security/trust/`, `dist/`, and manifest/registry path conventions
- validation report paths and machine-readable mirrors used by the repo itself

## J. Anti-Patterns And Forbidden Shapes

- choosing a target topology based only on aesthetics or top-level cleanliness
- assuming separate directories imply real subsystem isolation
- moving baseline-critical wrappers or shells before a stronger canonical replacement exists
- redesigning around stale docs or stale `src/...` mirrors instead of live code
- treating repo-root math or save-root drift as minor path cleanup when they already block boot flows
- assuming generated roots are irrelevant because they are non-canonical, even when live flows still consume them
- treating the import bridge as proof that old layouts are still authoritative
- flattening safe-to-move, needs-shim, and do-not-move-yet into one generic migration bucket

## K. Stability And Evolution

- Stability class:
  stable until later prompts record new evidence that changes the coupling or blocker posture materially
- Later prompts expected to consume this artifact:
  topology-option generation, preferred-target comparison, shim-strategy design, migration-sequencing design, and ownership-reconciliation prompts in this repo-structure series
- What must not change without explicit follow-up:
  the coupling-class meanings, the baseline-critical risk findings, the drift findings that identify stale versus live narratives, and the safe-to-move versus needs-shim versus do-not-move-yet distinctions
