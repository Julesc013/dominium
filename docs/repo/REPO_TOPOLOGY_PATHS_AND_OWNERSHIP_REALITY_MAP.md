Status: DERIVED
Last Reviewed: 2026-04-08
Supersedes: none
Superseded By: none
Stability: stable
Series Scope: repo-structure discovery and design
Series Role: authoritative topology, path-contract, and ownership reality map for later repo-structure discovery, design, migration-planning, and decision prompts; downstream of stronger canon, the Omega0 constraint packet, audit evidence, and live implementation evidence
Replacement Target: later explicit repo-structure follow-up after approved topology design or new playable-baseline evidence
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `.agentignore`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`, `docs/planning/GATES_AND_PROOFS.md`, `docs/planning/MERGED_PROGRAM_STATE.md`, `docs/repo/REPO_NON_NEGOTIABLES_AND_CURRENT_REALITY.md`, `data/repo/repo_non_negotiables_and_current_reality.json`, `docs/planning/CHECKPOINT_C_ZETA_MEGA_VALIDATION_AND_CLOSURE.md`, `data/planning/checkpoints/checkpoint_c_zeta_mega_validation_and_closure.json`, `docs/planning/NEXT_EXECUTION_ORDER_POST_ZETA.md`, `data/planning/next_execution_order_post_zeta.json`, `docs/audit/ULTRA_REPO_AUDIT_EXECUTIVE_SUMMARY.md`, `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`, `docs/audit/ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_PLAYTEST_READINESS.md`, `docs/audit/ULTRA_REPO_AUDIT_GAPS_AND_TODOS.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`, `docs/audit/ULTRA_REPO_AUDIT_BUILD_RUN_TEST_MATRIX.md`, `docs/audit/ULTRA_REPO_AUDIT_WIRING_MAP.md`, `data/audit/ultra_repo_audit_system_inventory.json`, `data/audit/ultra_repo_audit_entrypoints.json`, `data/audit/ultra_repo_audit_product_assembly_plan.json`, `data/audit/ultra_repo_audit_gap_ledger.json`, `data/audit/ultra_repo_audit_build_run_test_matrix.json`, `data/audit/ultra_repo_audit_wiring_map.json`, `docs/xstack/CHECKPOINT_C_XSTACK_AIDE_CLOSURE.md`, `data/xstack/checkpoint_c_xstack_aide_closure.json`, `docs/xstack/NEXT_EXECUTION_ORDER_POST_XSTACK_AIDE.md`, `data/xstack/next_execution_order_post_xstack_aide.json`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`, `docs/xstack/XSTACK_TO_AIDE_EXTRACTION_MAP.md`, `CMakePresets.json`, `appshell/command_registry.py`, `appshell/paths/virtual_paths.py`, `data/registries/virtual_root_registry.json`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `tools/validation/tool_run_validation.py`, `tools/xstack/testx_all.py`, `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/sessionx/creator.py`, `tools/xstack/sessionx/runner.py`, `tools/mvp/runtime_entry.py`, `tools/mvp/runtime_bundle.py`, `tools/xstack/registry_compile/constants.py`, `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, `server/server_main.py`, `server/net/loopback_transport.py`, `net/policies/policy_server_authoritative.py`, `release/release_manifest_engine.py`, `release/component_graph_resolver.py`, `release/update_resolver.py`, `security/trust/trust_verifier.py`, `profiles/bundles/bundle.mvp_default.json`, `locks/pack_lock.mvp_default.json`, `data/session_templates/session.mvp_default.json`, `data/registries/bundle_profiles.json`, `data/registries/session_defaults.json`, `schema/README.md`, `schemas/README.md`, `packs/README.md`, `repo/release_policy.toml`

# Repo Topology, Paths, And Ownership Reality Map

## A. Purpose And Scope

This artifact maps the repository as it actually exists now so later repo-structure prompts can compare candidate topologies against live ownership, path, and entrypoint constraints instead of naming aesthetics.

It exists because the repo already has a frozen non-negotiable packet in Omega0, but later design prompts still need a concrete answer to a different question:

- what the real important roots and clusters are
- what each actually owns
- which roots are canonical, derived, mixed, transitional, wrapper-only, or support-data
- which current path contracts and entrypoint dependencies would break if a relayout ignored them

Its relationship to Omega0 is strict:

- Omega0 freezes what must not break
- this artifact maps where that current reality lives and how it is coupled

Its relationship to the playable-baseline priority is also strict:

- baseline-critical roots and path contracts are called out explicitly
- no topology interpretation in this artifact is allowed to hide the current repo-local session creation plus loopback-authority baseline path
- this artifact does not choose the target topology, migration phases, shim plan, or root renames

For later repo-structure work, the direct answers are:

- What are the real important roots and clusters in the repo:
  the roots and clusters listed in Sections B and D.
- What does each actually own:
  the ownership ledger in Section D.
- What path contracts and assumptions currently exist:
  Section E.
- Which roots and paths are baseline-critical:
  Sections D, E, and F.
- What is canonical vs derived vs mixed right now:
  Section G.
- What prompt this enables next:
  a coupling, drift, and redesign-risk analysis prompt that evaluates where current ownership splits and path contracts make future topology changes dangerous or cheap.

This is a reality map, not a topology decision.

## B. Topology Reality Summary

The repo has many top-level roots, but later topology work should distinguish between roots that matter to the current playable-baseline path and roots that are merely present.

### Major Top-Level Roots

- Product and runtime roots:
  `client/`, `server/`, `appshell/`, `launcher/`, `setup/`, `runtime/`, `net/`
- Tooling and validation roots:
  `tools/`, `validation/`, `tests/`
- Content, config, and contract roots:
  `packs/`, `profiles/`, `locks/`, `data/`, `schema/`, `schemas/`
- Doctrine, planning, and evidence roots:
  `docs/`, `specs/`, `repo/`
- Large authored code clusters outside the immediate launcher/playtest path:
  `engine/`, `game/`, and many domain roots such as `astro/`, `control/`, `logic/`, `mobility/`, `worldgen/`, and related module trees
- Derived or generated output roots:
  `build/`, `dist/`, `out/`, `.xstack_cache/`, `artifacts/`, `run_meta/`, `tmp/`, `saves/`

### Major Second-Level Clusters That Matter To Topology Decisions

- `client/local_server/` is the current repo-local singleplayer orchestration cluster.
- `server/net/`, `server/runtime/`, and `server/persistence/` are the current authoritative runtime cluster behind the local baseline.
- `tools/launcher/`, `tools/setup/`, `tools/xstack/`, and `tools/validation/` are the tool subroots that materially affect build, session, validation, and operator flows.
- `profiles/bundles/`, `locks/`, `data/session_templates/`, and `data/registries/` are the authored and machine-readable data roots that current flows consume directly.
- `docs/planning/`, `docs/audit/`, `docs/repo/`, `docs/xstack/`, `specs/reality/`, `data/planning/`, `data/audit/`, and `data/xstack/` are the doctrine and evidence cluster that later design prompts must consume instead of rediscovering.

### Roots Central To Current Product Flows

- `client/`
- `server/`
- `appshell/`
- `tools/launcher/`
- `tools/setup/`
- `tools/xstack/`
- `tools/validation/`
- `validation/`
- `profiles/`
- `locks/`
- `data/session_templates/`
- `data/registries/`
- `packs/`
- `runtime/`
- `release/`
- `security/trust/`
- `dist/`
- `saves/`

### Support-Only Or Derived Roots

- `build/`
- `out/`
- `.xstack_cache/`
- `artifacts/`
- `run_meta/`
- large parts of `dist/` once assembled
- `data/audit/`
- many generated report leaves under `docs/audit/`

## C. Ownership Classes

| Class ID | Class | Real meaning |
| --- | --- | --- |
| `authoritative_canonical_root` | Authoritative / canonical root | A root that currently functions as the safest canonical owner of a repo-level domain of truth or behavior. |
| `authoritative_bounded_domain_root` | Authoritative but bounded-domain root | A root that is authoritative for a specific implementation, data, or policy area, but is not a whole-repo owner. |
| `derived_generated_root` | Derived / generated root | A root whose contents are produced, mirrored, materialized, or report-only rather than authored canon. |
| `mixed_ambiguous_root` | Mixed / ambiguous root | A root that contains real value but mixes roles, hosts overlapping responsibilities, or should not be treated as a clean owner without more design work. |
| `transitional_legacy_root` | Transitional / legacy root | A root that still participates in live flows or compatibility but is explicitly not the settled long-term owner. |
| `wrapper_only_root` | Wrapper-only root | A root that exposes launch, install, or operator surfaces but is currently thinner than the stronger implementation it wraps. |
| `support_data_root` | Support-data root | A data root that is authoritative for a bounded machine-readable payload family, but should not be mistaken for doctrine or for a broader code owner. |

## D. Concrete Topology And Ownership Ledger

### `TOP-001 - engine_game_domain_cluster`

- Root/path:
  `engine/`, `game/`, and major authored domain module roots
- Actual purpose:
  hosts the bulk of authored simulation, runtime, and domain logic outside the launcher/setup/session shell layer
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  primary authored gameplay, engine, simulation, and domain-module implementation bodies
- What it appears not to own:
  operator shell policy, release/install control-plane policy, validation pipeline ownership, or repo topology governance
- Product-critical now:
  yes
- Baseline-critical now:
  indirect yes
- Safe to treat as canonical:
  yes for authored simulation and domain code, no for repo-level orchestration
- Major dependencies or path couplings:
  compiled through the verify preset family and consumed by client/server/test surfaces
- Evidence notes:
  `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`, `CMakePresets.json`

### `TOP-002 - appshell_root`

- Root/path:
  `appshell/`
- Actual purpose:
  repo-rooted operator shell substrate for commands, IPC, logging, supervisor behavior, and virtual path resolution
- Ownership class:
  `authoritative_canonical_root`
- What it appears to own:
  virtual-root discovery, command registry loading, TUI panel wiring, shell diagnostics, and supervision helpers used by repo-local launcher/setup/server surfaces
- What it appears not to own:
  release policy, core client/server product logic, or session materialization semantics
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  yes for current repo-local shell/bootstrap behavior
- Major dependencies or path couplings:
  `data/registries/command_registry.json`, `data/registries/tui_panel_registry.json`, `data/registries/virtual_root_registry.json`, `dist/`, `packs/`, `profiles/`, `locks/`, `saves/`, `runtime/`
- Evidence notes:
  `appshell/command_registry.py`, `appshell/paths/virtual_paths.py`, `data/registries/virtual_root_registry.json`

### `TOP-003 - client_root`

- Root/path:
  `client/`
- Actual purpose:
  owns the client binary and client-side presentation, input, local-server bridge, and application wiring
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  client application runtime, input, presentation layers, and the local singleplayer controller cluster
- What it appears not to own:
  server authority semantics, release/update policy, or repo-wide virtual path policy
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  yes for client implementation
- Major dependencies or path couplings:
  verify build lane, `runtime/process_spawn.py`, `server/net/loopback_transport.py`, `build/client/local_singleplayer/<save_id>/diag/`
- Evidence notes:
  `client/CMakeLists.txt`, `client/local_server/local_server_controller.py`, `docs/audit/ULTRA_REPO_AUDIT_WIRING_MAP.md`

### `TOP-004 - client_local_server_cluster`

- Root/path:
  `client/local_server/`
- Actual purpose:
  orchestrates repo-local singleplayer by creating or reusing session data, spawning the Python server, and attaching loopback transport
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  local-only client to server orchestration for the current baseline path
- What it appears not to own:
  general multiplayer transport, compiled launcher ownership, or release manifest policy
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  yes for the current local loopback path
- Major dependencies or path couplings:
  `runtime/process_spawn.py`, `server/server_main.py`, `server/net/loopback_transport.py`, `tools/xstack/session_create.py`, `saves/<save_id>/`
- Evidence notes:
  `client/local_server/local_server_controller.py`, `docs/audit/ULTRA_REPO_AUDIT_PRODUCT_ASSEMBLY_PLAN.md`

### `TOP-005 - server_root`

- Root/path:
  `server/`
- Actual purpose:
  owns authoritative runtime, persistence, shard, and server-side net integration
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  authoritative server runtime logic, server boot support, persistence, server tests, and loopback-capable server integration
- What it appears not to own:
  repo-root path law, install/update manifests, or client-side local orchestration
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  yes for server implementation, no for the public Python startup path without caveat
- Major dependencies or path couplings:
  `server/server_main.py`, `runtime/process_spawn.py`, `server/net/loopback_transport.py`, verify binaries, `saves/<save_id>/`
- Evidence notes:
  `server/CMakeLists.txt`, `server/server_main.py`, `server/net/loopback_transport.py`

### `TOP-006 - launcher_root`

- Root/path:
  `launcher/`
- Actual purpose:
  compiled launcher root with CLI, core, GUI, include, and TUI surfaces
- Ownership class:
  `wrapper_only_root`
- What it appears to own:
  native launcher wrapper surfaces and compatibility shell packaging
- What it appears not to own:
  the strongest repo-local operator truth or the most complete launcher behavior path
- Product-critical now:
  likely
- Baseline-critical now:
  no
- Safe to treat as canonical:
  no
- Major dependencies or path couplings:
  verify build lane, shared include surfaces, AppShell-adjacent concepts, but current stronger shell path is under `tools/launcher/`
- Evidence notes:
  `launcher/CMakeLists.txt`, `docs/audit/ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md`, `docs/audit/ULTRA_REPO_AUDIT_REUSE_AND_CONSOLIDATION_PLAN.md`

### `TOP-007 - setup_root`

- Root/path:
  `setup/`
- Actual purpose:
  compiled setup root with CLI, core, GUI, include, packages, and TUI surfaces
- Ownership class:
  `wrapper_only_root`
- What it appears to own:
  native setup wrapper surfaces and package/install-facing compiled code
- What it appears not to own:
  the strongest repo-local setup truth, which currently lives in the Python/AppShell shell
- Product-critical now:
  likely
- Baseline-critical now:
  no
- Safe to treat as canonical:
  no
- Major dependencies or path couplings:
  verify build lane, install packaging assets, AppShell-adjacent concepts, but stronger repo-local flow is `tools/setup/setup_cli.py`
- Evidence notes:
  `setup/CMakeLists.txt`, `docs/audit/ULTRA_REPO_AUDIT_ENTRYPOINTS_AND_RUNPATHS.md`

### `TOP-008 - release_root`

- Root/path:
  `release/`
- Actual purpose:
  release manifest, component graph, install-profile, and update resolution logic
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  release-manifest semantics, component graph resolution, install discovery, and store/dist-oriented install payload resolution
- What it appears not to own:
  gameplay code, session boot semantics, or baseline shell orchestration
- Product-critical now:
  yes
- Baseline-critical now:
  yes because launcher/setup shells and dist discovery depend on it
- Safe to treat as canonical:
  yes for release and install logic
- Major dependencies or path couplings:
  `manifests/release_manifest.json`, `manifests/release_index.json`, `data/registries/component_graph_registry.json`, `data/registries/install_profile_registry.json`, `store/profiles/`, `store/locks/`, `dist/`
- Evidence notes:
  `release/release_manifest_engine.py`, `release/component_graph_resolver.py`, `release/update_resolver.py`

### `TOP-009 - security_trust_root`

- Root/path:
  `security/trust/`
- Actual purpose:
  trust verification and root/policy registry resolution
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  trust policy resolution, trust root loading, and release/install trust checks
- What it appears not to own:
  broader release topology or session orchestration
- Product-critical now:
  yes
- Baseline-critical now:
  indirect yes
- Safe to treat as canonical:
  yes for trust verification
- Major dependencies or path couplings:
  `data/registries/trust_policy_registry.json`, `data/registries/trust_root_registry.json`, `manifests/trust_root_registry.local.json`
- Evidence notes:
  `security/trust/trust_verifier.py`

### `TOP-010 - runtime_root`

- Root/path:
  `runtime/`
- Actual purpose:
  thin runtime helper root, currently dominated by process-spawn support
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  bounded helper responsibilities such as server process launch specifications
- What it appears not to own:
  the full runtime orchestration layer or session materialization
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  yes only for the thin helper scope it actually implements
- Major dependencies or path couplings:
  `server/server_main.py`, repo-root cwd assumptions, local-server controller use
- Evidence notes:
  `runtime/process_spawn.py`, `docs/audit/ULTRA_REPO_AUDIT_WIRING_MAP.md`

### `TOP-011 - net_root`

- Root/path:
  `net/`
- Actual purpose:
  generic network policy, transport, testing, and anti-cheat substrate
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  generic network-policy and transport-layer substrate that server-side runtime consumes
- What it appears not to own:
  the full authoritative server runtime or the loopback transport implementation, which lives under `server/net/`
- Product-critical now:
  yes
- Baseline-critical now:
  indirect yes
- Safe to treat as canonical:
  yes with bounded-domain caveat
- Major dependencies or path couplings:
  entangled with `server/net/`, consumed by authority policy code and runtime wiring
- Evidence notes:
  `net/policies/policy_server_authoritative.py`, `docs/audit/ULTRA_REPO_AUDIT_WIRING_MAP.md`

### `TOP-012 - validation_root`

- Root/path:
  `validation/`
- Actual purpose:
  owns the validation engine and the canonical report-writing logic
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  validation inventory, report generation, and legacy validation surface reconciliation
- What it appears not to own:
  the CLI wrapper, which lives in `tools/validation/`, or repo doctrine
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  yes for validation-engine logic
- Major dependencies or path couplings:
  `data/registries/validation_suite_registry.json`, `docs/audit/VALIDATION_INVENTORY.md`, `docs/audit/VALIDATION_REPORT_<PROFILE>.md`, `data/audit/validation_report_<PROFILE>.json`, `docs/audit/VALIDATION_UNIFY_FINAL.md`
- Evidence notes:
  `validation/validation_engine.py`, `tools/validation/tool_run_validation.py`

### `TOP-013 - tools_root`

- Root/path:
  `tools/`
- Actual purpose:
  umbrella tooling root containing canonical baseline-critical tool subroots plus many unrelated or broader admin, audit, dist, and review tools
- Ownership class:
  `mixed_ambiguous_root`
- What it appears to own:
  many tool entrypoints, wrappers, validation helpers, dist helpers, xstack utilities, and review tools
- What it appears not to own:
  a single clean semantic or product boundary
- Product-critical now:
  yes
- Baseline-critical now:
  yes because several required entrypoints live here
- Safe to treat as canonical:
  no at the top-level umbrella
- Major dependencies or path couplings:
  `tools/launcher/`, `tools/setup/`, `tools/xstack/`, `tools/validation/`, `tools/mvp/`, `tools/dist/`, many repo-root hints and relative-path contracts
- Evidence notes:
  `tools/CMakeLists.txt`, `docs/audit/ULTRA_REPO_AUDIT_SYSTEM_INVENTORY.md`

### `TOP-014 - tools_baseline_shell_cluster`

- Root/path:
  `tools/launcher/`, `tools/setup/`, `tools/xstack/`, `tools/validation/`, `tools/mvp/`
- Actual purpose:
  hosts the tool entrypoints that currently define the live build, validation, session, and transitional runtime shell flows
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  launcher/setup Python shells, validation CLI, SessionX create and boot CLI, TestX harness, and the transitional MVP runtime wrapper
- What it appears not to own:
  the compiled launcher/setup roots, full server runtime ownership, or final settled public playtest API
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  yes for the specific entrypoints it actually hosts, no as a claim that `tools/` itself is a clean top-level owner
- Major dependencies or path couplings:
  repo-root hints, `appshell/`, `validation/`, `build/registries/`, `build/lockfile.json`, `profiles/`, `locks/`, `data/session_templates/`, `saves/`, `dist/`
- Evidence notes:
  `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `tools/xstack/session_create.py`, `tools/xstack/session_boot.py`, `tools/xstack/testx_all.py`, `tools/mvp/runtime_entry.py`

