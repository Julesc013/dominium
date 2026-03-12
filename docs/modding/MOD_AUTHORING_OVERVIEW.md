Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Mod Authoring Overview

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.






Status: canonical.


Scope: mandatory rules for all mods.


Authority: canonical. All mods MUST follow this.





## Core rule


Mods add layers. Mods do not rewrite truth.





## Binding rules


- Mods MUST provide capabilities and refinement layers, not engine behavior.


- Mods MUST declare precedence explicitly in refinement plans.


- Mods MUST remain removable without corrupting objective truth or saves.


- Mods MUST preserve determinism under the same seeds and inputs.





## Precedence order


- Base content < DLC < Mod < Save/local override.


- If multiple mods overlap, precedence MUST be explicit; load order MUST NOT be relied upon.





## Removal safety


- Removing a mod MUST degrade explicitly or freeze affected views.


- Removing a mod MUST NOT mutate or delete objective truth.





## References


- `docs/architectureitecture/COMPATIBILITY_PHILOSOPHY.md`


- `docs/worldgen/REFINEMENT_CONTRACT.md`
