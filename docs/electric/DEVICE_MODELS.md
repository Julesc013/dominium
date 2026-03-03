# Device Models

Status: CANONICAL
Last Updated: 2026-03-03
Scope: ELEC-3 advanced electrical device behavior via constitutive models.

## 1) Purpose

ELEC-3 moves advanced electrical device behavior to constitutive model evaluation. Device response logic must be data-driven and deterministic, not hardcoded in solver loops.

## 2) Model-Bound Device Behavior

Electrical device behavior is bound through `model_bindings` on electrical nodes/edges and evaluated via the META-MODEL engine.

Canonical ELEC-3 model families:

- `model_type.elec_pf_correction`
- `model_type.elec_transformer_stub`
- `model_type.elec_storage_battery`
- `model_type.elec_device_loss`

## 3) PF Correction

PF correction is represented as a constitutive model that maps:

- requested active/reactive power
- desired PF target (or direct compensation ratio)

to deterministic `Q` adjustment outputs.

The model reduces reactive demand magnitude without mutating canonical state directly; outputs are applied through process-mediated flow/effect paths.

## 4) Transformer Stub

Transformer behavior remains a meso-tier stub and is model-driven:

- uses ratio/spec parameters
- applies deterministic transfer and loss proxy
- emits downstream P/Q/S adjustments and heat-loss outputs

No waveform simulation is introduced.

## 5) Storage (Battery) Model

Storage nodes expose deterministic state via `storage_state` and model outputs:

- available discharge/charge power bounded by state-of-charge and limits
- internal resistance proxy contributes deterministic loss/heat
- degradation hooks emit hazard increments for maintenance/safety coupling

State mutation is process-only (`process.storage_charge` / `process.storage_discharge`).

## 6) Loss-to-Heat Convention

Electrical losses are represented as model outputs by convention:

- preferred quantity: `quantity.thermal.heat_loss_stub`
- optional direct effect hook: `effect.temperature_increase_local`

When THERM is unavailable, heat-loss values remain observable as deterministic derived/inspection artifacts and effect hooks.

## 7) Tiering

- E1 is the default advanced electrical tier for model-driven phasor behavior.
- E0 fallback remains available and deterministic under budget pressure.
- E2 waveform tier is explicitly out-of-scope for ELEC-3.

## 8) Determinism and Enforcement

Required invariants:

- device behavior must be model-driven (`INV-DEVICE-BEHAVIOR-MODEL-ONLY`)
- loss-to-heat mapping must be declared (`INV-LOSS-TO-HEAT-DECLARED`)
- process-only mutation remains mandatory for state/effect/hazard changes.
