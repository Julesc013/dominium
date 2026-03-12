Status: BASELINE
Last Reviewed: 2026-03-05
Supersedes: none
Superseded By: none
Version: 1.0.0
Compatibility: SYS-1 retro audit for interface signature and invariant enforcement.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# SYS1 Retro Audit

## Scope
Audit existing interface/rating/invariant usage prior to SYS-1 strict validation enforcement.

## 1) Port/Spec/Rating Usage Across Domains
Observed boundary-style declarations exist but are fragmented and mostly domain-local:

- Machine/port surfaces:
  - `data/registries/machine_type_registry.json`
  - `src/machines/port_engine.py`
- Mobility/vehicle interfaces:
  - `data/registries/vehicle_class_registry.json`
  - `data/registries/mobility_vehicle_class_registry.json`
- Signal channel typing:
  - `data/registries/signal_channel_type_registry.json`
- Spec declarations and checks:
  - `data/registries/spec_type_registry.json`
  - `src/specs/spec_engine.py`

Gap: no unified SYS-level interface descriptor contract requiring typed ports, bundle allowlists, and spec limit references on every system boundary.

## 2) Implicit Interface Assumptions
Current SYS-0 collapse eligibility checks require only:

- non-empty `port_list`
- declared boundary invariant IDs

in `src/system/system_collapse_engine.py`.

Implicit assumptions not yet enforced at SYS level:

- port descriptor completeness (`port_type_id`, direction, allowed bundle IDs)
- signal descriptor completeness (`channel_type_id`, capacity/delay/access policy)
- rating/spec compatibility at system interface boundary

## 3) Existing Black-Box Candidates Without Full Signature
Existing abstraction/collapse-capable candidates that still need strict SYS signatures:

- engine/power module systems
- generator systems
- pump/compressor systems
- heat exchanger systems
- vehicle propulsion module systems

Current SYS-0 capsules preserve state and boundary invariant IDs, but do not enforce full interface descriptor/rating completeness.

## 4) Missing Signature Elements to Backfill
Required SYS-1 backfill on interface and invariant data:

- Port descriptors:
  - `port_id`
  - `port_type_id`
  - `direction`
  - `allowed_bundle_ids`
  - `spec_limit_refs`
- Signal descriptors:
  - `channel_type_id`
  - `capacity`
  - `delay`
  - `access_policy_id`
- Boundary invariant detail:
  - `invariant_kind`
  - `boundary_flux_allowed`
  - `ledger_transform_required`
- Macro capsule binding linkage:
  - `macro_model_set_id`
  - `model_error_bounds_ref`

## 5) Migration Direction
SYS-1 migration should:

- introduce deterministic system validation engine for interface/invariant/macro model checks
- run checks automatically in collapse/expand process paths
- refuse collapse/expand on invalid interface/invariant state
- preserve SYS-0 deterministic process-only mutation discipline
