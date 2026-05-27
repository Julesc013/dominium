# Reader Brief — AIDE_XStack_Dominium_Refactor_Control_Plane

## What this chat was about

This chat developed the architecture and migration strategy for AIDE, XStack, and Dominium. It started from improving AI coding workflows and ended with a concrete plan: AIDE becomes the repo-native operating/refactor control plane; XStack becomes Dominium’s strict local profile and legacy validation layer; Dominium cleanup proceeds through AIDE-controlled root recycling.

## Top 20 things to know

1. AIDE is not a full coding agent first.
2. AIDE first ships Profiles + Harness + Compatibility + Dominium Bridge.
3. XStack remains Dominium strict profile, not public general product.
4. Old XStack/AuditX/RepoX/TestX checks are valuable.
5. Old X names should eventually retire behind AIDE adapters.
6. Dominium currently builds but is not CTest-clean.
7. POST-CONVERGE-10E improved AuditX blockers but left unit/RepoX blockers.
8. Feature work should wait.
9. Root cleanup must be file-by-file root recycling.
10. Every file gets one fate: Keep, Adapt, Extract, Convert, Archive, Drop.
11. AIDE should own install/repair/upgrade/rollback plans before wide use.
12. AIDE should support dev/main/task branch discipline.
13. Generated outputs are not canon unless promoted.
14. Target repo truth wins over AIDE pack defaults.
15. Versions identify releases; capabilities decide compatibility.
16. External projects are pattern sources, not foundations.
17. Graph tools may help but are derived artifacts.
18. AIDE Runtime/Gateway/Hosts are deferred until QCHECK-04.
19. Live repo state must be rechecked before implementation.
20. This package is the current human and aggregator handoff.

## Best next step

Verify live AIDE and Dominium heads. If Dominium remains at/near POST-CONVERGE-10E, generate a bounded WorkUnit for `invariant_units_present` and `inv_repox_rules` remediation/classification. In parallel, ensure AIDE Q35 and QCHECK-03 are complete before Q36-Q42 work.
