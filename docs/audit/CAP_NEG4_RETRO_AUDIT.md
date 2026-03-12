Status: DERIVED
Last Reviewed: 2026-03-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# CAP-NEG-4 Retro Audit

## Scope
- Audit current endpoint descriptor, negotiation-record, and degrade-ladder surfaces before adding the mixed-version stress envelope.
- Confirm that synthetic descriptors can be generated deterministically without requiring historical binaries.
- Identify the minimum enforcement additions needed for regression locks and interop-matrix coverage.

## Findings
- Deterministic synthetic endpoint descriptors are already possible.
  - `src/compat/capability_negotiation.py` exposes `build_default_endpoint_descriptor(...)` and `build_endpoint_descriptor(...)`.
  - Current descriptor construction is data-driven from product defaults, protocol ranges, contract ranges, and degrade ladders.
- Negotiation output is already deterministic and replay-verifiable.
  - `src/compat/capability_negotiation.py` produces sorted `NegotiationRecord` rows and a canonical hash.
  - `tools/compat/tool_replay_negotiation.py` already regenerates a recorded negotiation for a descriptor pair and verifies the hash.
- Degrade behavior is already explicit enough to stress.
  - `data/registries/degrade_ladder_registry.json` and `data/registries/capability_fallback_registry.json` cover rendered-ui fallback, compiled-logic fallback, protocol-layer disablement, and read-only contract fallback.
  - `src/compat/negotiation/degrade_enforcer.py` can already enforce negotiated disabled/substituted capabilities at runtime.
- Real product descriptors are available offline.
  - `dist/bin/*` wrappers exist for `client`, `server`, `engine`, `game`, `launcher`, `setup`, and `tool_attach_console_stub`.
  - `tools/compat/tool_generate_descriptor_manifest.py` can already emit a stable offline manifest from those wrappers.
- Missing CAP-NEG-4 surfaces are tooling and regression locks, not core negotiation semantics.
  - There is no current synthetic interop-matrix generator.
  - There is no stress harness that summarizes full/degraded/read-only/refused statistics across a deterministic scenario matrix.
  - There is no committed CAP-NEG regression lock analogous to the EARTH-9 or MW-4 baselines.

## Integration Direction
- Reuse the existing negotiation engine directly instead of creating a parallel simulator.
- Add a shared CAP-NEG-4 helper module so the generator tool, stress tool, regression lock builder, and TestX all consume the same deterministic scenario set.
- Cover both synthetic descriptors and real emitted descriptors.
  - Synthetic rows prove mix-and-match behavior without requiring old binaries.
  - Real descriptor smoke rows prove that current products negotiate as expected.
- Keep CAP-NEG-4 behavior non-invasive.
  - No runtime handshake semantics need to change.
  - CAP-NEG-4 should add only tools, regression data, explain/report artifacts, and enforcement around coverage.
