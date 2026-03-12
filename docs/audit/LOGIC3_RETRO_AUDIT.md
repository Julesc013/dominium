Status: DERIVED
Last Reviewed: unknown
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# LOGIC3 Retro Audit

Status: complete
Scope: LOGIC-3 topology baseline for NetworkGraph specialization
Source Prompt: LOGIC-3

## Reviewed Existing Wiring and Link Systems

### Core NetworkGraph substrate
- `src/core/graph/network_graph_engine.py`
- Canonical deterministic graph normalization already exists.
- This is the required substrate for LOGIC-3.
- Conclusion: LOGIC wiring must specialize `NetworkGraph`, not replace it.

### Mobility network topology
- `src/mobility/network/mobility_network_engine.py`
- Mobility already uses `NetworkGraph` as a specialization with domain payloads.
- Useful pattern for deterministic graph ids, bindings, and payload normalization.
- Conclusion: LOGIC-3 should mirror this layering pattern.

### Electrical network topology
- `src/electric/power_network_engine.py`
- Electrical graph usage is domain-specific and solver-oriented.
- No reusable generic "logic graph" exists here.
- Conclusion: LOGIC must not inherit electrical semantics.

### Fluid, thermal, logistics, and other network users
- `src/fluid/network/fluid_network_engine.py`
- `src/thermal/network/thermal_network_engine.py`
- `src/logistics/logistics_engine.py`
- All consume `NetworkGraph` rather than defining parallel graph substrates.
- Conclusion: repo-wide precedent supports a typed specialization, not ad hoc topology.

### Signal transport and SIG routing
- `src/signals/transport/transport_engine.py`
- `src/signals/addressing/address_engine.py`
- SIG already owns message routing, receipts, trust, and delivery semantics.
- Integration point for LOGIC-3 is `edge.sig_link` and carrier `carrier.sig`, not a duplicate protocol engine.

### Existing LOGIC state and mutation paths
- `src/logic/signal/signal_store.py`
- `src/logic/element/logic_element_validator.py`
- LOGIC already has typed signal records, carrier seams, and pack-defined elements.
- No existing logic network graph implementation exists under `src/logic/network/`.
- Conclusion: LOGIC-3 fills a missing topology layer; it does not replace an older runtime.

### Session runtime graph storage
- `tools/xstack/sessionx/process_runtime.py`
- Runtime already stores generic `state["network_graphs"]`.
- Mobility graph edits also persist through this generic collection.
- Conclusion: LOGIC-3 can integrate cleanly by persisting normalized logic graphs into the shared graph collection plus logic-specific state.

## Integration Points

### SYS templates and assemblies
- SYS templates can carry graph references through existing graph-bearing state and assembly composition.
- Logic networks can therefore be embedded without a dedicated logic-only graph substrate.

### PROC orchestration
- PROC process definitions can create, edit, and validate logic networks through canonical processes.
- This supports scripted construction and automation pipelines without direct state mutation.

### META-COMPUTE
- `src/meta/compute`
- Graph create/edit/validate operations can request deterministic compute units before mutating state.

### COUPLE
- Edge and graph change hashes can feed coupling relevance as a later LOGIC-4/6 seam.
- No direct coupling bypass was found that would force a bespoke path here.

### META-INSTR
- Existing domain and logic element surfaces already declare logic probe surfaces.
- LOGIC-3 needs network-level node/edge probing and inspector-only graph visibility as a new surface layer.

### SIG and shard boundaries
- Cross-shard synchronous wiring is not represented elsewhere and must remain forbidden.
- Existing SIG receipts and artifact exchange are the correct seam for cross-shard logic links.

## Ad Hoc Wiring and Duplication Findings

- No existing `src/logic/network/*` implementation exists.
- No separate "logic graph" substrate was found outside `NetworkGraph`.
- Existing wiring systems are domain-specific and do not preempt LOGIC-3.
- Main drift risk is future ad hoc wiring in `src/logic/` that bypasses `NetworkGraph`; this is addressed in LOGIC-3 enforcement.

## Reserved Word and Naming Review

Reviewed against `docs/canon/glossary_v1.md`.

- Safe canonical terms for this slice:
  - `LogicNetworkGraph`
  - `network binding`
  - `boundary artifact`
  - `signal`, `carrier`, `policy`, `refusal`, `deterministic`
- Avoid introducing ambiguous or non-canonical aliases:
  - `circuit` as the authoritative domain term
  - `wire simulator`
  - `clock subsystem`
  - `electrical logic` as a semantic layer label

## Conclusions

- LOGIC-3 should be a `NetworkGraph` specialization with logic payload schemas and policy registries.
- No canon conflict or existing logic graph duplication was found.
- Main mandatory integrations are:
  - generic `network_graphs` state persistence
  - process-only mutation through runtime dispatch
  - SIG-based shard boundaries
  - META-COMPUTE metering
  - META-INSTR probe surfaces
