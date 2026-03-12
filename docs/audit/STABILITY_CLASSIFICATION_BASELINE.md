Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Stability Classification Baseline

## Summary

- scoped registry families: 46
- stable entries: 31
- provisional entries: 353
- experimental entries: 0
- scoped validator result: complete
- scoped validator fingerprint: `77b6a159bfd080d390a648d18a3ccdaf88b23889192401c166e4becbcfa3a902`
- semantic contract registry validation: pass
- semantic contract registry hash: `0f8fb3785990c6f8ea80ce767d8c2501df969a1cdb7d0f5a74b0c43a279dcdbc`

## Stable Entries

### `data/registries/capability_fallback_registry.json`

- `cap.geo.atlas_unwrap`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG fallback semantics are frozen for MVP release governance.
- `cap.logic.compiled_automaton`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG fallback semantics are frozen for MVP release governance.
- `cap.logic.debug_analyzer`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG fallback semantics are frozen for MVP release governance.
- `cap.logic.protocol_layer`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG fallback semantics are frozen for MVP release governance.
- `cap.ui.rendered`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG fallback semantics are frozen for MVP release governance.
- `cap.ui.tui`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG fallback semantics are frozen for MVP release governance.

### `data/registries/compat_mode_registry.json`

- `compat.degraded`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG negotiated mode semantics are frozen for MVP release governance.
- `compat.full`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG negotiated mode semantics are frozen for MVP release governance.
- `compat.read_only`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG negotiated mode semantics are frozen for MVP release governance.
- `compat.refuse`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG negotiated mode semantics are frozen for MVP release governance.

### `data/registries/degrade_ladder_registry.json`

- `client`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG degrade ladder semantics are frozen for MVP release governance.
- `engine`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG degrade ladder semantics are frozen for MVP release governance.
- `game`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG degrade ladder semantics are frozen for MVP release governance.
- `launcher`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG degrade ladder semantics are frozen for MVP release governance.
- `server`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG degrade ladder semantics are frozen for MVP release governance.
- `setup`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG degrade ladder semantics are frozen for MVP release governance.
- `tool.attach_console_stub`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: CAP-NEG degrade ladder semantics are frozen for MVP release governance.

### `data/registries/pack_degrade_mode_registry.json`

- `pack.degrade.best_effort`
  - contract_id: `contract.pack.compat.v1`
  - rationale: PACK-COMPAT degrade semantics are frozen for MVP release governance.
- `pack.degrade.read_only_only`
  - contract_id: `contract.pack.compat.v1`
  - rationale: PACK-COMPAT degrade semantics are frozen for MVP release governance.
- `pack.degrade.strict_refuse`
  - contract_id: `contract.pack.compat.v1`
  - rationale: PACK-COMPAT degrade semantics are frozen for MVP release governance.

### `data/registries/semantic_contract_registry.json`

- `contract.appshell.lifecycle.v1`
  - contract_id: `contract.appshell.lifecycle.v1`
  - rationale: Semantic contract meaning is frozen under its versioned contract entry.
- `contract.cap_neg.negotiation.v1`
  - contract_id: `contract.cap_neg.negotiation.v1`
  - rationale: Semantic contract meaning is frozen under its versioned contract entry.
- `contract.geo.metric.v1`
  - contract_id: `contract.geo.metric.v1`
  - rationale: Semantic contract meaning is frozen under its versioned contract entry.
- `contract.geo.partition.v1`
  - contract_id: `contract.geo.partition.v1`
  - rationale: Semantic contract meaning is frozen under its versioned contract entry.
- `contract.geo.projection.v1`
  - contract_id: `contract.geo.projection.v1`
  - rationale: Semantic contract meaning is frozen under its versioned contract entry.
- `contract.logic.eval.v1`
  - contract_id: `contract.logic.eval.v1`
  - rationale: Semantic contract meaning is frozen under its versioned contract entry.
- `contract.overlay.merge.v1`
  - contract_id: `contract.overlay.merge.v1`
  - rationale: Semantic contract meaning is frozen under its versioned contract entry.
