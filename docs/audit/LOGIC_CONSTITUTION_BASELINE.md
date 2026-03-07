Status: DERIVED
Last Reviewed: 2026-03-08
Version: 1.0.0
Scope: LOGIC-0 cybernetic logic constitution baseline.

# Logic Constitution Baseline

## Constitutional Summary
- Added the binding LOGIC constitution in `docs/logic/LOGIC_CONSTITUTION.md`.
- Frozen LOGIC as substrate-agnostic cybernetics over typed signals, discrete state machines, schedules, and delays.
- Frozen deterministic `SENSE -> COMPUTE -> COMMIT -> PROPAGATE` evaluation order for future L1 logic networks.
- Frozen process-mediated actuation, SIG-governed message carriers, TEMP-governed timing, and META-COMPUTE budget consumption.
- Frozen profile-only rule-breaking and explain-event requirements for loops, oscillation, timing, compute throttle, and command refusal.

## Retro-Audit Summary
- Retro consistency audit recorded in `docs/audit/LOGIC0_RETRO_AUDIT.md`.
- Existing logic-adjacent behavior remains correctly distributed:
  - MOB signal/interlocking state machines
  - ELEC protection and relay semantics
  - SIG trust and receipt routing
  - PROC software/pipeline step graphs
- LOGIC-0 did not introduce a bespoke runtime. It defined constitutional semantics over those existing substrates and their future integration points.

## Constitutional Skeletons

### Schemas
- `schema/logic/signal_type.schema`
- `schema/logic/carrier_type.schema`
- `schema/logic/transducer.schema`
- `schema/logic/logic_policy.schema`

### Registries
- `data/registries/signal_type_registry.json`
  - baseline signal ids:
    - `signal.boolean`
    - `signal.scalar`
    - `signal.pulse`
    - `signal.message`
    - `signal.bus`
- `data/registries/carrier_type_registry.json`
  - baseline carrier ids:
    - `carrier.electrical`
    - `carrier.pneumatic`
    - `carrier.hydraulic`
    - `carrier.mechanical`
    - `carrier.optical`
    - `carrier.sig`
- `data/registries/logic_policy_registry.json`
  - `logic.default`
  - `logic.rank_strict`
  - `logic.lab_experimental`

## Tier, Coupling, and Explain Mappings

### Tier Contract
- `tier.logic.default`
  - supported tiers: `macro`, `meso`, `micro`
  - canonical aliases: `L0 -> macro`, `L1 -> meso`, `L2 -> micro`
  - deterministic degradation order: `micro -> meso -> macro`
  - `micro` reserved for ROI logic timing detail; macro assumes compiled/capsule-compatible controllers

### Coupling Contracts
- `coupling.logic.command_to_proc.actuator`
  - LOGIC emits actuator intent only through canonical process routing
  - direct foreign-domain truth mutation remains forbidden
- `coupling.sys.transducer_to_logic.signal`
  - carrier observations enter LOGIC only through transducer systems with declared signatures and error bounds
- `coupling.sig.receipt_to_logic.message`
  - receipt-based message carriers enter LOGIC only through SIG trust, addressing, and encryption policy gates

### Explain Contracts
- `explain.logic_loop_detected` -> `logic.loop_detected`
- `explain.logic_oscillation` -> `logic.oscillation`
- `explain.logic_timing_violation` -> `logic.timing_violation`
- `explain.logic_compute_throttle` -> `logic.compute_throttle`
- `explain.logic_command_refused` -> `logic.command_refused`

## Enforcement and Observation Surfaces
- RepoX invariants added:
  - `INV-LOGIC-SUBSTRATE-AGNOSTIC`
  - `INV-LOGIC-USES-COMPUTE-BUDGET`
  - `INV-LOGIC-DEBUG-REQUIRES-INSTRUMENTATION`
  - `INV-LOGIC-RULE-BREAK-PROFILED`
- AuditX promoted smells added:
  - `E307_ELECTRICAL_BIAS_IN_LOGIC_SMELL`
  - `E308_UNMETERED_LOGIC_COMPUTE_SMELL`
  - `E309_OMNISCIENT_LOGIC_DEBUG_SMELL`
