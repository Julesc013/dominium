Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Change: LOGIC-9 deterministic distributed protocol framing, arbitration, SIG transport, and debug surfaces for logic networks
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

Touched Paths:
- data/registries/explain_contract_registry.json
- docs/audit/LOGIC_PROTOCOL_BASELINE.md
- docs/logic/PROTOCOL_SHARD_RULES.md
- control/proof/control_proof_bundle.py
- logic/__init__.py
- logic/debug/debug_engine.py
- logic/eval/__init__.py
- logic/eval/logic_eval_engine.py
- logic/eval/propagate_engine.py
- logic/eval/runtime_state.py
- logic/protocol/__init__.py
- logic/protocol/protocol_engine.py
- logic/protocol/rows.py
- logic/signal/signal_store.py
- tools/auditx/analyzers/e326_nondeterministic_arbitration_smell.py
- tools/auditx/analyzers/e327_protocol_security_bypass_smell.py
- tools/auditx/analyzers/e328_protocol_bypass_smell.py
- tools/logic/tool_replay_logic_window.py
- tools/logic/tool_replay_protocol_window.py
- tools/logic/tool_run_logic_protocol_stress.py
- tools/xstack/repox/check.py
- tools/xstack/sessionx/process_runtime.py
- tools/xstack/testx/tests/_logic_eval_test_utils.py
- tools/xstack/testx/tests/test_fixed_priority_arbitration_deterministic.py
- tools/xstack/testx/tests/test_frame_encoding_deterministic.py
- tools/xstack/testx/tests/test_replay_protocol_hash_match.py
- tools/xstack/testx/tests/test_security_blocks_unverified_frames.py
- tools/xstack/testx/tests/test_sig_backed_delivery_respects_delay_loss.py
- tools/xstack/testx/tests/test_token_arbitration_state_progress.py

Demand IDs:
- fact.plc_control_panel
- fact.automated_factory
- city.smart_power_grid
- city.traffic_lights_coordination
- trans.train_interlocking_cabinet
- space.reactor_control_room
- cyber.hacking_scada
- cyber.firmware_flashing_pipeline_integration
- mil.drone_autopilot

Notes:
- LOGIC-9 turns the existing protocol definition skeleton into deterministic framed delivery with stable arbitration, explicit addressing, and bounded replayable event records.
- The SIG-backed transport seam preserves receipt-governed epistemics for SCADA, reactor-room, interlocking, and city-scale controller fantasies rather than allowing direct omniscient frame delivery.
- Proof bundle extensions now cover protocol frame, arbitration, protocol-event, and sniffer-summary chains so compiled and distributed controller windows can be audited and replayed without silent fallback.
