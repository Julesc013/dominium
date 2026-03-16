Status: DERIVED
Last Reviewed: 2026-03-08
Supersedes: none
Superseded By: none
Version: 1.0.0
Scope: LOGIC-1 retro-consistency audit for typed signal and bus abstraction.
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# LOGIC-1 Retro Audit

## Summary
- Existing signal-like behavior is still distributed across domain runtimes, not hidden inside a pre-existing generic logic engine.
- LOGIC-1 can land as a substrate-agnostic signal layer without redesigning SIG, MOB, or ELEC semantics.
- The required adapter seams are small and explicit:
  - SIG receipt artifact -> `signal.message`
  - MOB interlocking state -> future LOGIC transducer-facing signal ports
  - ELEC switch/breaker state -> future carrier/transducer bridge

## Existing Signal-Like Systems

### SIG envelopes and receipts
- `src/signals/transport/transport_engine.py` already models message artifacts, envelopes, delivery, trust, and receipts.
- This remains the canonical transport substrate for `carrier.sig`.
- No conflict: LOGIC-1 only maps receipt-governed artifacts into `signal.message`; it does not replace SIG routing, trust, or encryption.

### MOB signaling and interlocking
- `src/mobility/signals/signal_engine.py` holds mobility-specific signal state and interlocking helpers.
- This is domain logic for rail/road/waypoint signaling, not a general substrate-agnostic logic layer.
- No conflict: LOGIC-1 introduces generic typed signals and buses but does not absorb mobility meanings, route tables, or safety law.

### ELEC switch and protection patterns
- ELEC retains breaker/relay/protection semantics and domain-owned transport costs in its own runtime and registries.
- LOGIC-1 must not encode ELEC-only quantities into signal meaning.
- No conflict: carrier identity can be declared as `carrier.electrical` while semantics remain in `signal_type_id`, `value_ref`, and future transducer bindings.

## Adapter Needs
- `carrier.sig`
  - map SIG receipt artifact rows into deterministic `signal.message` value rows
  - preserve receipt/trust metadata as references, not duplicated truth
- physical carriers
  - bridge through declared `transducer_id` and model bindings only
  - no direct substrate solve inside `src/logic`
- bus/protocol seams
  - provide framing, arbitration, addressing, and error-detection placeholders as data contracts
  - do not introduce a protocol runtime yet

## Integration Points
- Actuator/process seam
  - `process.signal_set`
  - `process.signal_emit_pulse`
- Instrumentation seam
  - `data/registries/instrumentation_surface_registry.json`
  - `instrument.logic_probe`
  - `instrument.logic_analyzer`
- Compute budgeting seam
  - `src/meta/compute/compute_budget_engine.py::request_compute`
- Coupling relevance seam
  - `data/registries/coupling_relevance_policy_registry.json`
  - tolerance-aware change detection feeds later COUPLE scheduling

## Naming Review
- Reserved LOGIC terms already frozen in `docs/logic/LOGIC_CONSTITUTION.md` remain usable:
  - signal
  - carrier
  - transducer
  - policy
- No glossary conflict found for:
  - bus encoding
  - protocol definition
  - signal delay policy
  - signal noise policy
- Avoid introducing substrate-semantic aliases such as "wire truth", "circuit state", or "relay network" as the generic layer names.

## Conclusion
- LOGIC-1 is additive and compatible with current canon.
- No hidden generic logic subsystem was found.
- The implementation path is safe if:
  - signal writes stay process-only
  - reads stay instrumentation-gated
  - carriers remain cost/constraint metadata, not semantics
  - SIG receipts stay authoritative for message transport
