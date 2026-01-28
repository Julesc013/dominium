# CONSTRUCTION MODEL

Construction MUST be a process chain: survey_site, prepare_ground, lay_foundation, place_part,
connect_interface, inspect, certify.
Structures MUST claim volume; volume conflicts MUST be detected deterministically.
Inspection and certification MUST be process-mediated and authority-gated.
Structures MUST fail if unsupported; failures MUST emit events and affect planning.

Construction MUST NOT assume prefab building types or UI placement modes.
Construction MUST NOT rely on "AI magic" or scripted outcomes.

References:
- docs/architecture/INVARIANTS.md
- docs/architecture/REALITY_LAYER.md
