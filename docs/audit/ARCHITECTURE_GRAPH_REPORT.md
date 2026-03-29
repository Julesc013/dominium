Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI
Replacement Target: XI-1 architectural convergence plan

# Architecture Graph Report

- concept_count: `319`
- module_count: `1735`
- duplicate_symbol_signal_count: `5871`
- unknown_domain_module_count: `1`
- circular_dependency_count: `14`

## Duplicate Signals

- `ALLOWED_CONTROL_IR_OP_TYPES` -> control/__init__.py, control/ir/__init__.py, control/ir/control_ir_verifier.py
- `ALL_REGISTRY_PATHS` -> meta/stability/__init__.py, meta/stability/stability_scope.py, meta/stability/stability_validator.py
- `ANCHOR_REASON_INTERVAL` -> engine/time/__init__.py, engine/time/epoch_anchor_engine.py
- `ANCHOR_REASON_MIGRATION` -> engine/time/__init__.py, engine/time/epoch_anchor_engine.py
- `ANCHOR_REASON_SAVE` -> engine/time/__init__.py, engine/time/epoch_anchor_engine.py
- `ARCHITECTURE_GRAPH_REL` -> tools/review/architecture_graph_bootstrap_common.py, tools/review/convergence_execution_common.py, tools/review/convergence_plan_common.py, tools/review/duplicate_impl_scan_common.py
- `ARCHIVE_POLICY_ID` -> governance/__init__.py, governance/governance_profile.py
- `ARTIFACT_DEGRADE_BEST_EFFORT` -> lib/artifact/__init__.py, lib/artifact/artifact_validator.py
- `ARTIFACT_DEGRADE_MODE_VALUES` -> lib/artifact/__init__.py, lib/artifact/artifact_validator.py
- `ARTIFACT_DEGRADE_READ_ONLY_ONLY` -> lib/artifact/__init__.py, lib/artifact/artifact_validator.py
- `ARTIFACT_DEGRADE_STRICT_REFUSE` -> lib/artifact/__init__.py, lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_BLUEPRINT` -> compat/migration_lifecycle.py, lib/artifact/__init__.py, lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_IDS` -> compat/migration_lifecycle.py, tools/xstack/testx/tests/migration_lifecycle_testlib.py
- `ARTIFACT_KIND_LOGIC_PROGRAM` -> lib/artifact/__init__.py, lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_PACK` -> release/release_manifest_engine.py, security/trust/__init__.py
- `ARTIFACT_KIND_PROCESS_DEFINITION` -> lib/artifact/__init__.py, lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_PROFILE_BUNDLE` -> compat/migration_lifecycle.py, lib/artifact/__init__.py, lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_RELEASE_INDEX` -> compat/migration_lifecycle.py, security/trust/__init__.py
- `ARTIFACT_KIND_RELEASE_MANIFEST` -> compat/migration_lifecycle.py, security/trust/__init__.py
- `ARTIFACT_KIND_RESOURCE_PACK_STUB` -> lib/artifact/__init__.py, lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_SYSTEM_TEMPLATE` -> lib/artifact/__init__.py, lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_VALUES` -> lib/artifact/__init__.py, lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_VIEW_PRESET` -> lib/artifact/__init__.py, lib/artifact/artifact_validator.py
- `AnalysisGraph` -> tools/auditx/graph/__init__.py, tools/auditx/graph/analysis_graph.py
- `AppShellIPCEndpointServer` -> appshell/ipc/__init__.py, appshell/ipc/ipc_endpoint_server.py

## Unknown Domains

- `unknown.root` :: `.`

## Circular Dependencies

