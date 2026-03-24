Status: DERIVED
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: release surface index regenerated from TOOL-SURFACE-0 tooling

# Tool Surface Map

Source: `data/audit/repo_inventory.json` + `src/tools/tool_surface_adapter.py`

- Wrapped commands: `120`
- Alias commands: `12`
- Subprocess adapters: `108`
- Surface fingerprint: `6eaf0d4aaedb87847485ab88b1e4901d0a701c593631d33cc79399888cbb49cd`

## `geo`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `tools/geo/tool_explain_property_origin.py` | tool.utility | `dom geo explain-property-origin` | `dom.geo.explain-property-origin.v1` | `python_subprocess` | - |
| `tools/geo/tool_generate_geo_stress.py` | tool.utility | `dom geo generate-geo-stress` | `dom.geo.generate-geo-stress.v1` | `python_subprocess` | - |
| `tools/geo/tool_replay_field_geo_window.py` | tool.utility | `dom geo replay-field-geo-window` | `dom.geo.replay-field-geo-window.v1` | `python_subprocess` | - |
| `tools/geo/tool_replay_frame_window.py` | tool.utility | `dom geo replay-frame-window` | `dom.geo.replay-frame-window.v1` | `python_subprocess` | - |
| `tools/geo/tool_replay_geo_window.py` | tool.utility | `dom geo replay-geo-window` | `dom.geo.replay-geo-window.v1` | `python_subprocess` | - |
| `tools/geo/tool_replay_geometry_window.py` | tool.utility | `dom geo replay-geometry-window` | `dom.geo.replay-geometry-window.v1` | `python_subprocess` | - |
| `tools/geo/tool_replay_overlay_merge.py` | tool.utility | `dom geo replay-overlay-merge` | `dom.geo.replay-overlay-merge.v1` | `python_subprocess` | - |
| `tools/geo/tool_replay_path_request.py` | tool.utility | `dom geo replay-path-request` | `dom.geo.replay-path-request.v1` | `python_subprocess` | - |
| `tools/geo/tool_replay_view_window.py` | tool.utility | `dom geo replay-view-window` | `dom.geo.replay-view-window.v1` | `python_subprocess` | - |
| `tools/geo/tool_replay_worldgen_cell.py` | tool.utility | `dom geo replay-worldgen-cell` | `dom.geo.replay-worldgen-cell.v1` | `python_subprocess` | - |
| `tools/geo/tool_run_geo_stress.py` | tool.utility | `dom geo run-geo-stress` | `dom.geo.run-geo-stress.v1` | `python_subprocess` | - |
| `tools/geo/tool_verify_id_stability.py` | tool.utility | `dom geo verify-id-stability` | `dom.geo.verify-id-stability.v1` | `python_subprocess` | - |
| `tools/geo/tool_verify_metric_stability.py` | tool.utility | `dom geo verify-metric-stability` | `dom.geo.verify-metric-stability.v1` | `python_subprocess` | - |
| `tools/geo/tool_verify_overlay_identity.py` | tool.utility | `dom geo verify-overlay-identity` | `dom.geo.verify-overlay-identity.v1` | `python_subprocess` | - |
| `tools/geo/tool_verify_sol_pin_overlay.py` | tool.utility | `dom geo verify-sol-pin-overlay` | `dom.geo.verify-sol-pin-overlay.v1` | `python_subprocess` | - |

