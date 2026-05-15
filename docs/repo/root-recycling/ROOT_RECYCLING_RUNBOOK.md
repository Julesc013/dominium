# Root Recycling Runbook

1. Choose a root family.
2. Inventory the root.
3. Classify files.
4. Scan references and sensitivity markers.
5. Generate a draft salvage map.
6. Review risks.
7. Approve a move map in a later task.
8. Apply a small wave only after approval.
9. Rewrite references only in the approved task.
10. Run validators/build/test as required.
11. Update exception ledgers.
12. Retire shims only after evidence.

First inventories and reconciliation are evidence only. Move-wave selection is separate from move-wave application. Content/package roots require identity scans; authority roots require authority scans; core/control/net require semantic scans; lib/libs require ABI/build scans.
