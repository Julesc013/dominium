# PARTS AND ASSEMBLIES

Parts MUST be atomic, unitful components with interfaces and failure modes.
Assemblies MUST be graphs of parts with explicit connections.
Structures are assemblies with claimed volumes and ground support requirements.
Assemblies MUST fail deterministically when support constraints are violated.

Parts and assemblies MUST NOT assume human form factors or Earth-specific materials.
Parts and assemblies MUST NOT rely on "AI magic" or implicit stability.

References:
- docs/architecture/INVARIANTS.md
- docs/architecture/REALITY_LAYER.md