## `worldgen`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `tools/worldgen/tool_generate_worldgen_baseline.py` | Generate the Omega worldgen lock baseline snapshot | `dom worldgen generate-worldgen-baseline` | `dom.worldgen.generate-worldgen-baseline.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_climate_window.py` | tool.utility | `dom worldgen replay-climate-window` | `dom.worldgen.replay-climate-window.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_galaxy_objects.py` | tool.utility | `dom worldgen replay-galaxy-objects` | `dom.worldgen.replay-galaxy-objects.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_galaxy_proxies.py` | tool.utility | `dom worldgen replay-galaxy-proxies` | `dom.worldgen.replay-galaxy-proxies.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_hydrology_window.py` | tool.utility | `dom worldgen replay-hydrology-window` | `dom.worldgen.replay-hydrology-window.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_illumination_view.py` | tool.utility | `dom worldgen replay-illumination-view` | `dom.worldgen.replay-illumination-view.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_material_proxy_window.py` | tool.utility | `dom worldgen replay-material-proxy-window` | `dom.worldgen.replay-material-proxy-window.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_refinement_window.py` | tool.utility | `dom worldgen replay-refinement-window` | `dom.worldgen.replay-refinement-window.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_sky_view.py` | tool.utility | `dom worldgen replay-sky-view` | `dom.worldgen.replay-sky-view.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_system_instantiation.py` | tool.utility | `dom worldgen replay-system-instantiation` | `dom.worldgen.replay-system-instantiation.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_system_l2.py` | tool.utility | `dom worldgen replay-system-l2` | `dom.worldgen.replay-system-l2.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_tide_window.py` | tool.utility | `dom worldgen replay-tide-window` | `dom.worldgen.replay-tide-window.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_water_view.py` | tool.utility | `dom worldgen replay-water-view` | `dom.worldgen.replay-water-view.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_wind_window.py` | tool.utility | `dom worldgen replay-wind-window` | `dom.worldgen.replay-wind-window.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_run_refinement_stress.py` | tool.utility | `dom worldgen run-refinement-stress` | `dom.worldgen.run-refinement-stress.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_verify_earth_surface.py` | tool.utility | `dom worldgen verify-earth-surface` | `dom.worldgen.verify-earth-surface.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_verify_worldgen_lock.py` | Verify the Omega worldgen lock against the committed baseline snapshot | `dom worldgen verify-worldgen-lock` | `dom.worldgen.verify-worldgen-lock.v1` | `python_subprocess` | - |

## `earth`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `tools/earth/tool_generate_earth_mvp_stress.py` | tool.utility | `dom earth generate-earth-mvp-stress` | `dom.earth.generate-earth-mvp-stress.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_climate_window.py` | tool.utility | `dom earth replay-climate-window` | `dom.earth.replay-climate-window.v1` | `python_subprocess` | - |
| `tools/earth/tool_replay_earth_physics_window.py` | tool.utility | `dom earth replay-earth-physics-window` | `dom.earth.replay-earth-physics-window.v1` | `python_subprocess` | - |
| `tools/earth/tool_replay_earth_view_window.py` | tool.utility | `dom earth replay-earth-view-window` | `dom.earth.replay-earth-view-window.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_hydrology_window.py` | tool.utility | `dom earth replay-hydrology-window` | `dom.earth.replay-hydrology-window.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_illumination_view.py` | tool.utility | `dom earth replay-illumination-view` | `dom.earth.replay-illumination-view.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_material_proxy_window.py` | tool.utility | `dom earth replay-material-proxy-window` | `dom.earth.replay-material-proxy-window.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_sky_view.py` | tool.utility | `dom earth replay-sky-view` | `dom.earth.replay-sky-view.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_tide_window.py` | tool.utility | `dom earth replay-tide-window` | `dom.earth.replay-tide-window.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_water_view.py` | tool.utility | `dom earth replay-water-view` | `dom.earth.replay-water-view.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_wind_window.py` | tool.utility | `dom earth replay-wind-window` | `dom.earth.replay-wind-window.v1` | `python_subprocess` | - |
| `tools/earth/tool_run_earth_mvp_stress.py` | tool.utility | `dom earth run-earth-mvp-stress` | `dom.earth.run-earth-mvp-stress.v1` | `python_subprocess` | - |

## `sol`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `tools/astro/tool_replay_illumination_view.py` | tool.utility | `dom sol replay-illumination-view` | `dom.sol.replay-illumination-view.v1` | `python_subprocess` | - |
| `tools/astro/tool_replay_orbit_view.py` | tool.utility | `dom sol replay-orbit-view` | `dom.sol.replay-orbit-view.v1` | `python_subprocess` | - |

## `gal`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `tools/worldgen/tool_replay_galaxy_objects.py` | tool.utility | `dom gal replay-galaxy-objects` | `dom.gal.replay-galaxy-objects.v1` | `python_subprocess` | - |
| `tools/worldgen/tool_replay_galaxy_proxies.py` | tool.utility | `dom gal replay-galaxy-proxies` | `dom.gal.replay-galaxy-proxies.v1` | `python_subprocess` | - |