- `contract.pack.compat.v1`
  - contract_id: `contract.pack.compat.v1`
  - rationale: Semantic contract meaning is frozen under its versioned contract entry.
- `contract.proc.capsule.v1`
  - contract_id: `contract.proc.capsule.v1`
  - rationale: Semantic contract meaning is frozen under its versioned contract entry.
- `contract.sys.collapse.v1`
  - contract_id: `contract.sys.collapse.v1`
  - rationale: Semantic contract meaning is frozen under its versioned contract entry.
- `contract.worldgen.refinement.v1`
  - contract_id: `contract.worldgen.refinement.v1`
  - rationale: Semantic contract meaning is frozen under its versioned contract entry.

## Provisional Entries With Replacement Plans

### `data/registries/bundle_profiles.json`

- `bundle.core.runtime`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `bundle.default_core`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `bundle.education.basic`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `bundle.experience.defaults`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `bundle.missions.intro`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `bundle.scenarios.intro`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.

### `data/registries/command_registry.json`

- `command.client_namespace`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.compat_status`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.console`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.console_attach`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.console_detach`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.console_enter`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.console_sessions`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.descriptor`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.diag`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.diag_capture`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.diag_snapshot`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.engine_namespace`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.game_namespace`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.geo_namespace`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.help`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.launcher_attach`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.launcher_namespace`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.launcher_start`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.launcher_status`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.launcher_stop`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.logic_namespace`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.packs`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.packs_build_lock`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.packs_list`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.packs_verify`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.profiles`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.profiles_list`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.profiles_show`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.server_namespace`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.session_namespace`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.setup_namespace`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.tool_namespace`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.verify`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `command.version`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.

### `data/registries/exit_code_registry.json`

- `exit.contract`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `exit.internal`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `exit.pack_profile`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `exit.refusal`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `exit.success`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `exit.transport`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `exit.usage`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.

### `data/registries/galaxy_priors_registry.json`

- `priors.milkyway_stub_default`
  - future_series: `MW`
  - replacement_target: Replace Milky Way stub priors with calibrated MW series galaxy priors.

### `data/registries/generator_version_registry.json`

- `gen.v0_stub`
  - future_series: `MW/EARTH/SOL`
  - replacement_target: Replace MVP generator version placeholders with release lineage metadata for MW/EARTH/SOL generators.

### `data/registries/illumination_model_registry.json`

- `illum.basic_diffuse_default`
  - future_series: `SOL/EARTH`
  - replacement_target: Replace illumination stubs with calibrated SOL/EARTH illumination models.

### `data/registries/log_category_registry.json`

- `appshell`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `client`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `compat`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `diag`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `ipc`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `packs`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `server`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `tool`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `ui`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `worldgen`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.

### `data/registries/log_message_key_registry.json`

- `appshell.bootstrap.start`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `appshell.command.dispatch`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `appshell.mode.enter`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `appshell.refusal`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `appshell.tui.backend_degraded`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `appshell.tui.command.executed`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `appshell.tui.surface.ready`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `compat.negotiation.client_refused`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `compat.negotiation.mismatch`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `compat.negotiation.read_only`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `compat.negotiation.refused`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `compat.negotiation.result`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `diag.capture.written`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `diag.snapshot.written`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `ipc.attach.accepted`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `ipc.attach.refused`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `ipc.endpoint.started`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `ipc.endpoint.stopped`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `packs.lock.generated`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `packs.verify.result`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `server.connection.accepted`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `server.control.processed`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `server.listener.bound`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `server.proof_anchor.emitted`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `server.tick.advanced`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `supervisor.child.crash_requested`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `supervisor.child.ready`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `supervisor.child.stdin_ignored`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `supervisor.child.stop_requested`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `supervisor.command.attach`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `supervisor.command.start`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `supervisor.command.stop`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `supervisor.process.spawned`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `supervisor.restart.applied`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `supervisor.service.ready`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `supervisor.start.complete`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `supervisor.stop.complete`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `worldgen.refinement.request.summary`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.