### `TOP-015 - packs_root`

- Root/path:
  `packs/`
- Actual purpose:
  canonical runtime packaging, activation, compatibility, distribution-descriptor, and pack-layout root
- Ownership class:
  `authoritative_canonical_root`
- What it appears to own:
  on-disk runtime pack layout, compatibility-facing pack metadata, and pack family organization
- What it appears not to own:
  all authored pack content declarations, which still also live under `data/packs/`
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  yes with the AGENTS caveat that `data/packs/` remains authoritative within authored pack-content and declaration scope
- Major dependencies or path couplings:
  virtual-root pack discovery, pack compatibility validation, session materialization inputs, dist/store pack resolution
- Evidence notes:
  `packs/README.md`, `appshell/paths/virtual_paths.py`, `AGENTS.md`

### `TOP-016 - data_packs_root`

- Root/path:
  `data/packs/`
- Actual purpose:
  authored pack-content and declaration root that remains authoritative within its bounded scope while still being transitional for single-root convergence
- Ownership class:
  `transitional_legacy_root`
- What it appears to own:
  authored pack content and declaration payloads
- What it appears not to own:
  the settled single runtime packaging root for future convergence
- Product-critical now:
  yes
- Baseline-critical now:
  indirect yes
- Safe to treat as canonical:
  only for authored pack-content and declaration scope