## `logic`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `tools/logic/tool_generate_logic_stress.py` | tool.utility | `dom logic generate-logic-stress` | `dom.logic.generate-logic-stress.v1` | `python_subprocess` | - |
| `tools/logic/tool_replay_compiled_logic_window.py` | tool.utility | `dom logic replay-compiled-logic-window` | `dom.logic.replay-compiled-logic-window.v1` | `python_subprocess` | - |
| `tools/logic/tool_replay_fault_window.py` | tool.utility | `dom logic replay-fault-window` | `dom.logic.replay-fault-window.v1` | `python_subprocess` | - |
| `tools/logic/tool_replay_logic_window.py` | tool.utility | `dom logic replay-logic-window` | `dom.logic.replay-logic-window.v1` | `python_subprocess` | - |
| `tools/logic/tool_replay_protocol_window.py` | tool.utility | `dom logic replay-protocol-window` | `dom.logic.replay-protocol-window.v1` | `python_subprocess` | - |
| `tools/logic/tool_replay_timing_window.py` | tool.utility | `dom logic replay-timing-window` | `dom.logic.replay-timing-window.v1` | `python_subprocess` | - |
| `tools/logic/tool_replay_trace_window.py` | tool.utility | `dom logic replay-trace-window` | `dom.logic.replay-trace-window.v1` | `python_subprocess` | - |
| `tools/logic/tool_run_logic_compile_stress.py` | tool.utility | `dom logic run-logic-compile-stress` | `dom.logic.run-logic-compile-stress.v1` | `python_subprocess` | - |
| `tools/logic/tool_run_logic_debug_stress.py` | tool.utility | `dom logic run-logic-debug-stress` | `dom.logic.run-logic-debug-stress.v1` | `python_subprocess` | - |
| `tools/logic/tool_run_logic_eval_stress.py` | tool.utility | `dom logic run-logic-eval-stress` | `dom.logic.run-logic-eval-stress.v1` | `python_subprocess` | - |
| `tools/logic/tool_run_logic_fault_stress.py` | tool.utility | `dom logic run-logic-fault-stress` | `dom.logic.run-logic-fault-stress.v1` | `python_subprocess` | - |
| `tools/logic/tool_run_logic_protocol_stress.py` | tool.utility | `dom logic run-logic-protocol-stress` | `dom.logic.run-logic-protocol-stress.v1` | `python_subprocess` | - |
| `tools/logic/tool_run_logic_stress.py` | tool.utility | `dom logic run-logic-stress` | `dom.logic.run-logic-stress.v1` | `python_subprocess` | - |
| `tools/logic/tool_run_logic_timing_stress.py` | tool.utility | `dom logic run-logic-timing-stress` | `dom.logic.run-logic-timing-stress.v1` | `python_subprocess` | - |
| `tools/logic/tool_verify_compiled_vs_l1.py` | tool.utility | `dom logic verify-compiled-vs-l1` | `dom.logic.verify-compiled-vs-l1.v1` | `python_subprocess` | - |

## `sys`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `tools/system/tool_generate_sys_stress.py` | tool.utility | `dom sys generate-sys-stress` | `dom.sys.generate-sys-stress.v1` | `python_subprocess` | - |
| `tools/system/tool_replay_capsule_window.py` | tool.utility | `dom sys replay-capsule-window` | `dom.sys.replay-capsule-window.v1` | `python_subprocess` | - |
| `tools/system/tool_replay_certification_window.py` | tool.utility | `dom sys replay-certification-window` | `dom.sys.replay-certification-window.v1` | `python_subprocess` | - |
| `tools/system/tool_replay_sys_window.py` | tool.utility | `dom sys replay-sys-window` | `dom.sys.replay-sys-window.v1` | `python_subprocess` | - |
| `tools/system/tool_replay_system_failure_window.py` | tool.utility | `dom sys replay-system-failure-window` | `dom.sys.replay-system-failure-window.v1` | `python_subprocess` | - |
| `tools/system/tool_replay_tier_transitions.py` | tool.utility | `dom sys replay-tier-transitions` | `dom.sys.replay-tier-transitions.v1` | `python_subprocess` | - |
| `tools/system/tool_run_sys_stress.py` | tool.utility | `dom sys run-sys-stress` | `dom.sys.run-sys-stress.v1` | `python_subprocess` | - |
| `tools/system/tool_template_browser.py` | tool.utility | `dom sys template-browser` | `dom.sys.template-browser.v1` | `python_subprocess` | - |
| `tools/system/tool_verify_explain_determinism.py` | tool.utility | `dom sys verify-explain-determinism` | `dom.sys.verify-explain-determinism.v1` | `python_subprocess` | - |
| `tools/system/tool_verify_statevec_roundtrip.py` | tool.utility | `dom sys verify-statevec-roundtrip` | `dom.sys.verify-statevec-roundtrip.v1` | `python_subprocess` | - |
| `tools/system/tool_verify_template_reproducible.py` | tool.utility | `dom sys verify-template-reproducible` | `dom.sys.verify-template-reproducible.v1` | `python_subprocess` | - |

