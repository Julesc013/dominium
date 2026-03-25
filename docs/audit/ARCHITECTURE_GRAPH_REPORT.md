Status: DERIVED
Last Reviewed: 2026-03-26
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI
Replacement Target: XI-1 architectural convergence plan

# Architecture Graph Report

- concept_count: `316`
- module_count: `1743`
- duplicate_symbol_signal_count: `4143`
- unknown_domain_module_count: `439`
- circular_dependency_count: `16`

## Duplicate Signals

- `ALLOWED_CONTROL_IR_OP_TYPES` -> src/control/__init__.py, src/control/ir/__init__.py, src/control/ir/control_ir_verifier.py
- `ALL_REGISTRY_PATHS` -> src/meta/stability/__init__.py, src/meta/stability/stability_scope.py, src/meta/stability/stability_validator.py
- `ANCHOR_REASON_INTERVAL` -> src/time/__init__.py, src/time/epoch_anchor_engine.py
- `ANCHOR_REASON_MIGRATION` -> src/time/__init__.py, src/time/epoch_anchor_engine.py
- `ANCHOR_REASON_SAVE` -> src/time/__init__.py, src/time/epoch_anchor_engine.py
- `ARCHIVE_POLICY_ID` -> src/governance/__init__.py, src/governance/governance_profile.py
- `ARTIFACT_DEGRADE_BEST_EFFORT` -> src/lib/artifact/__init__.py, src/lib/artifact/artifact_validator.py
- `ARTIFACT_DEGRADE_MODE_VALUES` -> src/lib/artifact/__init__.py, src/lib/artifact/artifact_validator.py
- `ARTIFACT_DEGRADE_READ_ONLY_ONLY` -> src/lib/artifact/__init__.py, src/lib/artifact/artifact_validator.py
- `ARTIFACT_DEGRADE_STRICT_REFUSE` -> src/lib/artifact/__init__.py, src/lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_BLUEPRINT` -> src/compat/migration_lifecycle.py, src/lib/artifact/__init__.py, src/lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_IDS` -> src/compat/migration_lifecycle.py, tools/xstack/testx/tests/migration_lifecycle_testlib.py
- `ARTIFACT_KIND_LOGIC_PROGRAM` -> src/lib/artifact/__init__.py, src/lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_PACK` -> src/release/release_manifest_engine.py, src/security/trust/__init__.py
- `ARTIFACT_KIND_PROCESS_DEFINITION` -> src/lib/artifact/__init__.py, src/lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_PROFILE_BUNDLE` -> src/compat/migration_lifecycle.py, src/lib/artifact/__init__.py, src/lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_RELEASE_INDEX` -> src/compat/migration_lifecycle.py, src/security/trust/__init__.py
- `ARTIFACT_KIND_RELEASE_MANIFEST` -> src/compat/migration_lifecycle.py, src/security/trust/__init__.py
- `ARTIFACT_KIND_RESOURCE_PACK_STUB` -> src/lib/artifact/__init__.py, src/lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_SYSTEM_TEMPLATE` -> src/lib/artifact/__init__.py, src/lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_VALUES` -> src/lib/artifact/__init__.py, src/lib/artifact/artifact_validator.py
- `ARTIFACT_KIND_VIEW_PRESET` -> src/lib/artifact/__init__.py, src/lib/artifact/artifact_validator.py
- `AnalysisGraph` -> tools/auditx/graph/__init__.py, tools/auditx/graph/analysis_graph.py
- `AppShellIPCEndpointServer` -> src/appshell/ipc/__init__.py, src/appshell/ipc/ipc_endpoint_server.py
- `BASELINE_DOC_REL` -> tools/compat/migration_lifecycle_common.py, tools/engine/concurrency_contract_common.py, tools/engine/numeric_discipline_common.py, tools/governance/governance_model_common.py

## Unknown Domains

- `unknown.github.workflows` :: `.github/workflows`
- `unknown.ide` :: `ide`
- `unknown.ide.manifests` :: `ide/manifests`
- `unknown.ide.manifests.projection_manifest_examples` :: `ide/manifests/projection_manifest_examples`
- `unknown.labs` :: `labs`
- `unknown.legacy` :: `legacy`
- `unknown.legacy._orphaned.engine_has_launcher_module.launcher` :: `legacy/_orphaned/engine_has_launcher_module/launcher`
- `unknown.legacy._orphaned.legacy_source_common.common` :: `legacy/_orphaned/legacy_source_common/common`
- `unknown.legacy._orphaned.legacy_source_game.game` :: `legacy/_orphaned/legacy_source_game/game`
- `unknown.legacy._orphaned.legacy_source_game.game._legacy.sdk` :: `legacy/_orphaned/legacy_source_game/game/_legacy/sdk`
- `unknown.legacy._orphaned.legacy_source_game.game.cli` :: `legacy/_orphaned/legacy_source_game/game/cli`
- `unknown.legacy._orphaned.legacy_source_game.game.cli.server` :: `legacy/_orphaned/legacy_source_game/game/cli/server`
- `unknown.legacy._orphaned.legacy_source_game.game.content` :: `legacy/_orphaned/legacy_source_game/game/content`
- `unknown.legacy._orphaned.legacy_source_game.game.core` :: `legacy/_orphaned/legacy_source_game/game/core`
- `unknown.legacy._orphaned.legacy_source_game.game.core.app_mode` :: `legacy/_orphaned/legacy_source_game/game/core/app_mode`
- `unknown.legacy._orphaned.legacy_source_game.game.core.client` :: `legacy/_orphaned/legacy_source_game/game/core/client`
- `unknown.legacy._orphaned.legacy_source_game.game.core.client.input` :: `legacy/_orphaned/legacy_source_game/game/core/client/input`
- `unknown.legacy._orphaned.legacy_source_game.game.frontends.gui` :: `legacy/_orphaned/legacy_source_game/game/frontends/gui`
- `unknown.legacy._orphaned.legacy_source_game.game.frontends.headless` :: `legacy/_orphaned/legacy_source_game/game/frontends/headless`
- `unknown.legacy._orphaned.legacy_source_game.game.frontends.tui` :: `legacy/_orphaned/legacy_source_game/game/frontends/tui`
- `unknown.legacy._orphaned.legacy_source_game.game.gui` :: `legacy/_orphaned/legacy_source_game/game/gui`
- `unknown.legacy._orphaned.legacy_source_game.game.gui.dom_sdl` :: `legacy/_orphaned/legacy_source_game/game/gui/dom_sdl`
- `unknown.legacy._orphaned.legacy_source_game.game.rules` :: `legacy/_orphaned/legacy_source_game/game/rules`
- `unknown.legacy._orphaned.legacy_source_game.game.runtime` :: `legacy/_orphaned/legacy_source_game/game/runtime`
- `unknown.legacy._orphaned.legacy_source_game.game.ui` :: `legacy/_orphaned/legacy_source_game/game/ui`

## Circular Dependencies

- apps.server.net -> apps.server.persistence
- apps.setup.packages.scripts.packaging -> tools.appshell -> tools.astro -> tools.audit -> tools.auditx -> tools.auditx.analyzers -> tools.auditx.output -> tools.chem -> tools.compat -> tools.convergence -> tools.dist -> tools.earth -> tools.electric -> tools.embodiment -> tools.engine -> tools.geo -> tools.governance -> tools.launcher -> tools.lib -> tools.logic -> tools.meta -> tools.mvp -> tools.net -> tools.perf -> tools.physics -> tools.pollution -> tools.process -> tools.release -> tools.review -> tools.security -> tools.server -> tools.setup -> tools.system -> tools.time -> tools.worldgen -> tools.xstack -> tools.xstack.auditx -> tools.xstack.cache_store -> tools.xstack.controlx -> tools.xstack.core -> tools.xstack.extensions -> tools.xstack.pack_contrib -> tools.xstack.pack_loader -> tools.xstack.packagingx -> tools.xstack.performx -> tools.xstack.registry_compile -> tools.xstack.repox -> tools.xstack.securex -> tools.xstack.sessionx -> tools.xstack.testx -> tools.xstack.testx.tests -> unknown.src.appshell -> unknown.src.appshell.commands -> unknown.src.appshell.diag -> unknown.src.appshell.ipc -> unknown.src.appshell.logging -> unknown.src.appshell.supervisor -> unknown.src.appshell.tui -> unknown.src.client.interaction -> unknown.src.client.local_server -> unknown.src.client.net -> unknown.src.client.ui -> unknown.src.compat.shims -> unknown.src.diag -> unknown.src.embodiment.body -> unknown.src.embodiment.tools -> unknown.src.lib.export -> unknown.src.lib.instance -> unknown.src.lib.store -> unknown.src.logic -> unknown.src.logic.compile -> unknown.src.logic.debug -> unknown.src.logic.eval -> unknown.src.logic.protocol -> unknown.src.logic.timing -> unknown.src.meta -> unknown.src.meta.provenance -> unknown.src.meta.reference -> unknown.src.mobility -> unknown.src.mobility.micro -> unknown.src.net.anti_cheat -> unknown.src.net.policies -> unknown.src.net.srz -> unknown.src.packs.compat -> unknown.src.physics -> unknown.src.physics.energy -> unknown.src.reality.ledger -> unknown.src.runtime -> unknown.src.server -> unknown.src.server.net -> unknown.src.server.runtime -> unknown.src.time -> unknown.src.tools -> unknown.src.ui -> unknown.src.universe -> unknown.src.validation -> worldgen.core
- engine.include.domino -> engine.include.domino.core -> engine.include.domino.world
- engine.include.domino.ecs -> engine.include.domino.execution
- engine.modules.agent -> engine.modules.ai -> engine.modules.build -> engine.modules.content -> engine.modules.core -> engine.modules.core.graph -> engine.modules.core.graph.part -> engine.modules.econ -> engine.modules.env -> engine.modules.execution.budgets -> engine.modules.execution.ir -> engine.modules.execution.scheduler -> engine.modules.hydro -> engine.modules.job -> engine.modules.net -> engine.modules.policy -> engine.modules.replay -> engine.modules.res -> engine.modules.research -> engine.modules.scale -> engine.modules.sim -> engine.modules.sim.act -> engine.modules.sim.lod -> engine.modules.sim.pkt -> engine.modules.struct -> engine.modules.trans -> engine.modules.vehicle -> engine.modules.world -> engine.modules.world.frame
- engine.modules.system -> engine.modules.system.input
- game.core.execution -> game.include.dominium -> game.include.dominium.agents -> game.include.dominium.execution -> game.include.dominium.physical -> game.include.dominium.rules.agents
- game.include.dominium.rules.city -> game.include.dominium.rules.infrastructure
- tools.tool_editor -> tools.tool_editor.ui.gen -> tools.tool_editor.ui.user
- tools.validate -> tools.validation
- unknown.src.appshell.paths -> unknown.src.compat -> unknown.src.compat.descriptor -> unknown.src.lib.install -> unknown.src.release
- unknown.src.client.render -> unknown.src.client.render.renderers -> unknown.src.field -> unknown.src.fields -> unknown.src.geo -> unknown.src.geo.overlay -> unknown.src.geo.path -> unknown.src.geo.projection -> unknown.src.geo.worldgen -> unknown.src.worldgen.earth -> unknown.src.worldgen.earth.material -> unknown.src.worldgen.earth.sky -> unknown.src.worldgen.earth.water -> unknown.src.worldgen.earth.wind -> unknown.src.worldgen.galaxy -> unknown.src.worldgen.mw -> unknown.src.worldgen.refinement
- unknown.src.control -> unknown.src.control.ir -> unknown.src.control.planning
- unknown.src.materials -> unknown.src.materials.maintenance
- unknown.src.process -> unknown.src.process.capsules -> unknown.src.process.software
- unknown.src.system -> unknown.src.system.certification -> unknown.src.system.macro -> unknown.src.system.reliability

