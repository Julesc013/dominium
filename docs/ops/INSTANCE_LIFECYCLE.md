Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Instance Lifecycle (DEV-OPS-0)

Scope: instance creation, migration, and retirement.

Lifecycle states
1) Create
   - instance manifest written
   - capability lockfile generated
2) Verify
   - compat_report generated
   - packs resolved
3) Run
   - server/client operate using lockfile
4) Update
   - lockfile updated explicitly
   - compatibility re-verified
5) Migrate
   - schema migrations executed explicitly
   - replay hash stability verified
6) Archive
   - instance frozen and marked read-only

Rules
- No implicit migrations.
- No cross-instance profile mutation.
- Instances remain traceable via lineage.

Artifacts
- install.manifest.json
- instance.manifest.json
- capability.lockfile.json (or equivalent)
- compat_report.json