## `proc`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `tools/process/tool_generate_proc_stress.py` | tool.utility | `dom proc generate-proc-stress` | `dom.proc.generate-proc-stress.v1` | `python_subprocess` | - |
| `tools/process/tool_replay_capsule_window.py` | tool.utility | `dom proc replay-capsule-window` | `dom.proc.replay-capsule-window.v1` | `python_subprocess` | - |
| `tools/process/tool_replay_drift_window.py` | tool.utility | `dom proc replay-drift-window` | `dom.proc.replay-drift-window.v1` | `python_subprocess` | - |
| `tools/process/tool_replay_experiment_window.py` | tool.utility | `dom proc replay-experiment-window` | `dom.proc.replay-experiment-window.v1` | `python_subprocess` | - |
| `tools/process/tool_replay_maturity_window.py` | tool.utility | `dom proc replay-maturity-window` | `dom.proc.replay-maturity-window.v1` | `python_subprocess` | - |
| `tools/process/tool_replay_pipeline_window.py` | tool.utility | `dom proc replay-pipeline-window` | `dom.proc.replay-pipeline-window.v1` | `python_subprocess` | - |
| `tools/process/tool_replay_proc_window.py` | tool.utility | `dom proc replay-proc-window` | `dom.proc.replay-proc-window.v1` | `python_subprocess` | - |
| `tools/process/tool_replay_process_window.py` | tool.utility | `dom proc replay-process-window` | `dom.proc.replay-process-window.v1` | `python_subprocess` | - |
| `tools/process/tool_replay_qc_window.py` | tool.utility | `dom proc replay-qc-window` | `dom.proc.replay-qc-window.v1` | `python_subprocess` | - |
| `tools/process/tool_replay_quality_window.py` | tool.utility | `dom proc replay-quality-window` | `dom.proc.replay-quality-window.v1` | `python_subprocess` | - |
| `tools/process/tool_replay_reverse_engineering_window.py` | tool.utility | `dom proc replay-reverse-engineering-window` | `dom.proc.replay-reverse-engineering-window.v1` | `python_subprocess` | - |
| `tools/process/tool_run_proc_stress.py` | tool.utility | `dom proc run-proc-stress` | `dom.proc.run-proc-stress.v1` | `python_subprocess` | - |
| `tools/process/tool_verify_proc_compaction.py` | tool.utility | `dom proc verify-proc-compaction` | `dom.proc.verify-proc-compaction.v1` | `python_subprocess` | - |

## `pack`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `appshell:tool.attach_console_stub:packs build-lock` | Verify packs offline and emit a deterministic pack lock plus compatibility report. | `dom pack build-lock` | `dom.pack.build-lock.v1` | `appshell_alias` | - |
| `tools/pack/capability_inspect.py` | packaging.install | `dom pack capability-inspect` | `dom.pack.capability-inspect.v1` | `python_subprocess` | - |
| `appshell:tool.attach_console_stub:packs list` | List available pack manifests in deterministic order. | `dom pack list` | `dom.pack.list.v1` | `appshell_alias` | - |
| `tools/pack/migrate_capability_gating.py` | packaging.install | `dom pack migrate-capability-gating` | `dom.pack.migrate-capability-gating.v1` | `python_subprocess` | - |
| `tools/pack/pack_validate.py` | packaging.install | `dom pack validate-manifest` | `dom.pack.validate-manifest.v1` | `python_subprocess` | - |
| `appshell:tool.attach_console_stub:packs verify` | Run the offline pack compatibility verification pipeline. | `dom pack verify` | `dom.pack.verify.v1` | `appshell_alias` | - |

## `lib`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `tools/lib/tool_generate_lib_stress.py` | unknown | `dom lib generate-lib-stress` | `dom.lib.generate-lib-stress.v1` | `python_subprocess` | - |
| `tools/lib/tool_replay_save_open.py` | unknown | `dom lib replay-save-open` | `dom.lib.replay-save-open.v1` | `python_subprocess` | - |
| `tools/lib/tool_run_lib_stress.py` | unknown | `dom lib run-lib-stress` | `dom.lib.run-lib-stress.v1` | `python_subprocess` | - |
| `tools/lib/tool_run_store_gc.py` | Run deterministic STORE-GC-0 baseline generation | `dom lib run-store-gc` | `dom.lib.run-store-gc.v1` | `python_subprocess` | - |
| `tools/lib/tool_store_verify.py` | Run deterministic store verification and write STORE-GC-0 verify outputs | `dom lib store-verify` | `dom.lib.store-verify.v1` | `python_subprocess` | - |
| `tools/lib/tool_verify_bundle.py` | unknown | `dom lib verify-bundle` | `dom.lib.verify-bundle.v1` | `python_subprocess` | - |