- Major dependencies or path couplings:
  pack manifests, content folders, pack tooling, convergence cautions from governance docs
- Evidence notes:
  `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, inspection of `data/packs/`

### `TOP-017 - profiles_root`

- Root/path:
  `profiles/`
- Actual purpose:
  authored profile root, currently dominated by `profiles/bundles/`
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  authored profile bundle declarations used by runtime and baseline tooling
- What it appears not to own:
  generated installed profile copies under `store/` or registry-compiled bundle ids
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  yes for authored profile bundles
- Major dependencies or path couplings:
  `profiles/bundles/bundle.mvp_default.json`, AppShell virtual roots, release/install store projections
- Evidence notes:
  `profiles/bundles/bundle.mvp_default.json`, `appshell/paths/virtual_paths.py`, `tools/mvp/runtime_bundle.py`

### `TOP-018 - locks_root`

- Root/path:
  `locks/`
- Actual purpose:
  authored pack-lock root for baseline and runtime configuration
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  authored lock declarations such as `pack_lock.mvp_default.json`
- What it appears not to own:
  compiled lockfile outputs under `build/` or installed lock copies under `store/`
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  yes for authored locks
- Major dependencies or path couplings:
  `locks/pack_lock.mvp_default.json`, AppShell virtual roots, release/install store projections, SessionX create and boot flows
- Evidence notes:
  `locks/pack_lock.mvp_default.json`, `tools/mvp/runtime_bundle.py`, `release/update_resolver.py`

### `TOP-019 - data_session_templates_root`

- Root/path:
  `data/session_templates/`
- Actual purpose:
  authored session-template support-data root
- Ownership class:
  `support_data_root`
- What it appears to own:
  session template payloads such as `session.mvp_default`
- What it appears not to own:
  runtime save materialization outputs or the whole session orchestration layer
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  yes for authored session-template data
- Major dependencies or path couplings:
  `data/session_templates/session.mvp_default.json`, session materialization flows, SessionX tooling, baseline recipe docs
- Evidence notes:
  `data/session_templates/session.mvp_default.json`, `tools/mvp/runtime_bundle.py`

### `TOP-020 - data_registries_root`

- Root/path:
  `data/registries/`
- Actual purpose:
  machine-readable registry root consumed by AppShell, release, trust, validation, and parts of runtime/session tooling
- Ownership class:
  `support_data_root`
- What it appears to own:
  registry payloads for commands, panels, virtual roots, trust, install, component graphs, validation suites, session defaults, and bundle profiles
- What it appears not to own:
  doctrine, broader product code, or compiled registry outputs under `build/registries/`
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  yes for registry data families that live there
- Major dependencies or path couplings:
  `appshell/command_registry.py`, `appshell/paths/virtual_paths.py`, `release/component_graph_resolver.py`, `security/trust/trust_verifier.py`, `validation/validation_engine.py`
- Evidence notes:
  `data/registries/virtual_root_registry.json`, `data/registries/bundle_profiles.json`, `data/registries/session_defaults.json`

### `TOP-021 - schema_root`

- Root/path:
  `schema/`
- Actual purpose:
  authoritative semantic and contract-law root
- Ownership class:
  `authoritative_canonical_root`
- What it appears to own:
  contract law, semantic schemas, compatibility identity and migration meaning
- What it appears not to own:
  validator-facing projection copies or report mirrors
- Product-critical now:
  yes
- Baseline-critical now:
  indirect yes
- Safe to treat as canonical:
  yes
- Major dependencies or path couplings:
  contract-facing docs, compatibility meaning, validation consumers
- Evidence notes:
  `schema/README.md`, `AGENTS.md`

### `TOP-022 - schemas_root`

- Root/path:
  `schemas/`
- Actual purpose:
  validator-facing JSON schema and example projection tree
- Ownership class:
  `mixed_ambiguous_root`
- What it appears to own:
  projection schemas and examples used by tooling and validation consumers
- What it appears not to own:
  canonical semantic law
- Product-critical now:
  yes
- Baseline-critical now:
  indirect yes
- Safe to treat as canonical:
  no
- Major dependencies or path couplings:
  validation scans, compat tooling, schema-facing consumers
- Evidence notes:
  `schemas/README.md`, `AGENTS.md`, `validation/validation_engine.py`

### `TOP-023 - docs_specs_cluster`

- Root/path:
  `docs/` and `specs/reality/`
- Actual purpose:
  doctrine, planning, audit, repo-series, xstack closure, and semantic-specification root cluster
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  canon, planning law, audit packet, xstack closure packet, repo-series artifacts, and semantic specifications
- What it appears not to own:
  live implementation behavior where code disagrees
- Product-critical now:
  yes
- Baseline-critical now:
  yes because later topology work must remain downstream of these packets
- Safe to treat as canonical:
  yes for doctrine and planning within authority order, no as a replacement for live code evidence
- Major dependencies or path couplings:
  `docs/planning/`, `docs/audit/`, `docs/repo/`, `docs/xstack/`, `specs/reality/`
- Evidence notes:
  `docs/planning/AUTHORITY_ORDER.md`, `docs/repo/REPO_NON_NEGOTIABLES_AND_CURRENT_REALITY.md`, `docs/xstack/CODEX_REPO_OPERATING_CONTRACT.md`

### `TOP-024 - data_planning_audit_xstack_cluster`

- Root/path:
  `data/planning/`, `data/audit/`, `data/xstack/`
- Actual purpose:
  machine-readable mirrors and evidence payloads for planning, audit, and xstack packets
- Ownership class:
  `support_data_root`
- What it appears to own:
  JSON mirrors, checkpoint payloads, and report artifacts with intact provenance
- What it appears not to own:
  higher-order doctrine or live implementation ownership
- Product-critical now:
  yes
- Baseline-critical now:
  yes for machine-readable planning and audit consumption
- Safe to treat as canonical:
  only as derived evidence or mirror data in the authority slots explicitly assigned to them
- Major dependencies or path couplings:
  downstream planning prompts, audit consumption, xstack closure packet parsing
- Evidence notes:
  `docs/planning/AUTHORITY_ORDER.md`, `docs/repo/REPO_NON_NEGOTIABLES_AND_CURRENT_REALITY.md`

### `TOP-025 - repo_policy_root`

- Root/path:
  `repo/` plus root-level control files such as `AGENTS.md`, `.agentignore`, and `CMakePresets.json`
- Actual purpose:
  repo policy, release policy, canon-state markers, and root-level execution controls
- Ownership class:
  `authoritative_bounded_domain_root`
- What it appears to own:
  release policy, canon-state metadata, repo-series governance anchors, and the verify preset family
- What it appears not to own:
  product runtime implementation or session materialization logic
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  yes for the specific policy and root-control scope it actually hosts
- Major dependencies or path couplings:
  `repo/release_policy.toml`, `repo/canon_state.json`, `CMakePresets.json`
- Evidence notes:
  `repo/release_policy.toml`, `CMakePresets.json`, `AGENTS.md`

### `TOP-026 - dist_root`

- Root/path:
  `dist/`
- Actual purpose:
  assembled distribution tree and install-style payload staging root
- Ownership class:
  `derived_generated_root`
- What it appears to own:
  assembled runtime distribution leaves, manifests, staged bundles, staged locks, and install-style layouts
- What it appears not to own:
  authored canonical truth
- Product-critical now:
  yes operationally
- Baseline-critical now:
  yes because launcher/setup shells and AppShell virtual paths discover it
- Safe to treat as canonical:
  no
- Major dependencies or path couplings:
  `dist/manifests/release_manifest.json`, `dist/packs/`, `dist/profiles/`, `dist/locks/`, AppShell install/store search roots
- Evidence notes:
  `appshell/paths/virtual_paths.py`, `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, `release/release_manifest_engine.py`

