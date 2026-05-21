dependency direction validation: PASS (16579 files scanned, 0 violations, 68 warnings)
warning: apps/server/server_boot.py:9: exception_applied: apps->tools import tools.validators.modding
  product/runtime/engine/game code must not depend on tools
warning: apps/server/server_boot.py:10: exception_applied: apps->tools import tools.validators.network.policies.policy_server_authoritative
  product/runtime/engine/game code must not depend on tools
warning: apps/server/server_boot.py:24: exception_applied: apps->tools import tools.release.mvp.runtime_bundle
  product/runtime/engine/game code must not depend on tools
warning: apps/server/server_boot.py:31: exception_applied: apps->tools import tools.xstack.sessionx.creator
  product/runtime/engine/game code must not depend on tools
warning: apps/server/server_boot.py:38: exception_applied: apps->tools import tools.xstack.sessionx.runner
  product/runtime/engine/game code must not depend on tools
warning: apps/server/server_boot.py:49: exception_applied: apps->tools import tools.xstack.sessionx.universe_physics
  product/runtime/engine/game code must not depend on tools
warning: apps/server/server_console.py:12: unlisted_active_dependency: apps->engine import engine.time
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: apps/workbench/module/domain/item/main_item_editor.cpp:21: unlisted_active_dependency: apps->content include content/d_content_schema.h
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: apps/workbench/module/domain/technology/main_tech_editor.cpp:21: unlisted_active_dependency: apps->content include content/d_content_schema.h
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: apps/workbench/module/domain/transport/main_transport_editor.cpp:21: unlisted_active_dependency: apps->content include content/d_content_schema.h
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: apps/workbench/module/pack/editor/main_pack_editor.cpp:21: unlisted_active_dependency: apps->content include content/d_content_schema.h
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: apps/workbench/module/policy/editor/main_policy_editor.cpp:21: unlisted_active_dependency: apps->content include content/d_content_schema.h
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: apps/workbench/module/process/editor/main_process_editor.cpp:21: unlisted_active_dependency: apps->content include content/d_content_schema.h
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: apps/workbench/module/schema/blueprint/main_blueprint_editor.cpp:21: unlisted_active_dependency: apps->content include content/d_content_schema.h
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: apps/workbench/module/schema/structure/main_struct_editor.cpp:21: unlisted_active_dependency: apps->content include content/d_content_schema.h
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: game/domain/chemistry/degradation/degradation_engine.py:7: unlisted_active_dependency: game->runtime import runtime.capability.effects
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: game/domain/embodiment/tools/logic_tool.py:7: unlisted_active_dependency: game->runtime import runtime.compatibility
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: game/domain/embodiment/tools/teleport_tool.py:8: unlisted_active_dependency: game->runtime import runtime.ui.client.teleport_controller
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: game/domain/fluids/network/fluid_network_engine.py:7: unlisted_active_dependency: game->runtime import runtime.capability.effects
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: game/domain/inspection/inspection_engine.py:7: unlisted_active_dependency: game->runtime import runtime.capability.fidelity
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: game/domain/interaction/action_surface_engine.py:7: unlisted_active_dependency: game->runtime import runtime.capability.core
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: game/domain/materials/blueprint_engine.py:9: unlisted_active_dependency: game->runtime import runtime.compatibility.data_format_loader
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: game/domain/materials/commitments/commitment_engine.py:7: unlisted_active_dependency: game->runtime import runtime.capability.fidelity
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: game/domain/materials/materialization/materialization_engine.py:7: unlisted_active_dependency: game->runtime import runtime.capability.fidelity
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: game/domain/mechanics/structural_graph_engine.py:7: unlisted_active_dependency: game->runtime import runtime.capability.effects
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: game/domain/signals/institutions/dispatch_engine.py:9: unlisted_active_dependency: game->runtime import runtime.capability.control_plane_engine
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: game/domain/thermal/network/thermal_network_engine.py:7: unlisted_active_dependency: game->runtime import runtime.capability.effects
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/network/server/loopback_transport.py:18: exception_applied: runtime->tools import tools.validators.network.policies.policy_server_authoritative
  forbidden high-confidence dependency direction
warning: runtime/render/backend/representation_resolver.py:8: unlisted_active_dependency: runtime->game import game.domain.geology
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/render/backend/software_renderer.py:11: unlisted_active_dependency: runtime->game import game.domain.geology
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/shell/command/command_engine.py:49: exception_applied: runtime->tools import tools.release
  forbidden high-confidence dependency direction
warning: runtime/shell/command/command_engine.py:55: exception_applied: runtime->tools import tools
  forbidden high-confidence dependency direction
warning: runtime/shell/command/command_engine.py:257: exception_applied: runtime->tools import tools.package.setup
  forbidden high-confidence dependency direction
warning: runtime/shell/command/command_engine.py:564: exception_applied: runtime->tools import tools.validators.suite
  forbidden high-confidence dependency direction
