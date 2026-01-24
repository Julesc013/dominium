# Infinite Detail

Infinite detail is achieved through bounded refinement, not through unlimited
storage or hidden computation.

## Binding rules
- All refinement MUST be requested through the refinement contract.
- All refinement MUST be LOD-bounded and budget-bounded.
- All refinement MUST be collapsible without changing objective truth.
- No refinement may assume a privileged physics or realism baseline.

## How infinite detail is safe
- Refinement is lazy: detail is materialized only when explicitly requested.
- Refinement is bounded: each request declares maximum cost and LOD band.
- Refinement is collapsible: coarse truth remains valid after detail is removed.
- Unknown data is preserved: absence of detail is explicit, not an error.

## Consequences
- Infinite universes are possible with finite storage.
- Procedural and authored data coexist without hierarchy.
- Real-world overlays refine; they never replace or force defaults.
