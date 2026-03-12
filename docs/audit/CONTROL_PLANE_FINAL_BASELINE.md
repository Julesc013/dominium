Status: BASELINE
Version: 1.0.0
Date: 2026-03-01
Scope: CTRL-10 final hardening envelope before MOB series
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Control Plane Final Baseline

## Control Subsystems

- `src/control/control_plane_engine.py`
- `src/control/negotiation/negotiation_kernel.py`
- `src/control/ir/control_ir_compiler.py`
- `src/control/view/view_engine.py`
- `src/control/fidelity/fidelity_engine.py`
- `src/control/effects/effect_engine.py`
- `src/control/proof/control_proof_bundle.py`

## Determinism Guarantees

The control-plane envelope is hardened to remain deterministic across:

1. Thread-count variants (validated by `tools/control/tool_determinism_compare.py`).
2. Simulated platform variants (same tool; deterministic fingerprints remain aligned).
3. Multiplayer policy modes:
   - `policy.net.lockstep`
   - `policy.net.server_authoritative`
   - `policy.net.srz_hybrid`
4. High-load stress conditions (`tools/control/tool_global_control_stress.py`).

Deterministic surfaces locked:

- control resolution fingerprints
- decision-log fingerprints
- fidelity allocation fingerprints
- control proof-bundle fingerprints
- lockstep per-tick control decision hash contribution

## Proof Integration Summary

CTRL-10 integrates control proof bundles via:

- `schema/control/control_proof_bundle.schema`
- `schemas/control_proof_bundle.schema.json`
- runtime proof builder (`src/control/proof/control_proof_bundle.py`)

Network integration:

1. Authoritative/hybrid policies emit control proof bundle artifacts per tick and baseline.
2. Lockstep hash anchors include control-decision hash material.
3. Anchor extensions carry control proof references/hashes.

## Migration and Compatibility Guarantees

CompatX version registry now includes:

1. `control_proof_bundle` schema registration.
2. Migration stubs:
   - `control_ir` (`0.9.0 -> 1.0.0`)
   - `control_decision_log` (`0.1.0 -> 1.0.0`)

Forward-compat policy:

1. additive fields must have defaults.
2. removed/renamed fields require explicit migration route.
3. unsupported schema versions refuse explicitly (no silent coercion).

## Regression Locks

Baselines:

1. `data/regression/control_decision_baseline.json` (CTRL-9 sequence lock).
2. `data/regression/control_plane_full_baseline.json` (CTRL-10 full-envelope lock).

Update-tag requirements:

1. `CTRL-DECISION-REGRESSION-UPDATE`
2. `CTRL-PLANE-REGRESSION-UPDATE`

RepoX enforcement:

- `INV-CONTROL-DECISION-REGRESSION-LOCK-PRESENT`
- `INV-CONTROL-PLANE-FULL-REGRESSION-LOCK-PRESENT`

## Extension Contract

Future domain integration is governed by:

- `docs/control/CONTROL_EXTENSION_CONTRACT.md`

Key blocker invariant:

- `INV-DOMAIN-CONTROL-REGISTERED`

## MOB Readiness Statement

Control-plane hardening is complete for MOB entry:

1. no direct bypass path is permitted.
2. downgrade/refusal/proof surfaces are deterministic and auditable.
3. compatibility and migration envelope is explicit.
4. topology + semantic-impact governance includes control subsystem coupling.