### `TOP-027 - saves_root`

- Root/path:
  `saves/`
- Actual purpose:
  runtime materialization root for session saves and bootable session specs
- Ownership class:
  `mixed_ambiguous_root`
- What it appears to own:
  live save directories, session specs, and runtime artifacts for the current repo-local baseline
- What it appears not to own:
  authored source-of-truth configuration
- Product-critical now:
  yes
- Baseline-critical now:
  yes
- Safe to treat as canonical:
  only as the current operational save-root assumption, not as authored canon
- Major dependencies or path couplings:
  `tools/xstack/session_boot.py`, `tools/xstack/sessionx/runner.py`, `client/local_server/local_server_controller.py`, AppShell virtual paths
- Evidence notes:
  `tools/xstack/session_boot.py`, `tools/xstack/sessionx/runner.py`, `appshell/paths/virtual_paths.py`

### `TOP-028 - generated_output_cluster`

- Root/path:
  `build/`, `out/`, `.xstack_cache/`, `artifacts/`, `run_meta/`, `tmp/`
- Actual purpose:
  generated work roots, build outputs, caches, reports, and transient artifact materialization
- Ownership class:
  `derived_generated_root`
- What it appears to own:
  compiled outputs, generated registries, generated lockfiles, cache state, run metadata, and report bundles
