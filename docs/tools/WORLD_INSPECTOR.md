# WORLD INSPECTOR

World inspection MUST read field layers and topology through observation stores only.
Queries MUST support LOD and scope filters and MUST surface unknown/latent values explicitly.
Inspection MUST NOT assume geometry is authoritative; geometry is derived.
Inspection MUST be deterministic and read-only.

References:
- docs/arch/INVARIANTS.md
- docs/arch/REALITY_LAYER.md
