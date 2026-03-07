Change: GR3 no-stops hardening unblock for deterministic control, system expand, protection, and planning contracts

Touched Paths:
- schemas/control_proof_bundle.schema.json
- src/control/control_plane_engine.py
- src/electric/protection/protection_engine.py
- src/system/system_expand_engine.py
- tools/xstack/sessionx/process_runtime.py
- tools/xstack/testx/tests/lod_invariance_testlib.py
- tools/xstack/testx/tests/plan_testlib.py

Demand IDs:
- fact.balanced_bus_factory
- engr.metrology_lab_flow
- city.blackout_restoration_plan
- trans.rail_interlocking_mastery

Notes:
- Restores deterministic decision-log addressing so repeated control resolutions remain hash-stable.
- Closes system expand provenance tamper acceptance without changing successful expand semantics.
- Aligns control proof bundle schema coverage with the emitted META/PROC/COMPILE/POLL fields already carried by runtime proofs.
- Fixes electrical overload trip planning to evaluate against the observed fault measure instead of a mixed severity scale.
- Brings LOD and planning fixtures up to the stricter capability/conservation contracts enforced by GR3.