- What it appears not to own:
  authored doctrine, product canon, or stable ownership truth
- Product-critical now:
  yes operationally
- Baseline-critical now:
  yes because verify outputs, generated registries, generated lockfile, and run metadata are consumed by current flows
- Safe to treat as canonical:
  no
- Major dependencies or path couplings:
  `out/build/vs2026/verify/`, `build/registries/`, `build/lockfile.json`, `run_meta/`, `.xstack_cache/`
- Evidence notes:
  `CMakePresets.json`, `tools/xstack/sessionx/creator.py`, `tools/xstack/sessionx/runner.py`

## E. Path-Contract Map

The following path contracts exist now and matter to later relayout work.

### Repo-Root Assumptions

- `PATH-001 - repo_root_tools_shell_hint`
  Most Python tool entrypoints under `tools/` compute repo root with `../..` from the script directory. This is live in `tools/launcher/launch.py`, `tools/setup/setup_cli.py`, and `tools/validation/tool_run_validation.py`.
  Baseline-critical: yes.

- `PATH-002 - repo_root_nested_xstack_hints`
  Nested SessionX modules under `tools/xstack/` use deeper relative repo-root math and expect to resolve generated build outputs and save directories from repo root.
  Baseline-critical: yes.

- `PATH-003 - repo_root_server_main_bug`
  `server/server_main.py` computes `REPO_ROOT_HINT` by walking two levels up from `server/`, which escapes the repo root and is explicitly a live blocker.
  Baseline-critical: yes.