### `data/registries/logic_compile_policy_registry.json`

- `compile.logic.default`
  - future_series: `LOGIC`
  - replacement_target: Replace provisional logic semantics with release-pinned LOGIC registry definitions.
- `compile.logic.lab`
  - future_series: `LOGIC`
  - replacement_target: Replace provisional logic semantics with release-pinned LOGIC registry definitions.
- `compile.logic.rank_strict`
  - future_series: `LOGIC`
  - replacement_target: Replace provisional logic semantics with release-pinned LOGIC registry definitions.

### `data/registries/logic_network_policy_registry.json`

- `logic.policy.allow_roi_loops`
  - future_series: `LOGIC`
  - replacement_target: Replace provisional logic semantics with release-pinned LOGIC registry definitions.
- `logic.policy.default`
  - future_series: `LOGIC`
  - replacement_target: Replace provisional logic semantics with release-pinned LOGIC registry definitions.
- `logic.policy.lab_allow`
  - future_series: `LOGIC`
  - replacement_target: Replace provisional logic semantics with release-pinned LOGIC registry definitions.

### `data/registries/logic_security_policy_registry.json`

- `sec.auth_required_stub`
  - future_series: `LOGIC`
  - replacement_target: Replace provisional logic semantics with release-pinned LOGIC registry definitions.
- `sec.encrypted_required_stub`
  - future_series: `LOGIC`
  - replacement_target: Replace provisional logic semantics with release-pinned LOGIC registry definitions.
- `sec.none`
  - future_series: `LOGIC`
  - replacement_target: Replace provisional logic semantics with release-pinned LOGIC registry definitions.

### `data/registries/platform_registry.json`

- `abi:android:ndk-r26`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `abi:dos:djgpp`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `abi:dos:watcom`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `abi:ios:xcode`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `abi:linux:gnu`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `abi:macclassic:metrowerks`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `abi:macosx:clang`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `abi:web:emscripten`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `abi:win16:watcom-16`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `abi:win9x:mingw-legacy`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `abi:winnt:msvc-v180`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `abi:winnt:msvc-v180`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `abi:winnt:msvc-v180`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.

### `data/registries/process_drift_policy_registry.json`

- `drift.default`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `drift.fast_dev`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `drift.strict`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.

### `data/registries/process_lifecycle_policy_registry.json`

- `proc.lifecycle.default`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `proc.lifecycle.lab_experimental`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `proc.lifecycle.rank_strict`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.

### `data/registries/process_registry.json`

