Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# LOGIC8 Retro Audit

Date: 2026-03-08
Scope: LOGIC-8 faults, noise, EMI stubs, and protocol-security hooks

## Existing Fault / Failure Patterns Reviewed

- ELEC already models deterministic fault state rows in:
  - `src/electric/fault/fault_engine.py`
  - `schema/electric/fault_state.schema`
  - `data/registries/fault_kind_registry.json`
- ELEC protection and SAFETY integration already route fault consequences through:
  - `src/electric/protection/protection_engine.py`
  - `src/safety/safety_engine.py`
- FLUID stress tooling already models deterministic injected faults such as:
  - stuck valve
  - burst
  - leak
  - cavitation
- Process/system degradation and drift already use explicit registry/policy surfaces in:
  - `src/process/drift/drift_engine.py`
  - `data/registries/drift_policy_registry.json`
  - `data/registries/degradation_profile_registry.json`

## Existing Noise / RNG Patterns Reviewed

- LOGIC-1 already defines signal noise policies:
  - `noise.none`
  - deterministic quantization
  - named RNG optional
- SIG transport already uses deterministic named-RNG patterns for loss/attenuation, with explicit `rng_stream_name`.
- Model evaluation already gates stochastic branches on:
  - explicit `stochastic_allowed`
  - explicit `rng_stream_name`
  - deterministic seed hashing from canonical inputs

## Existing Security / Verification Patterns Reviewed

- SIG trust/verification already exposes deterministic result rows and trust updates in:
  - `src/signals/trust/trust_engine.py`
- Credential / certificate artifacts already exist in SIG institutions and session runtime plumbing.
- Protocol/message layers already track verification state and security headers in `src/signals/transport/transport_engine.py`.

## Existing Ad Hoc Random-Failure Risk Review

- No existing LOGIC-specific random-failure subsystem was found.
- Existing repo-wide stochastic surfaces already follow the named-RNG pattern and can be reused.
- Retire/avoid for LOGIC:
  - ad hoc inline random failure branches
  - direct signal mutation to simulate faults
  - carrier-specific “voltage noise” semantics inside logic behavior

## Integration Seams Confirmed

- SENSE phase is the correct place to apply:
  - open/short/stuck-at overrides
  - threshold drift input shaping
  - sampling noise
- LOGIC evaluation already has explicit runtime/proof surfaces for:
  - throttle events
  - timing violations
  - state updates
  - output signal chains
- Compiled/collapsed logic already has forced-expand and debug seams; LOGIC-8 fault and security anomalies can reuse explain/expand routing.

## Cross-Domain Coupling Fit

- EMI and radiation effects should enter LOGIC through:
  - field sample / constitutive model style inputs
  - carrier/noise/fault modifiers
  - not direct logic-semantic branches
- SAFETY patterns can already consume fault-visible context and emit fail-safe outcomes.
- SIG verification/trust surfaces are suitable for protocol-link spoof rejection stubs.

## Naming / Glossary Check

- Proposed LOGIC-8 names are consistent with canon vocabulary:
  - `logic_fault_state`
  - `noise_policy`
  - `security_policy`
  - `process.logic_fault_set`
  - `process.logic_fault_clear`
- Constraint to preserve:
  - carrier and field effects must remain modifiers/constraints, not logic semantics.

## Conclusion

- The repo already contains reusable deterministic patterns for fault rows, named-RNG gating, trust verification, and safety escalation.
- LOGIC-8 should extend LOGIC SENSE/eval/runtime proof surfaces rather than creating a standalone failure subsystem.