### Entrypoint And Output Layout Assumptions

- `PATH-004 - verify_out_tree_contract`
  The compiled verify lane expects `CMakePresets.json` to configure and build into `out/build/vs2026/<preset>/`, with the audited canonical tree centered on `out/build/vs2026/verify/`.
  Baseline-critical: yes.

- `PATH-005 - client_server_binary_contract`
  The verify build path produces the client and server binaries used by the audited compiled lane, even though the current repo-local shell path leans more heavily on Python/AppShell surfaces.
  Baseline-critical: yes.

### Session Save-Root Assumptions

- `PATH-006 - session_spec_under_saves_contract`
  `tools/xstack/session_boot.py` still documents and expects boot specs at `saves/<save_id>/session_spec.json`.
  Baseline-critical: yes.

- `PATH-007 - session_runner_hardcoded_save_root`
  `tools/xstack/sessionx/runner.py` still resolves `save_dir = os.path.join(repo_root, "saves", save_id)`, which means alternate save roots are not honored end to end.
  Baseline-critical: yes.

- `PATH-008 - local_controller_save_contract`
  `client/local_server/local_server_controller.py` and related local-loopback code assume repo-local save materialization and emit diagnostics under `build/client/local_singleplayer/<save_id>/diag/`.
  Baseline-critical: yes.

### Profile, Bundle, Lock, Template, And Registry Location Assumptions

- `PATH-009 - authored_mvp_asset_locations`
  The authored baseline asset trio is physically located at `profiles/bundles/bundle.mvp_default.json`, `locks/pack_lock.mvp_default.json`, and `data/session_templates/session.mvp_default.json`.
  Baseline-critical: yes.

- `PATH-010 - registry_vs_authored_bundle_seam`
  The authored baseline asset trio coexists with registry-driven defaults in `data/registries/bundle_profiles.json` and a SessionX default bundle id of `bundle.base.lab` from `tools/xstack/registry_compile/constants.py`.
  Baseline-critical: yes because later design must not hide the seam.

- `PATH-011 - build_registry_and_lockfile_outputs`
  SessionX create and runner paths currently depend on `build/registries/` and `build/lockfile.json` as generated intermediates.
  Baseline-critical: yes.

- `PATH-012 - virtual_root_registry_defaults`
  `appshell/paths/virtual_paths.py` and `data/registries/virtual_root_registry.json` encode default search locations for `packs`, `profiles`, `locks`, `saves`, `runtime`, and store/install-style fallbacks.
  Baseline-critical: yes.

### Manifest, Store, And Dist Assumptions

- `PATH-013 - dist_release_manifest_contract`
  The repo-local launcher/setup shells and release logic expect release manifests at `manifests/release_manifest.json`, with the repo-local install/discovery path commonly resolving via `dist/manifests/release_manifest.json`.
  Baseline-critical: yes.

- `PATH-014 - store_projection_contract`
  Release/update logic also expects installed or projected payloads such as `store/profiles/bundles/bundle.mvp_default.json` and `store/locks/pack_lock.mvp_default.json`.
  Baseline-critical: no for the immediate playable baseline, yes for release/install continuity.

### Schema And Pack Split Assumptions

- `PATH-015 - schema_vs_schemas_split`
  `schema/` remains canonical semantic law while `schemas/` remains the validator-facing projection and example tree.
  Baseline-critical: indirect yes.

