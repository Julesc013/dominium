Status: DERIVED
Last Reviewed: 2026-03-08
Version: 1.0.0
Scope: LOGIC-1 signal, bus, carrier, and protocol-hook baseline.

# Signal And Bus Baseline

## Constitutional Summary
- Added the binding signal-layer doctrine in `docs/logic/SIGNAL_AND_BUS_MODEL.md`.
- Frozen typed signal values as substrate-agnostic records over `signal_type_id`, `carrier_type_id`, canonical tick validity, and deterministic payload hashing.
- Frozen bus definitions and protocol hooks as registry-driven schema objects, not runtime-specific protocol engines.
- Frozen process-only signal mutation through `process.signal_set` and `process.signal_emit_pulse`.
- Frozen instrumentation-gated signal observation and compactable trace artifacts.

## Retro-Audit Summary
- Retro consistency audit recorded in `docs/audit/LOGIC1_RETRO_AUDIT.md`.
- Existing signal-like concepts remain in their home systems:
  - SIG envelopes and receipts remain authoritative transport artifacts.
  - MOB signaling and interlocking remain domain behavior, not a generic logic runtime.
  - ELEC switch and breaker states remain physical-domain truth, not signal semantics.
- LOGIC-1 introduced the shared signal abstraction layer and adapter seams without collapsing those systems into a bespoke logic subsystem.

## Signal Value Model

### Signal Core
- Canonical signal record fields:
  - `signal_id`
  - `signal_type_id`
  - `carrier_type_id`
  - `value_ref`
  - `valid_from_tick`
  - `valid_until_tick`
  - `deterministic_fingerprint`
  - `extensions`
- Canonical time reference remains simulation tick. Delay behavior is delegated to declared delay policies, not a global clock subsystem.

### Value Formats
- `signal.boolean`
  - payload schema: `dominium.schema.logic.signal_value_boolean@1.0.0`
  - value domain: `0 | 1`
- `signal.scalar`
  - payload schema: `dominium.schema.logic.signal_value_scalar@1.0.0`
  - value domain: fixed-point scalar with optional `units_id`
- `signal.pulse`
  - payload schema: `dominium.schema.logic.signal_value_pulse@1.0.0`
  - value domain: bounded edge list `{tick_offset, edge_kind}`
- `signal.message`
  - payload schema: `dominium.schema.logic.signal_value_message@1.0.0`
  - value domain: SIG `artifact_id` plus optional `receipt_id`
- `signal.bus`
  - payload schema: `dominium.schema.logic.bus_definition@1.0.0`
  - value domain: bus definition reference with encoding-driven sub-signal layout

## Bus And Protocol Hooks

### Bus Encodings
- `encoding.bits`
- `encoding.uint`
- `encoding.struct`
- `encoding.frame`

### Protocol Hooks
- `protocol.none`
- `protocol.simple_frame_stub`
- `protocol.bus_arbitration_stub`
- Protocol definitions are minimal hook records over:
  - `framing_rules_ref`
  - `arbitration_policy_id`
  - `error_detection_policy_id`
- No protocol executor, network propagation engine, or element semantics were added in LOGIC-1.

## Delay, Noise, And Carrier Hooks

### Delay Policies
- `delay.none`
- `delay.fixed_ticks`
- `delay.temporal_domain`
- `delay.sig_delivery`

### Noise Policies
- `noise.none`
- `noise.deterministic_quantization`
- `noise.named_rng_optional`
- Named-RNG noise remains policy-gated and optional. LOGIC-1 does not introduce any nondeterministic path.

### Carrier Seams
- Carrier types remain constraint and cost selectors, not semantic dispatch:
  - `carrier.electrical`
  - `carrier.pneumatic`
  - `carrier.hydraulic`
  - `carrier.mechanical`
  - `carrier.optical`
  - `carrier.sig`
- Adapter seam implementations:
  - `carrier.sig` maps SIG receipt artifacts into `signal.message` payloads.
  - physical carriers read and write only through declared transducer bindings and model-backed system interfaces.
- No direct electrical, pneumatic, hydraulic, or mechanical physics was introduced inside `src/logic`.

## Deterministic Store And Process APIs
- Canonical store implementation: `src/logic/signal/signal_store.py`
- Canonical process entrypoints:
  - `process.signal_set`
  - `process.signal_emit_pulse`
- Deterministic ordering key:
  - `(network_id, element_id, port_id, tick, sequence)`
- Canonical serialization and proof inputs:
  - `canonical_signal_snapshot`
  - `canonical_signal_serialization`
  - `canonical_signal_hash`
- Coupling change records are emitted as derived rows using tolerance-aware payload hashes; propagation remains out of scope until LOGIC-3.

