Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI
Replacement Target: XI-1 architectural convergence plan

# Architecture Graph Report

- concept_count: `126`
- module_count: `2356`
- duplicate_symbol_signal_count: `7980`
- unknown_domain_module_count: `1`
- circular_dependency_count: `19`

## Duplicate Signals

- `ALLOWED_CONTROL_IR_OP_TYPES` -> archive/quarantine/control/__init__.py, tools/repo/governance/ir/__init__.py, tools/repo/governance/ir/control_ir_verifier.py
- `ALL_REGISTRY_PATHS` -> tools/validators/stability/__init__.py, tools/validators/stability/stability_scope.py, tools/validators/stability/stability_validator.py
- `ANCHOR_REASON_INTERVAL` -> engine/time/__init__.py, engine/time/epoch_anchor_engine.py
- `ANCHOR_REASON_MIGRATION` -> engine/time/__init__.py, engine/time/epoch_anchor_engine.py
- `ANCHOR_REASON_SAVE` -> engine/time/__init__.py, engine/time/epoch_anchor_engine.py
- `ARCHITECTURE_GRAPH_REL` -> tools/audit/review/architecture_graph_bootstrap_common.py, tools/audit/review/convergence_execution_common.py, tools/audit/review/convergence_plan_common.py, tools/audit/review/duplicate_impl_scan_common.py
- `ARCHIVE_POLICY_ID` -> archive/quarantine/governance/__init__.py, tools/repo/governance/governance_profile.py
- `ARTIFACT_DEGRADE_BEST_EFFORT` -> tools/package/libraries/artifact/__init__.py, tools/package/libraries/artifact/artifact_validator.py
- `ARTIFACT_DEGRADE_MODE_VALUES` -> tools/package/libraries/artifact/__init__.py, tools/package/libraries/artifact/artifact_validator.py
- `ARTIFACT_DEGRADE_READ_ONLY_ONLY` -> tools/package/libraries/artifact/__init__.py, tools/package/libraries/artifact/artifact_validator.py
- `ARTIFACT_DEGRADE_STRICT_REFUSE` -> tools/package/libraries/artifact/__init__.py, tools/package/libraries/artifact/artifact_validator.py
- `ARTIFACT_KIND_BLUEPRINT` -> runtime/compatibility/migration_lifecycle.py, tools/package/libraries/artifact/__init__.py, tools/package/libraries/artifact/artifact_validator.py, tools/validators/compatibility/migration_lifecycle.py
- `ARTIFACT_KIND_COMPONENT_GRAPH` -> runtime/compatibility/migration_lifecycle.py, tools/validators/compatibility/migration_lifecycle.py
- `ARTIFACT_KIND_IDS` -> runtime/compatibility/migration_lifecycle.py, tools/validators/compatibility/migration_lifecycle.py, tools/xstack/testx/tests/migration_lifecycle_testlib.py
- `ARTIFACT_KIND_INSTALL_MANIFEST` -> runtime/compatibility/migration_lifecycle.py, tools/validators/compatibility/migration_lifecycle.py
- `ARTIFACT_KIND_INSTALL_PLAN` -> runtime/compatibility/migration_lifecycle.py, tools/validators/compatibility/migration_lifecycle.py
- `ARTIFACT_KIND_INSTANCE_MANIFEST` -> runtime/compatibility/migration_lifecycle.py, tools/validators/compatibility/migration_lifecycle.py
- `ARTIFACT_KIND_LOGIC_PROGRAM` -> tools/package/libraries/artifact/__init__.py, tools/package/libraries/artifact/artifact_validator.py
- `ARTIFACT_KIND_NEGOTIATION_RECORD` -> runtime/compatibility/migration_lifecycle.py, tools/validators/compatibility/migration_lifecycle.py
- `ARTIFACT_KIND_PACK` -> tools/release/release_manifest_engine.py, tools/validators/security/trust/__init__.py
- `ARTIFACT_KIND_PACK_LOCK` -> runtime/compatibility/migration_lifecycle.py, tools/validators/compatibility/migration_lifecycle.py
- `ARTIFACT_KIND_PROCESS_DEFINITION` -> tools/package/libraries/artifact/__init__.py, tools/package/libraries/artifact/artifact_validator.py
- `ARTIFACT_KIND_PROFILE_BUNDLE` -> runtime/compatibility/migration_lifecycle.py, tools/package/libraries/artifact/__init__.py, tools/package/libraries/artifact/artifact_validator.py, tools/validators/compatibility/migration_lifecycle.py
- `ARTIFACT_KIND_RELEASE_INDEX` -> runtime/compatibility/migration_lifecycle.py, tools/validators/compatibility/migration_lifecycle.py, tools/validators/security/trust/__init__.py
- `ARTIFACT_KIND_RELEASE_MANIFEST` -> runtime/compatibility/migration_lifecycle.py, tools/validators/compatibility/migration_lifecycle.py, tools/validators/security/trust/__init__.py

## Unknown Domains

- `unknown.root` :: `.`

## Circular Dependencies