- `PATH-016 - packs_vs_data_packs_split`
  `packs/` remains canonical for runtime packaging, activation, compatibility, and distribution-descriptor scope, while `data/packs/` remains authoritative within authored pack-content and declaration scope.
  Baseline-critical: indirect yes.

## F. Entrypoint Dependency Map

### `ENTRY-001 - verify_configure_build_test`

- Entrypoint:
  `cmake --preset verify`, `cmake --build --preset verify`, `ctest --preset verify`
- Depends on:
  `CMakePresets.json`, root build graph, `client/`, `server/`, `launcher/`, `setup/`, major authored code roots, and `out/build/vs2026/verify/`
- Critical path contracts:
  `PATH-004`, `PATH-005`
- Baseline-critical now:
  yes
- Evidence notes:
  `CMakePresets.json`, `docs/audit/ULTRA_REPO_AUDIT_BUILD_RUN_TEST_MATRIX.md`

### `ENTRY-002 - validation_fast`

- Entrypoint:
  `python tools/validation/tool_run_validation.py --repo-root . --profile FAST`
- Depends on:
  `tools/validation/`, `validation/`, `data/registries/validation_suite_registry.json`, `docs/audit/`, `data/audit/`
- Critical path contracts:
  `PATH-001`, `PATH-012`
- Baseline-critical now:
  yes
- Evidence notes:
  `tools/validation/tool_run_validation.py`, `validation/validation_engine.py`

### `ENTRY-003 - testx_all`

- Entrypoint:
  `python tools/xstack/testx_all.py --repo-root . --profile FAST`
- Depends on:
  `tools/xstack/`, repo-root assumptions, test libraries under `tools/xstack/testx/`, generated and source data roots
- Critical path contracts:
  `PATH-002`, `PATH-011`
- Baseline-critical now:
  yes
- Evidence notes:
  `tools/xstack/testx_all.py`, `docs/audit/ULTRA_REPO_AUDIT_BUILD_RUN_TEST_MATRIX.md`

### `ENTRY-004 - launcher_appshell_shell`

- Entrypoint:
  `python tools/launcher/launch.py`
- Depends on:
  `appshell/`, `release/`, `compat/`, `lib/install/`, `data/registries/virtual_root_registry.json`, `dist/`, repo-local `saves/`
- Critical path contracts:
  `PATH-001`, `PATH-012`, `PATH-013`
- Baseline-critical now:
  yes
- Evidence notes:
  `tools/launcher/launch.py`, `appshell/paths/virtual_paths.py`

### `ENTRY-005 - setup_appshell_shell`

- Entrypoint:
  `python tools/setup/setup_cli.py`
- Depends on:
  `appshell/`, `release/`, `security/trust/`, install/export/store libs, repo-root hints, manifest discovery
- Critical path contracts:
  `PATH-001`, `PATH-012`, `PATH-013`, `PATH-014`
- Baseline-critical now:
  yes
- Evidence notes:
  `tools/setup/setup_cli.py`, `security/trust/trust_verifier.py`, `release/update_resolver.py`

### `ENTRY-006 - session_create`

- Entrypoint:
  `python tools/xstack/session_create.py`
- Depends on:
  `tools/xstack/`, `profiles/`, `locks/`, `data/session_templates/`, `data/registries/`, generated `build/registries/` and `build/lockfile.json`, repo-local `saves/`
- Critical path contracts:
  `PATH-002`, `PATH-009`, `PATH-010`, `PATH-011`
- Baseline-critical now:
  yes
- Evidence notes:
  `tools/xstack/session_create.py`, `tools/xstack/sessionx/creator.py`, `tools/xstack/registry_compile/constants.py`

### `ENTRY-007 - session_boot`

- Entrypoint:
  `python tools/xstack/session_boot.py`
- Depends on:
  `tools/xstack/`, `saves/<save_id>/session_spec.json`, SessionX runner, generated registries and lockfile outputs, server boot path
- Critical path contracts:
  `PATH-002`, `PATH-006`, `PATH-007`, `PATH-011`
- Baseline-critical now:
  yes
- Evidence notes:
  `tools/xstack/session_boot.py`, `tools/xstack/sessionx/runner.py`

### `ENTRY-008 - local_loopback_authority_path`

- Entrypoint:
  repo-local singleplayer flow anchored in `client/local_server/local_server_controller.py`
- Depends on:
  `client/local_server/`, `runtime/process_spawn.py`, `server/server_main.py`, `server/net/loopback_transport.py`, repo-local `saves/`
- Critical path contracts:
  `PATH-003`, `PATH-006`, `PATH-007`, `PATH-008`
- Baseline-critical now:
  yes
- Evidence notes:
  `client/local_server/local_server_controller.py`, `runtime/process_spawn.py`, `server/net/loopback_transport.py`

### `ENTRY-009 - runtime_entry_transitional_shell`

- Entrypoint:
  `python tools/mvp/runtime_entry.py --local-singleplayer`
- Depends on:
  `tools/mvp/`, `client/local_server/`, authored MVP asset locations, SessionX machinery, repo-local save assumptions
- Critical path contracts:
  `PATH-009`, `PATH-010`, `PATH-006`, `PATH-007`
- Baseline-critical now:
  transitional only
- Evidence notes:
  `tools/mvp/runtime_entry.py`, `tools/mvp/runtime_bundle.py`, `docs/audit/ULTRA_REPO_AUDIT_PLAYTEST_READINESS.md`

## G. Canonical Vs Derived Data And Location Map