- apps.client.interaction -> apps.client.local_server -> apps.client.net -> apps.client.render -> apps.client.render.renderers -> apps.client.ui -> apps.server -> apps.server.net -> apps.server.persistence -> apps.server.runtime -> apps.setup.packages.scripts.packaging -> appshell -> appshell.commands -> appshell.diag -> appshell.ipc -> appshell.logging -> appshell.paths -> appshell.supervisor -> appshell.tui -> archive -> astro.ephemeris -> astro.illumination -> astro.views -> chem -> chem.degradation -> compat -> compat.descriptor -> compat.negotiation -> compat.shims -> control -> control.capability -> control.effects -> control.fidelity -> control.ir -> control.negotiation -> control.planning -> control.proof -> control.view -> core.flow -> core.graph -> core.hazards -> core.schedule -> diag -> diegetics -> electric -> electric.fault -> electric.protection -> electric.storage -> embodiment.body -> embodiment.collision -> embodiment.lens -> embodiment.movement -> embodiment.tools -> engine.platform -> engine.time -> epistemics.memory -> field -> fields -> fluid -> fluid.network -> geo -> geo.edit -> geo.frame -> geo.index -> geo.kernel -> geo.metric -> geo.overlay -> geo.path -> geo.projection -> geo.worldgen -> governance -> infrastructure.formalization -> inspection -> interaction.task -> interior -> lib.artifact -> lib.bundle -> lib.export -> lib.install -> lib.instance -> lib.provides -> lib.save -> lib.store -> logic -> logic.compile -> logic.debug -> logic.element -> logic.eval -> logic.fault -> logic.network -> logic.noise -> logic.protocol -> logic.signal -> logic.timing -> logistics -> materials -> materials.commitments -> materials.construction -> materials.maintenance -> materials.materialization -> materials.performance -> materials.provenance -> mechanics -> meta -> meta.compile -> meta.compute -> meta.explain -> meta.extensions -> meta.identity -> meta.instrumentation -> meta.profile -> meta.provenance -> meta.reference -> meta.stability -> mobility -> mobility.geometry -> mobility.maintenance -> mobility.micro -> mobility.network -> mobility.signals -> mobility.traffic -> mobility.travel -> mobility.vehicle -> modding -> models -> net.anti_cheat -> net.policies -> net.srz -> net.testing -> packs.compat -> performance -> physics -> physics.energy -> physics.entropy -> pollution -> process -> process.capsules -> process.drift -> process.maturity -> process.qc -> process.research -> process.software -> reality.ledger -> release -> runtime -> safety -> security.trust -> signals.addressing -> signals.aggregation -> signals.transport -> signals.trust -> specs -> system -> system.certification -> system.forensics -> system.macro -> system.reliability -> system.roi -> system.statevec -> system.templates -> thermal.network -> tools -> tools.appshell -> tools.astro -> tools.audit -> tools.auditx -> tools.auditx.analyzers -> tools.auditx.output -> tools.chem -> tools.compat -> tools.compatx.core -> tools.convergence -> tools.data -> tools.dev.impact_graph -> tools.dist -> tools.domain -> tools.earth -> tools.electric -> tools.embodiment -> tools.engine -> tools.fluid -> tools.geo -> tools.governance -> tools.launcher -> tools.lib -> tools.logic -> tools.meta -> tools.mmo -> tools.mvp -> tools.net -> tools.perf -> tools.physics -> tools.pollution -> tools.process -> tools.release -> tools.review -> tools.scripts.ci -> tools.scripts.dev -> tools.security -> tools.server -> tools.setup -> tools.system -> tools.thermal -> tools.time -> tools.worldgen -> tools.xstack -> tools.xstack.auditx -> tools.xstack.cache_store -> tools.xstack.compatx -> tools.xstack.controlx -> tools.xstack.core -> tools.xstack.extensions -> tools.xstack.pack_contrib -> tools.xstack.pack_loader -> tools.xstack.packagingx -> tools.xstack.performx -> tools.xstack.registry_compile -> tools.xstack.repox -> tools.xstack.securex -> tools.xstack.sessionx -> tools.xstack.testx -> tools.xstack.testx.tests -> ui -> universe -> unknown.root -> validation -> worldgen.core -> worldgen.earth -> worldgen.earth.lighting -> worldgen.earth.material -> worldgen.earth.sky -> worldgen.earth.water -> worldgen.earth.wind -> worldgen.galaxy -> worldgen.mw -> worldgen.refinement
- engine.include.domino -> engine.include.domino.core -> engine.include.domino.world
- engine.include.domino.ecs -> engine.include.domino.execution
- engine.modules.agent -> engine.modules.ai -> engine.modules.build -> engine.modules.content -> engine.modules.core -> engine.modules.core.graph -> engine.modules.core.graph.part -> engine.modules.econ -> engine.modules.env -> engine.modules.execution.budgets -> engine.modules.execution.ir -> engine.modules.execution.scheduler -> engine.modules.hydro -> engine.modules.job -> engine.modules.net -> engine.modules.policy -> engine.modules.replay -> engine.modules.res -> engine.modules.research -> engine.modules.scale -> engine.modules.sim -> engine.modules.sim.act -> engine.modules.sim.lod -> engine.modules.sim.pkt -> engine.modules.struct -> engine.modules.trans -> engine.modules.vehicle -> engine.modules.world -> engine.modules.world.frame
- engine.modules.system -> engine.modules.system.input
- game.core.execution -> game.include.dominium -> game.include.dominium.agents -> game.include.dominium.execution -> game.include.dominium.physical -> game.include.dominium.rules.agents
- game.include.dominium.rules.city -> game.include.dominium.rules.infrastructure
- legacy._orphaned.legacy_source_game.game -> legacy._orphaned.legacy_source_game.game.runtime -> legacy._orphaned.legacy_source_game.game.ui
- legacy.engine_modules_engine.engine.render -> legacy.engine_modules_engine.engine.render.dx11 -> legacy.engine_modules_engine.engine.render.dx9 -> legacy.engine_modules_engine.engine.render.gl2
- legacy.engine_modules_engine.engine.render.api -> legacy.engine_modules_engine.engine.render.api.core -> legacy.engine_modules_engine.engine.render.dx.dx9 -> legacy.engine_modules_engine.engine.render.soft.core -> legacy.engine_modules_engine.engine.render.soft.targets.null
- legacy.engine_modules_engine.engine.trans.compile -> legacy.engine_modules_engine.engine.trans.model
- legacy.setup_core_setup.setup.core -> legacy.setup_core_setup.setup.core.log
- tools.tool_editor -> tools.tool_editor.ui.gen -> tools.tool_editor.ui.user
- tools.validate -> tools.validation

