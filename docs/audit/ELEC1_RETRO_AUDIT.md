# ELEC1 Retro-Consistency Audit

Status: AUDIT
Date: 2026-03-03
Scope: ELEC-1 `PowerNetworkGraph + Core Flow Integration`

## Findings

1. No pre-existing electrical flow runtime exists:
- No `src/electric/` module is present.
- No `process.elec.*` handlers are present in `tools/xstack/sessionx/process_runtime.py`.

2. Electrical registries were already scaffolded in ELEC-0:
- `data/registries/elec_node_kind_registry.json`
- `data/registries/elec_edge_kind_registry.json`
- `data/registries/elec_model_registry.json`

3. Registry references pointed to missing schemas:
- `dominium.schema.electric.elec_node_payload@1.0.0`
- `dominium.schema.electric.elec_edge_payload@1.0.0`

4. Flow substrate is already bundle-capable:
- `src/core/flow/flow_engine.py` supports `quantity_bundle_id` and per-component capacity/loss policy.
- This enables electrical P/Q/S flow without introducing a bespoke electrical transport engine.

5. Safety flow-disconnect path was signal-channel-only:
- `process.safety_tick` action `flow_disconnect` currently mutates `signal_channel_rows` only.
- Electrical channels require the same path to operate on electrical flow channels.

6. Proof bundle lacked electrical flow hash surface:
- `control_proof_bundle` currently includes mobility/signal proof hashes but no power hash entry.

## Migration Plan

1. Add missing electrical payload schemas and wire CompatX registration.
2. Introduce `src/electric/power_network_engine.py` with deterministic node/edge payload normalization and E1 solve helpers.
3. Add process-mediated electrical handlers:
- `process.elec.connect_wire`
- `process.elec.flip_breaker`
- `process.elec.lockout_tagout`
- `process.elec.network_tick`
4. Reuse FlowSystem bundle channels (`bundle.power_phasor`) for transport state.
5. Route overload protection through SAFETY breaker patterns; do not add ad-hoc breaker paths.
6. Extend control proof bundle with `power_flow_hash`.
7. Add enforcement and tests for:
- bundle-only power flow path
- safety-only breaker path
- deterministic PF/loss/tier fallback behavior.