- apps.client.local_server -> apps.server -> archive -> game.domain.embodiment.tools -> runtime.compatibility.shims -> runtime.network.server -> runtime.shell -> runtime.shell.command -> runtime.shell.ipc -> runtime.shell.server -> runtime.shell.supervisor -> runtime.shell.tui -> runtime.storage -> runtime.storage.server.persistence -> runtime.ui -> runtime.ui.client -> runtime.ui.client.interaction -> tools.audit -> tools.audit.review -> tools.codegen.shell -> tools.domain -> tools.domain.astronomy -> tools.domain.chemistry -> tools.domain.electricity -> tools.domain.embodiment -> tools.domain.fluids -> tools.domain.logic -> tools.domain.pollution -> tools.domain.processes -> tools.domain.systems -> tools.domain.thermal -> tools.domain.time -> tools.domain.worldgen -> tools.domain.worldgen.earth_stress -> tools.export -> tools.package.compatibility -> tools.package.launcher -> tools.package.libraries.artifact -> tools.package.libraries.export -> tools.package.libraries.install -> tools.package.libraries.instance -> tools.package.libraries.provides -> tools.package.libraries.save -> tools.package.libraries.store -> tools.package.libraries.stress -> tools.package.setup -> tools.performance -> tools.performance.envelope -> tools.release -> tools.release.dist -> tools.release.mvp -> tools.repo.dev.impact_graph -> tools.repo.governance -> tools.repo.governance.ir -> tools.repo.governance.planning -> tools.repo.governance.proof -> tools.repo.governance.view -> tools.repo.meta.audit -> tools.repo.meta.compile -> tools.repo.meta.compute -> tools.repo.meta.explain -> tools.repo.meta.instrumentation -> tools.repo.meta.profile -> tools.repo.meta.provenance -> tools.repo.meta.reference -> tools.repo.models -> tools.repo.specs -> tools.scripts.ci -> tools.scripts.dev -> tools.test.network -> tools.test.server -> tools.validators -> tools.validators.compatibility -> tools.validators.compatibility.descriptor -> tools.validators.compatibility.negotiation -> tools.validators.compatibility.shims -> tools.validators.core.flow -> tools.validators.core.graph -> tools.validators.core.hazards -> tools.validators.core.schedule -> tools.validators.domain.geology -> tools.validators.engine -> tools.validators.identity -> tools.validators.modding -> tools.validators.network.anti_cheat -> tools.validators.network.policies -> tools.validators.network.srz -> tools.validators.network.testing -> tools.validators.package.compatibility_payload -> tools.validators.safety -> tools.validators.security.model -> tools.validators.security.trust -> tools.validators.shell -> tools.validators.stability -> tools.validators.suite -> tools.xstack -> tools.xstack.auditx -> tools.xstack.auditx.analyzers -> tools.xstack.auditx.output -> tools.xstack.cache_store -> tools.xstack.ci -> tools.xstack.compatx -> tools.xstack.compatx.core -> tools.xstack.controlx -> tools.xstack.controlx.core -> tools.xstack.core -> tools.xstack.extensions -> tools.xstack.pack_contrib -> tools.xstack.pack_loader -> tools.xstack.packagingx -> tools.xstack.performx -> tools.xstack.registry_compile -> tools.xstack.repox -> tools.xstack.securex -> tools.xstack.sessionx -> tools.xstack.testx -> tools.xstack.testx.tests
- apps.workbench.module.tooling.editor -> apps.workbench.module.ui.editor.user -> tools.codegen.ui.tool_editor.gen
- archive.legacy._orphaned.legacy_source_game.game -> archive.legacy._orphaned.legacy_source_game.game.runtime -> archive.legacy._orphaned.legacy_source_game.game.ui
- archive.legacy.engine_modules_engine.engine.render -> archive.legacy.engine_modules_engine.engine.render.dx11 -> archive.legacy.engine_modules_engine.engine.render.dx9 -> archive.legacy.engine_modules_engine.engine.render.gl2
- archive.legacy.engine_modules_engine.engine.render.api -> archive.legacy.engine_modules_engine.engine.render.api.core -> archive.legacy.engine_modules_engine.engine.render.dx.dx9 -> archive.legacy.engine_modules_engine.engine.render.soft.core -> archive.legacy.engine_modules_engine.engine.render.soft.targets.null
- archive.legacy.engine_modules_engine.engine.trans.compile -> archive.legacy.engine_modules_engine.engine.trans.model
- archive.legacy.setup_core_setup.setup.core -> archive.legacy.setup_core_setup.setup.core.log
- engine.execution.budgets -> engine.execution.ir -> engine.execution.scheduler -> engine.kernel -> engine.replay -> engine.state.graph -> engine.state.graph.part -> game.domain.agent -> game.domain.ai -> game.domain.build -> game.domain.economy -> game.domain.environment -> game.domain.hydrology -> game.domain.job -> game.domain.mobility.vehicle -> game.domain.research -> game.domain.resource -> game.domain.scale -> game.domain.simulation -> game.domain.simulation.act -> game.domain.simulation.lod -> game.domain.simulation.pkt -> game.domain.structure -> game.domain.transport -> game.rule.policy -> game.world -> game.world.frame -> runtime.network -> runtime.package.content
- engine.include.domino -> engine.include.domino.core -> game.include.domino.world -> runtime.include.domino
- engine.include.domino.ecs -> engine.include.domino.execution
- game.domain.geology.worldgen -> game.domain.worldgen.earth -> game.domain.worldgen.earth.material -> game.domain.worldgen.earth.sky -> game.domain.worldgen.earth.water -> game.domain.worldgen.earth.wind -> game.domain.worldgen.galaxy -> game.domain.worldgen.mw -> game.domain.worldgen.refinement
- game.domain.logic.compile -> game.domain.logic.debug -> game.domain.logic.eval -> game.domain.logic.protocol -> game.domain.logic.timing
- game.domain.materials -> game.domain.materials.maintenance
- game.domain.processes -> game.domain.processes.capsules -> game.domain.processes.software
- game.domain.systems -> game.domain.systems.certification -> game.domain.systems.macro -> game.domain.systems.reliability
- game.include.dominium -> game.include.dominium.agents -> game.include.dominium.execution -> game.include.dominium.physical
- game.include.dominium.city -> game.include.dominium.infrastructure
- runtime.compatibility -> runtime.compatibility.descriptor
- runtime.platform.system -> runtime.platform.system.input