- `org.dominium.base.rules.process.template.epistemic.basic`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `org.dominium.base.rules.process.template.transactional.basic`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `org.dominium.base.rules.process.template.transformative.basic`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `proc.archetype.assemble_system`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `proc.archetype.cast_part`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `proc.archetype.compile_firmware`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `proc.archetype.machine_part`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `proc.archetype.test_and_calibrate`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.alchemy.calcine`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.alchemy.transmute`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.astrology.interpret`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.body_apply_input`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.body_jump`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.body_tick`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.candidate_promote_to_defined`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.compile_request_submit`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.craft.execute`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.earth_climate_tick`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.earth_tide_tick`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.earth_wind_tick`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.epistemic.distort`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.epistemic.experiment`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.epistemic.infer`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.epistemic.measure`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.epistemic.observe`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.epistemic.publish`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.epistemic.suppress`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.epistemic.survey`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.examples.false_science.build`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.examples.false_science.design`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.examples.lost_civilization.catalog`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.examples.lost_civilization.excavate`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.experiment_run_complete`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.experiment_run_start`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.field_update`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.hyperspace.enter`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.hyperspace.exit`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.hyperspace.travel`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.logic_compile_request`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.logic_fault_clear`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.logic_fault_set`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.logic_network_add_edge`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.logic_network_add_node`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.logic_network_create`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.logic_network_evaluate`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.logic_network_remove_edge`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.logic_network_validate`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.logic_probe`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.logic_trace_end`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.logic_trace_start`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.logic_trace_tick`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.magic.divination`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.magic.ritual.cast`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.magic.spell.weave`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.mine.cut`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.mine.extract`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.mine.support_check`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.construction.certify_structure`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.construction.claim_volume`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.construction.clear_and_prepare`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.construction.connect_interface`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.construction.establish_foundation`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.construction.place_part`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.construction.release_volume`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.construction.survey_site`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.construction.verify_integrity`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.maintenance.degrade_performance`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.maintenance.fail_component`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.maintenance.inspect_condition`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.maintenance.repair`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.maintenance.replace_part`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.maintenance.wear_accumulate`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.manufacturing.assemble_subsystem`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.manufacturing.fabricate_part`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.manufacturing.quality_check`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.manufacturing.scrap_or_rework`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.manufacturing.transform_material`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.mining.access_deposit`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.mining.discover_deposit`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.mining.extract_material`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.mining.handle_tailings`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.mining.refine_material`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.mining.transport_output`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.network.attach`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.network.balance_flow`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.network.detach`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.network.register`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.network.repair`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.network.route_flow`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.network.verify`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.regulation.certify`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.regulation.inspect`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.regulation.issue_or_deny`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.regulation.penalize_violation`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.regulation.request_permit`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.regulation.review_compliance`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terraforming.alter_atmosphere`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terraforming.climate_feedback`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terraforming.inject_gases`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terraforming.introduce_biomass`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terraforming.modify_albedo`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terraforming.redistribute_water`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terraforming.remove_gases`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terrain.channel_water`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terrain.clear_land`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terrain.compact_soil`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terrain.contaminate`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terrain.cut_tree`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terrain.dam_flow`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terrain.deposit_fill`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terrain.excavate`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terrain.grade_surface`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terrain.remediate`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.terrain.seed_biomass`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.trade.load_transport`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.trade.move_goods`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.trade.negotiate_contract`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.trade.schedule_delivery`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.trade.transfer_ownership`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.on_planet.trade.unload_and_register`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.pollution_compliance_tick`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.pollution_dispersion_tick`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.pollution_emit`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.pollution_measure`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.process_run_end`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.process_run_start`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.process_run_tick`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.refinement_request_enqueue`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.refinement_scheduler_tick`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.reverse_engineering_action`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.schema.migrate.pack_manifest.v1_to_v2`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.schema.migrate.pack_manifest.v2_1_to_v2_2`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.schema.migrate.pack_manifest.v2_2_to_v2_3`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.signal_emit_pulse`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.signal_set`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.software_pipeline_execute`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.statevec_update`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.system_collapse`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.system_evaluate_certification`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.system_expand`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.system_generate_explain`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.system_health_tick`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.system_macro_tick`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.system_reliability_tick`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.system_roi_tick`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.template_instantiate`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.terrain.collapse.1`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.terrain.cut.1`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `process.terrain.fill.1`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.

### `data/registries/process_stabilization_policy_registry.json`

- `stab.default`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `stab.fast_dev`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.
- `stab.strict`
  - future_series: `PROC`
  - replacement_target: Replace provisional process semantics with release-pinned PROC registry definitions.

### `data/registries/product_registry.json`

- `client`
  - future_series: `CAP-NEG`
  - replacement_target: Replace provisional product negotiation defaults with release-pinned CAP-NEG product contracts.
- `engine`
  - future_series: `CAP-NEG`
  - replacement_target: Replace provisional product negotiation defaults with release-pinned CAP-NEG product contracts.
- `game`
  - future_series: `CAP-NEG`
  - replacement_target: Replace provisional product negotiation defaults with release-pinned CAP-NEG product contracts.
- `launcher`
  - future_series: `CAP-NEG`
  - replacement_target: Replace provisional product negotiation defaults with release-pinned CAP-NEG product contracts.
