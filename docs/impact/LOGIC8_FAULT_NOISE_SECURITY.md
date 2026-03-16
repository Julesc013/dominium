Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Change: LOGIC-8 deterministic fault, noise, EMI-stub, and protocol-security hooks for logic networks
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

Touched Paths:
- data/registries/explain_contract_registry.json
- data/registries/instrumentation_surface_registry.json
- data/registries/process_registry.json
- docs/logic/FAULT_NOISE_SECURITY_MODEL.md
- src/control/proof/control_proof_bundle.py
- src/logic/debug/debug_engine.py
- src/logic/eval/logic_eval_engine.py
- src/logic/eval/runtime_state.py
- src/logic/eval/sense_engine.py
- src/logic/fault/fault_engine.py
- src/logic/noise/noise_engine.py
- tools/logic/tool_replay_fault_window.py
- tools/logic/tool_replay_logic_window.py
- tools/logic/tool_run_logic_fault_stress.py
- tools/xstack/sessionx/process_runtime.py

Demand IDs:
- fact.plc_control_panel
- fact.automated_factory
- trans.train_interlocking_cabinet
- space.reactor_control_room
- city.smart_power_grid
- city.traffic_lights_coordination
- cyber.hacking_scada
- cyber.firmware_flashing_pipeline_integration
- mil.drone_autopilot

Notes:
- LOGIC-8 adds deterministic fault overlays, declared noise policies, EMI field stubs, and protocol-security gating without changing LOGIC semantics or bypassing process-only mutation.
- Proof surfaces now cover logic fault state, behavior-affecting noise decisions, and security failures so SCADA, grid, interlocking, and autopilot scenarios can replay faulted controller windows exactly.
- Instrumentation remains epistemic: fault state is probeable only through registered measurement surfaces, while security failures and noise effects remain explainable and compactable.