## `compat`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `tools/compat/tool_apply_migration.py` | Apply deterministic migration lifecycle actions for a single artifact | `dom compat apply-migration` | `dom.compat.apply-migration.v1` | `python_subprocess` | - |
| `tools/compat/tool_emit_descriptor.py` | unknown | `dom compat emit-descriptor` | `dom.compat.emit-descriptor.v1` | `python_subprocess` | - |
| `tools/compat/tool_generate_descriptor_manifest.py` | unknown | `dom compat generate-descriptor-manifest` | `dom.compat.generate-descriptor-manifest.v1` | `python_subprocess` | - |
| `tools/compat/tool_generate_interop_matrix.py` | unknown | `dom compat generate-interop-matrix` | `dom.compat.generate-interop-matrix.v1` | `python_subprocess` | - |
| `tools/compat/tool_plan_migration.py` | Plan deterministic migration lifecycle actions for a single artifact | `dom compat plan-migration` | `dom.compat.plan-migration.v1` | `python_subprocess` | - |
| `tools/compat/tool_replay_migration.py` | unknown | `dom compat replay-migration` | `dom.compat.replay-migration.v1` | `python_subprocess` | - |
| `tools/compat/tool_replay_negotiation.py` | unknown | `dom compat replay-negotiation` | `dom.compat.replay-negotiation.v1` | `python_subprocess` | - |
| `tools/compat/tool_run_interop_stress.py` | unknown | `dom compat run-interop-stress` | `dom.compat.run-interop-stress.v1` | `python_subprocess` | - |
| `tools/compat/tool_run_migration_lifecycle.py` | Generate deterministic MIGRATION-LIFECYCLE-0 report artifacts | `dom compat run-migration-lifecycle` | `dom.compat.run-migration-lifecycle.v1` | `python_subprocess` | - |
| `appshell:tool.attach_console_stub:compat-status` | Run deterministic endpoint compatibility status and show negotiated mode plus disabled features. | `dom compat status` | `dom.compat.status.v1` | `appshell_alias` | - |

## `diag`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `appshell:tool.attach_console_stub:diag capture` | Write a deterministic DIAG-0 repro bundle with logs, proof anchors, canonical events, and pinned runtime inputs. | `dom diag capture` | `dom.diag.capture.v1` | `appshell_alias` | - |
| `tools/diag/tool_replay_bundle.py` | tool.utility | `dom diag replay-bundle` | `dom.diag.replay-bundle.v1` | `python_subprocess` | - |
| `appshell:tool.attach_console_stub:diag snapshot` | Write a deterministic offline diagnostic snapshot bundle with descriptor, logs, and proof anchors. | `dom diag snapshot` | `dom.diag.snapshot.v1` | `appshell_alias` | - |

## `server`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `appshell:server:compat-status` | Run deterministic endpoint compatibility status and show negotiated mode plus disabled features. | `dom server compat-status` | `dom.server.compat-status.v1` | `appshell_alias` | - |
| `appshell:server:console` | Alias of `console enter` for deterministic REPL console access. | `dom server console` | `dom.server.console.v1` | `appshell_alias` | - |
| `appshell:server:descriptor` | Emit the CAP-NEG endpoint descriptor for the active product. | `dom server descriptor` | `dom.server.descriptor.v1` | `appshell_alias` | - |
| `tools/server/tool_replay_local_singleplayer.py` | tool.utility | `dom server replay-local-singleplayer` | `dom.server.replay-local-singleplayer.v1` | `python_subprocess` | - |
| `tools/server/tool_replay_server_window.py` | tool.utility | `dom server replay-server-window` | `dom.server.replay-server-window.v1` | `python_subprocess` | - |

## `client`

| Current Path | Function | Stable Namespace | Stable ID | Adapter | Required Capabilities |
| --- | --- | --- | --- | --- | --- |
| `appshell:client:compat-status` | Run deterministic endpoint compatibility status and show negotiated mode plus disabled features. | `dom client compat-status` | `dom.client.compat-status.v1` | `appshell_alias` | - |
| `appshell:client:console` | Alias of `console enter` for deterministic REPL console access. | `dom client console` | `dom.client.console.v1` | `appshell_alias` | - |
| `appshell:client:descriptor` | Emit the CAP-NEG endpoint descriptor for the active product. | `dom client descriptor` | `dom.client.descriptor.v1` | `appshell_alias` | - |