- `server`
  - future_series: `CAP-NEG`
  - replacement_target: Replace provisional product negotiation defaults with release-pinned CAP-NEG product contracts.
- `setup`
  - future_series: `CAP-NEG`
  - replacement_target: Replace provisional product negotiation defaults with release-pinned CAP-NEG product contracts.
- `tool.attach_console_stub`
  - future_series: `CAP-NEG`
  - replacement_target: Replace provisional product negotiation defaults with release-pinned CAP-NEG product contracts.

### `data/registries/protocol_registry.json`

- `protocol.bus_arbitration_stub`
  - future_series: `LOGIC/CAP-NEG`
  - replacement_target: Replace protocol stubs with release-pinned logic/protocol registry definitions.
- `protocol.none`
  - future_series: `LOGIC/CAP-NEG`
  - replacement_target: Replace protocol stubs with release-pinned logic/protocol registry definitions.
- `protocol.simple_frame_stub`
  - future_series: `LOGIC/CAP-NEG`
  - replacement_target: Replace protocol stubs with release-pinned logic/protocol registry definitions.

### `data/registries/provides_registry.json`

- `provides.earth.dem.v1`
  - future_series: `LIB/PACK-COMPAT`
  - replacement_target: Replace provisional provides surfaces with release-pinned LIB and PACK-COMPAT provider definitions.
- `provides.profile.bundle.v1`
  - future_series: `LIB/PACK-COMPAT`
  - replacement_target: Replace provisional provides surfaces with release-pinned LIB and PACK-COMPAT provider definitions.

### `data/registries/refusal_code_registry.json`

- `refusal.compat.contract_mismatch`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.compat.feature_disabled`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.compat.negotiation_record_mismatch`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.compat.negotiation_record_missing`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.compat.no_common_protocol`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.connection.negotiation_mismatch`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.connection.no_negotiation`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.contract.mismatch`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.debug.command_unavailable`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.debug.command_unknown`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.debug.disabled`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.debug.mode_unsupported`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.debug.rendered_client_only`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.diag.bundle_hash_mismatch`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.diag.secrets_detected`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.io.invalid_args`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.io.offline_required`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.io.profile_not_found`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.law.attach_denied`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.law.denied`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.pack.contract_range_mismatch`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.pack.registry_missing`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.server.command_unknown`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.supervisor.already_running`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.supervisor.endpoint_unreached`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.supervisor.not_running`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.supervisor.process_missing`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `refusal.supervisor.restart_denied`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.

### `data/registries/server_config_registry.json`

- `server.mvp_default`
  - future_series: `LIB/SERVER`
  - replacement_target: Replace MVP server config placeholder with release-pinned server configuration semantics.

### `data/registries/server_profile_registry.json`

- `server.profile.casual_public`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `server.profile.private_relaxed`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `server.profile.rank_strict`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.

### `data/registries/shadow_model_registry.json`

- `shadow.horizon_stub_default`
  - future_series: `SOL/EARTH`
  - replacement_target: Replace shadow stubs with calibrated SOL/EARTH shadow models.
- `shadow.none`
  - future_series: `SOL/EARTH`
  - replacement_target: Replace shadow stubs with calibrated SOL/EARTH shadow models.

### `data/registries/sky_model_registry.json`

- `sky.gradient_stub_default`
  - future_series: `SOL/EARTH`
  - replacement_target: Replace sky stubs with calibrated SOL/EARTH sky models.

### `data/registries/software_toolchain_registry.json`

- `toolchain.stub_c89`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `toolchain.stub_cpp98`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.
- `toolchain.stub_script`
  - future_series: `LIB`
  - replacement_target: Replace provisional distribution and library semantics with release-pinned LIB registry definitions.

### `data/registries/surface_generator_registry.json`

- `gen.surface.default_stub`
  - future_series: `EARTH/MW`
  - replacement_target: Replace procedural surface stubs with calibrated EARTH and MW surface generators.
- `gen.surface.earth_stub`
  - future_series: `EARTH/MW`
  - replacement_target: Replace procedural surface stubs with calibrated EARTH and MW surface generators.