| Location | Current role | Classification | Why |
| --- | --- | --- | --- |
| `packs/` | runtime packaging, activation, compatibility, distribution descriptor root | canonical source of truth with bounded split caveat | governance and pack docs treat it as canonical for runtime packaging scope |
| `data/packs/` | authored pack-content and declaration root | transitional and bounded authoritative | still authoritative for authored pack-content scope, but not the settled single-root future |
| `profiles/bundles/` | authored profile bundles | canonical source of truth for authored profile bundles | current baseline assets live here and AppShell resolves profiles here |
| `locks/` | authored lock declarations | canonical source of truth for authored locks | baseline lock lives here; generated and store copies exist elsewhere |
| `data/session_templates/` | authored session template payloads | canonical support-data location | current baseline template lives here and tooling references it directly |
| `data/registries/` | machine-readable runtime, shell, release, trust, and validation registries | canonical support-data location | live code reads these registries directly |
| `build/registries/` | compiled registry outputs | generated and baseline-consumed | SessionX create and runner depend on them, but they are outputs, not authored canon |
| `build/lockfile.json` | compiled lockfile output | generated and baseline-consumed | current SessionX path still expects it |
| `schema/` | semantic and contract law | canonical source of truth | governance explicitly assigns canonical status here |
| `schemas/` | validator-facing schemas and examples | derived or mixed projection root | useful and consumed, but not canonical law |
| `docs/planning/` | planning law and checkpoints | canonical source of truth within authority order | planning canon outranks mirrors |
| `data/planning/` | planning mirrors and machine-readable checkpoints | derived mirror with intact provenance | useful evidence, not higher-order canon |
| `docs/audit/` | human-readable audit evidence | mixed evidence root | high-value evidence, but not implementation truth when code differs |
| `data/audit/` | machine-readable audit evidence | derived report-only root | mirrors reports and evidence payloads |
| `docs/xstack/` | xstack closure and retained/deferred contracts | canonical bounded-domain packet for this series | XStack/AIDE closure is frozen and constraining |
| `data/xstack/` | xstack mirrors | derived mirror with intact provenance | machine-readable consumption only |
| `dist/` | assembled distribution tree | generated but operationally important | launcher/setup/appshell discover it, but it is not authored canon |
| `saves/` | runtime materialized saves | mixed and operationally canonical for now | not authored truth, but current baseline path assumes it |

## H. Overlap, Duplication, And Ambiguity Findings

- `tools/` is top-level prominent but not a clean owner. Later prompts must reason at the subroot level, not by assuming the umbrella root is canonical.
- `launcher/` and `setup/` look like natural product owners because they are first-class compiled roots, but the stronger repo-local operator truth currently sits in `tools/launcher/launch.py` and `tools/setup/setup_cli.py`.
- `runtime/` and `validation/` are real roots, but both are thinner than the operational flows that depend on them. Later topology changes cannot assume their small size means low coupling.
- `net/` and `server/net/` are separate roots with operationally entangled responsibilities. A relayout that moves one without mapping the other will likely misread authority and transport ownership.
- `schema/` and `schemas/` remain an active canonical-versus-projection split. Later prompts must not flatten them into one ownership story.
- `packs/` and `data/packs/` remain an active runtime-packaging-versus-authored-pack-content split. Later prompts must consume that split before proposing consolidation.
- `profiles/bundles/`, `locks/`, `data/session_templates/`, and `data/registries/` are all real live inputs, but the current default-bundle story is split between authored MVP assets and registry-compiled `bundle.base.lab`.
- `dist/` is generated, but it is still on the operational path for launcher/setup discovery. Later prompts must not treat generated roots as irrelevant just because they are non-canonical.
- `saves/` is not authored canon, but it is a baseline-critical operational contract today. Moving or abstracting it prematurely would break the current boot path.

## I. Boundaries On Redesign Freedom

### Later Prompts Are Free To Redesign Conceptually

- the eventual top-level grouping or clustering model
- how to present or document ownership more clearly
- how to reduce ambiguity between wrapper roots and stronger implementation roots
- how to phase future convergence between authored and generated intermediates
- how to eventually normalize the bundle/profile/lock/template default story

### Later Prompts Must Preserve As Current-Reality Facts

- `appshell/` is the current canonical repo-local shell/bootstrap owner
- the strongest launcher/setup flows are currently the Python/AppShell shells under `tools/`
- the playable-baseline path is repo-local, session-based, and loopback-authoritative
- `server/server_main.py` repo-root math is still blocked
- SessionX runner still hardcodes repo-local `saves/<save_id>`
- authored MVP assets and generated registry/lockfile intermediates currently coexist
- `schema/` versus `schemas/` and `packs/` versus `data/packs/` are still active ownership splits
- `dist/` is derived but operationally consumed

### Later Prompts Must Not Ignore Even If They Plan To Move Things Later

- verify build and test presets
- FAST validation and TestX lanes
- launcher/setup AppShell flows
- session create and boot flows
- local loopback authority flow
- `profiles/`, `locks/`, `data/session_templates/`, `data/registries/` physical locations as current live inputs
- release and trust registry paths
- current `saves/` boot assumptions

## J. Anti-Patterns And Forbidden Shapes

- assuming top-level prominence means canonical ownership
- treating `tools/` as a clean owner without drilling into the actual subroot entrypoints
- treating `launcher/` or `setup/` native wrappers as canonical just because they look cleaner than the Python shells
- collapsing `schema/` and `schemas/` into one class before the ownership split is designed explicitly
- collapsing `packs/` and `data/packs/` into one class before the authored-versus-runtime split is designed explicitly
- ignoring generated intermediates like `build/registries/`, `build/lockfile.json`, or `dist/` because they are non-canonical, even though live flows still depend on them
- moving `saves/` assumptions too early while the baseline path still hardcodes them
- using stale docs or root names as topology truth when live implementation evidence shows otherwise
- presenting the current tree as already normalized when the bundle-default seam, wrapper-vs-shell seam, and save-root coupling remain unresolved

## K. Stability And Evolution

- Stability class:
  stable until a later prompt explicitly records new repo evidence or an approved topology decision changes the map
- Later prompts expected to consume this artifact:
  coupling and drift analysis, redesign-option comparison, migration-sequencing design, ownership-boundary reconciliation, and shim-strategy planning prompts in this repo-structure series
- What must not change without explicit follow-up:
  ownership-class meanings, baseline-critical path-contract statements, canonical-versus-derived classifications, and the explicit record of mixed or ambiguous areas that remain unresolved today