warning: runtime/shell/compat_adapter.py:6: exception_applied: runtime->tools import tools.release
  forbidden high-confidence dependency direction
warning: runtime/shell/pack_verifier_adapter.py:8: exception_applied: runtime->tools import tools.validators.package.compatibility_payload
  forbidden high-confidence dependency direction
warning: runtime/shell/pack_verifier_adapter.py:9: exception_applied: runtime->tools import tools.validators.security.trust
  forbidden high-confidence dependency direction
warning: runtime/shell/server/tick_loop.py:8: exception_applied: runtime->tools import tools.validators.network.policies.policy_server_authoritative
  forbidden high-confidence dependency direction
warning: runtime/storage/gc_engine.py:9: exception_applied: runtime->tools import tools.package.libraries.install.install_validator
  forbidden high-confidence dependency direction
warning: runtime/storage/gc_engine.py:12: exception_applied: runtime->tools import tools.package.libraries.store.reachability_engine
  forbidden high-confidence dependency direction
warning: runtime/ui/client/inspect_panels.py:8: exception_applied: runtime->tools import tools.validators.domain.geology.tool_explain_property_origin
  forbidden high-confidence dependency direction
warning: runtime/ui/client/interaction/affordance_generator.py:9: unlisted_active_dependency: runtime->game import game.domain.interaction
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/interaction/inspection_overlays.py:9: unlisted_active_dependency: runtime->game import game.domain.materials.blueprint_engine
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/interaction/interaction_dispatch.py:9: exception_applied: runtime->tools import tools.validators.network.anti_cheat.anti_cheat_engine
  forbidden high-confidence dependency direction
warning: runtime/ui/client/interaction/interaction_dispatch.py:13: exception_applied: runtime->tools import tools.validators.network.policies.policy_lockstep
  forbidden high-confidence dependency direction
warning: runtime/ui/client/interaction/interaction_dispatch.py:14: exception_applied: runtime->tools import tools.validators.network.policies.policy_server_authoritative
  forbidden high-confidence dependency direction
warning: runtime/ui/client/interaction/interaction_dispatch.py:15: exception_applied: runtime->tools import tools.validators.network.policies.policy_srz_hybrid
  forbidden high-confidence dependency direction
warning: runtime/ui/client/interaction/interaction_dispatch.py:17: exception_applied: runtime->tools import tools.xstack.sessionx.boundary_debug
  forbidden high-confidence dependency direction
warning: runtime/ui/client/interaction/interaction_dispatch.py:19: unlisted_active_dependency: runtime->game import game.domain.interaction.task
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/interaction/interaction_dispatch.py:777: exception_applied: runtime->tools import tools.xstack.sessionx.process_runtime
  forbidden high-confidence dependency direction
warning: runtime/ui/client/interaction/preview_generator.py:9: unlisted_active_dependency: runtime->game import game.domain.materials.blueprint_engine
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/map_views.py:11: unlisted_active_dependency: runtime->game import game.domain.geology
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/teleport_controller.py:8: unlisted_active_dependency: runtime->game import game.domain.geology.worldgen
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/teleport_controller.py:9: unlisted_active_dependency: runtime->game import game.domain.worldgen.refinement.refinement_scheduler
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/teleport_controller.py:10: unlisted_active_dependency: runtime->game import game.domain.worldgen.mw.sol_anchor
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/teleport_controller.py:11: unlisted_active_dependency: runtime->game import game.domain.worldgen.mw.system_query_engine
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/teleport_controller.py:17: exception_applied: runtime->tools import tools.release.mvp.runtime_bundle
  forbidden high-confidence dependency direction
warning: runtime/ui/client/viewer_shell.py:7: unlisted_active_dependency: runtime->game import game.domain.astronomy
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/viewer_shell.py:9: unlisted_active_dependency: runtime->game import game.domain.embodiment
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/viewer_shell.py:24: unlisted_active_dependency: runtime->game import game.domain.geology
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/viewer_shell.py:25: unlisted_active_dependency: runtime->game import game.domain.worldgen.galaxy
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/viewer_shell.py:26: unlisted_active_dependency: runtime->game import game.domain.worldgen.earth.lighting
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/viewer_shell.py:27: unlisted_active_dependency: runtime->game import game.domain.worldgen.earth.sky
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/viewer_shell.py:28: unlisted_active_dependency: runtime->game import game.domain.worldgen.earth.water
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/viewer_shell.py:29: unlisted_active_dependency: runtime->game import game.domain.worldgen.refinement.refinement_scheduler
  dependency is not listed as an allowed broad edge; review before stable promotion
warning: runtime/ui/client/viewer_shell.py:35: exception_applied: runtime->tools import tools.release.mvp.runtime_bundle
  forbidden high-confidence dependency direction
warning: runtime/ui/ui_model.py:20: exception_applied: runtime->tools import tools.package.libraries.instance
  forbidden high-confidence dependency direction
warning: runtime/ui/ui_model.py:21: exception_applied: runtime->tools import tools.package.libraries.save
  forbidden high-confidence dependency direction