### `data/registries/surface_generator_routing_registry.json`

- `gen.surface.default_stub`
  - future_series: `EARTH/MW`
  - replacement_target: Replace provisional routing rules with calibrated EARTH and MW surface routing rules.
- `gen.surface.earth_stub`
  - future_series: `EARTH/MW`
  - replacement_target: Replace provisional routing rules with calibrated EARTH and MW surface routing rules.

### `data/registries/system_boundary_invariant_registry.json`

- `invariant.energy_conserved`
  - future_series: `SYS`
  - replacement_target: Replace provisional system semantics with release-pinned SYS registry definitions.
- `invariant.mass_conserved`
  - future_series: `SYS`
  - replacement_target: Replace provisional system semantics with release-pinned SYS registry definitions.
- `invariant.momentum_conserved`
  - future_series: `SYS`
  - replacement_target: Replace provisional system semantics with release-pinned SYS registry definitions.
- `invariant.pollutant_accounted`
  - future_series: `SYS`
  - replacement_target: Replace provisional system semantics with release-pinned SYS registry definitions.

### `data/registries/system_priors_registry.json`

- `priors.system_default_stub`
  - future_series: `SYS`
  - replacement_target: Replace provisional system semantics with release-pinned SYS registry definitions.

### `data/registries/system_template_registry.json`

- `template.body.pill`
  - future_series: `SYS`
  - replacement_target: Replace provisional system semantics with release-pinned SYS registry definitions.
- `template.logic_controller`
  - future_series: `SYS`
  - replacement_target: Replace provisional system semantics with release-pinned SYS registry definitions.

### `data/registries/tide_params_registry.json`

- `tide.earth_stub_default`
  - future_series: `EARTH/SOL`
  - replacement_target: Replace tide stubs with calibrated EARTH/SOL tide parameter sets.

### `data/registries/tui_layout_registry.json`

- `layout.default`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `layout.server`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `layout.viewer`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.

### `data/registries/tui_panel_registry.json`

- `panel.console`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `panel.inspect`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `panel.logs`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `panel.map`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.
- `panel.status`
  - future_series: `APPSHELL`
  - replacement_target: Replace provisional AppShell semantics with release-pinned APPSHELL registry definitions.

### `data/registries/verification_procedure_registry.json`

- `verify.bounded_sampling`
  - future_series: `LOGIC`
  - replacement_target: Replace provisional logic semantics with release-pinned LOGIC registry definitions.
- `verify.exact_structural`
  - future_series: `LOGIC`
  - replacement_target: Replace provisional logic semantics with release-pinned LOGIC registry definitions.
- `verify.symbolic_stub`
  - future_series: `LOGIC`
  - replacement_target: Replace provisional logic semantics with release-pinned LOGIC registry definitions.

### `data/registries/wind_params_registry.json`

- `wind.earth_stub_default`
  - future_series: `EARTH`
  - replacement_target: Replace wind stubs with calibrated EARTH wind parameter sets.

## Experimental Entries

- none in META-STABILITY-0 scope
- gating notes: no experimental entries were tagged in the initial conservative pass

## Gate Status

- RepoX STRICT: full-repo check still fails on unrelated repository debt outside META-STABILITY-0; scoped stability invariants report 0 findings
- AuditX STRICT: full-repo scan exceeded the local timeout budget; scoped analyzers E387/E449/E450/E451 report 0 findings
- TestX: pass for `test_all_registries_have_stability_markers`, `test_stable_requires_contract_id`, `test_provisional_requires_replacement_plan`, and `test_validator_deterministic_output`
- strict build: pass via `python -m py_compile` on the touched stability, RepoX, AuditX, and TestX modules

## Readiness

- TIME-ANCHOR-0: ready from the stability-discipline perspective once unrelated repository-wide governance debt is cleared
- ARCH-AUDIT-0: ready for architecture review with stable semantics frozen and provisional debt explicitly tagged