## Epistemics And Instrumentation
- Signal reads require measurement surfaces and access validation.
- Placeholder instrumentation surface added for `domain.logic` with:
  - `measure.logic.signal`
  - `measure.logic.bus`
  - `control.logic.probe.attach`
  - `control.logic.probe.detach`
  - `forensics.logic.trace`
- Trace artifacts are derived, compactable provenance records; raw truth is not exposed directly to render or unauthorized tools.

## Compute And Coupling Hooks
- Bulk signal mutation requests compute units through META-COMPUTE before state is updated.
- Signal change rows are prepared for COUPLE relevance scheduling using deterministic change tokens.
- LOGIC-1 does not schedule propagation or element execution, but it establishes the meter-and-token interface required for later logic network work.

## Enforcement And Validation Coverage
- RepoX invariants added:
  - `INV-SIGNAL-TYPES-REGISTERED`
  - `INV-SIGNAL-UPDATES-PROCESS-ONLY`
  - `INV-NO-CARRIER-SEMANTIC-BIAS`
- AuditX promoted smells added:
  - `E310_DIRECT_SIGNAL_MUTATION_SMELL`
  - `E311_CARRIER_BIAS_SMELL`
- Existing LOGIC-0 electrical-bias enforcement was tightened to avoid variable-name false positives while preserving unit/reference detection.
- TestX coverage added:
  - `test_signal_serialization_deterministic`
  - `test_bus_definition_schema_valid`
  - `test_signal_set_process_only`
  - `test_sig_receipt_to_message_signal_mapping`
  - `test_no_truth_leak_without_instrument`

## Topology Integration
- `docs/audit/TOPOLOGY_MAP.json` and `docs/audit/TOPOLOGY_MAP.md` were regenerated after LOGIC-1 schema, registry, process, instrumentation, and enforcement additions.
- Refreshed topology artifact:
  - node_count: `3942`
  - edge_count: `8167`
  - deterministic_fingerprint: `9e8394a39a5063c4afd870933a9841721d6626f7f0cdf9841985ef168271bd95`

## Readiness Checklist

### LOGIC-2 Readiness (logic elements and assemblies)
- Ready: stable signal value model exists for boolean, scalar, pulse, message, and bus inputs.
- Ready: deterministic signal mutation path exists through canonical processes.
- Ready: carrier and transducer seams are separated from semantics.
- Ready: instrumentation-gated observation path exists for signal-level debugging.
- Not implemented yet: gates, relays, timers, PLC instructions, or state-machine elements.

### LOGIC-3 Readiness (logic network graph and propagation)
- Ready: signal IDs, serialization, and change tokens are deterministic.
- Ready: delay and noise policies are declared and registry-driven.
- Ready: protocol hooks exist for framing, arbitration, and error detection metadata.
- Ready: compute and coupling hooks are in place for signal mutation events.
- Not implemented yet: propagation scheduler, network graph executor, protocol runtimes, or compiled network collapse.

## Gate Results
- RepoX STRICT (`python tools/xstack/repox/check.py --repo-root . --profile STRICT`):
  - PASS on the final clean-tree seal rerun for this baseline
- AuditX STRICT (`python tools/xstack/auditx/check.py --repo-root . --profile STRICT`):
  - PASS
  - `auditx scan complete (changed_only=false, findings=2209, promoted_blockers=0)`
- TestX STRICT subset (`python -m tools.xstack.testx.runner --repo-root . --profile STRICT --cache off --subset test_signal_serialization_deterministic,test_bus_definition_schema_valid,test_signal_set_process_only,test_sig_receipt_to_message_signal_mapping,test_no_truth_leak_without_instrument,test_topology_map_deterministic,test_topology_map_includes_all_schemas,test_topology_map_includes_all_registries`):
  - PASS
  - `selected_tests=8`
- strict build (`python tools/setup/build.py --repo-root . --bundle bundle.base.lab --out build/dist.strict.logic1 --cache on --format json`):
  - PASS
  - `canonical_content_hash: 9cdabc6762b207303ef749adddf995b3fe64fe1d0605241cf417330f1966e2b5`
  - `manifest_hash: f262996a267f389df5294c19e50c43aa8dbbb82e4d799627a24c685e14137ac4`
- topology map refresh (`python tools/governance/tool_topology_generate.py --repo-root . --out-json docs/audit/TOPOLOGY_MAP.json --out-md docs/audit/TOPOLOGY_MAP.md`):
  - PASS
  - `deterministic_fingerprint: 9e8394a39a5063c4afd870933a9841721d6626f7f0cdf9841985ef168271bd95`
  - JSON size: `2232029` bytes

## Contract And Invariant Notes
- Canon/glossary alignment: preserved.
- Contract/schema impact: changed.
- No runtime mode flags introduced.
- No wall-clock dependency introduced.
- No carrier semantics were allowed to alter logic meaning.
- No authoritative signal mutation path was added outside deterministic Process execution.
- No observation pathway was added that bypasses META-INSTR authority checks.
