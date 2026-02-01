Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# SLICE-1 Contract





Purpose: prove local physical truth, deterministic failure, and inspectable causes


without hardcoded world assumptions or new simulation systems.





Scope (binding for SLICE-1):


- engine/, game/, data/, client/, tools/, docs/architecture/, docs/examples/, tests/


- Documentation and tests may be added/updated.





Non-goals (binding for SLICE-1):


- No scale, delegation, trade, or civilization systems.


- No Earth/Sol assumptions or any era-specific behavior.


- No new simulation systems; extend existing Field and Process systems only.





Required behaviors:


1) Field extensions (generic, unitful, LOD-aware, unknown-by-default):


   - support_capacity


   - surface_gradient


   - local_moisture


   - accessibility_cost


2) Epistemic survey process:


   - survey_local_area refines subjective knowledge only.


   - confidence/uncertainty tracked.


3) Transformative processes (parameterized, deterministic):


   - collect_local_material


   - assemble_simple_structure


   - connect_energy_source


   - inspect_structure


   - repair_structure


   Each declares required fields, capabilities, authority, time/resource costs,


   and explicit failure conditions.


4) Failure is expected and recorded:


   - support_capacity, surface_gradient, resource, energy, inspection, and


     epistemic failures must emit events and persist.


   - No silent corrections or implicit defaults.


5) Movement and interaction:


   - constrained by policy and by accessibility_cost.


   - deterministic and auditable.


6) Observability:


   - CLI/TUI/GUI expose local topology, known vs unknown fields,


     intent and plan, event log, and refusal/failure reasons.


7) Save/load/replay:


   - saves embed full WorldDefinition and unknown fields.


   - failures replay identically; subjective knowledge divergence is replayed.





Replaceability rules:


- All behavior is routed through WorldDefinition, Fields, Processes,


  and policy/law/capability systems.


- All SLICE-1 logic must be safe to replace or extend later.





SLICE-1 completion is defined by the acceptance checklist in


`docs/roadmap/SLICE_1_ACCEPTANCE.md`.