- TestX coverage added:
  - `test_logic_registries_valid`
  - `test_logic_policy_declared`
  - `test_logic_contracts_present`
  - `test_player_demand_entries_reference_logic`
  - `test_no_electrical_bias_in_logic_layer`
- Instrument-gated observation remains the only constitutional path:
  - `instrument.logic_probe`
  - `instrument.logic_analyzer`
- Reference interpretation path remains reserved, not implemented:
  - `ref.logic_eval_engine` (`status: stub`, `next_series: LOGIC-4`)

## Player Demand Linkage
- Updated LOGIC-dependent demands in the player demand matrix for:
  - PLC control panel
  - automated factory
  - train interlocking cabinet
  - reactor control room
  - smart power grid
  - hacking SCADA
  - drone autopilot
  - traffic lights coordination
  - firmware flashing pipeline integration
- Those demands now point to planned LOGIC series work (`LOGIC-2` or `LOGIC-3`) instead of treating LOGIC-0 as feature implementation.

## Topology Integration
- `docs/audit/TOPOLOGY_MAP.json` and `docs/audit/TOPOLOGY_MAP.md` were regenerated after LOGIC schema, registry, contract, and enforcement additions.
- Refreshed topology artifact:
  - node_count: `3914`
  - edge_count: `8064`
  - deterministic_fingerprint: `3fb8afb84dc6ce1b1ffd69ea48db923883143b5eb35e95257211cfd3835a9e92`
- The topology generator was tightened so blanket schema/contract enforcement edges are emitted only from canonical `compatx`/`repox`/`auditx`/`testx` entrypoints, preventing artifact-budget overflow without weakening topology coverage.

## Readiness Checklist

### LOGIC-1 Readiness (signals and buses)
- Ready: canonical signal type registry and schema exist.
- Ready: carrier types are decoupled from semantics.
- Ready: logic policies define loop handling, timing mode, and compute-profile binding.
- Ready: substrate-bias enforcement exists before runtime code lands.
- Ready: instrumentation and reference-evaluator placeholders are already reserved.

### LOGIC-2 Readiness (elements and assemblies)
- Ready: deterministic evaluation order is frozen.
- Ready: process-mediated actuation path is declared.
- Ready: explain events for loops, timing, throttle, and refusals are declared.
- Ready: tier contract already defines L0/L1 operation with L2 ROI-only detail.
- Ready: player-demand linkage identifies the first element-heavy feature clusters.
- Not implemented yet: gates, relays, timers, PLC elements, compiled element runtime, or network execution engine.

## Gate Results
- RepoX STRICT (`python tools/xstack/repox/check.py --repo-root . --profile STRICT`):
  - PASS
  - `repox scan passed (files=1758, findings=17)`
- AuditX STRICT (`python tools/xstack/auditx/check.py --repo-root . --profile STRICT`):
  - PASS
  - `auditx scan complete (changed_only=false, findings=1346, promoted_blockers=0)`
- TestX STRICT subset (`python -m tools.xstack.testx.runner --repo-root . --profile STRICT --cache off --subset test_logic_registries_valid,test_logic_policy_declared,test_logic_contracts_present,test_player_demand_entries_reference_logic,test_no_electrical_bias_in_logic_layer,test_topology_map_deterministic,test_topology_map_includes_all_schemas,test_topology_map_includes_all_registries`):
  - PASS
  - `selected_tests=8`
- strict build (`python tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.logic0 --cache on --format json`):
  - PASS
  - `canonical_content_hash: 9cdabc6762b207303ef749adddf995b3fe64fe1d0605241cf417330f1966e2b5`
  - `manifest_hash: f262996a267f389df5294c19e50c43aa8dbbb82e4d799627a24c685e14137ac4`
- topology map refresh (`python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`):
  - PASS
  - JSON size: `2209416` bytes against budget `103809024`

## Contract and Invariant Notes
- Canon/glossary alignment: preserved.
- No runtime mode flags introduced.
- No wall-clock dependency introduced.
- No authority/truth/render boundary was weakened.
- No authoritative mutation path was added outside deterministic Processes.
