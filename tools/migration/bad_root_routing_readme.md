Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Bad Root Routing Tool

`route_bad_roots.py` is a dry-run planner for MOVE-SCRIPT-00. It reads tracked paths with `git ls-files`, inspects only active former bad roots, proposes canonical target paths where the owner is clear, and records skipped/deferred items when a move would require identity, ABI/build, authority, import, reference, or naming review.

The tool does not move, delete, rename, rewrite references, create shims, apply move maps, apply salvage maps, or retire layout exceptions.

## Required Command

```powershell
python tools/migration/route_bad_roots.py --repo-root . --dry-run --rules tools/migration/bad_root_routing_rules.json --json-out .aide/reports/MOVE-SCRIPT-00-routing-preview.json --md-out .aide/reports/MOVE-SCRIPT-00-routing-preview.md --skipped-out .aide/reports/MOVE-SCRIPT-00-skipped-ledger.json --root-summary-out .aide/reports/MOVE-SCRIPT-00-root-summary.json --batch-plan-out .aide/reports/MOVE-SCRIPT-00-batch-plan.json
```

The Markdown companions for skipped, root summary, and batch plan are written next to their JSON outputs.

## Exit Policy

Default dry-run mode exits `0` if routing completed, even when paths are skipped. Use `--fail-on-collision` or `--fail-on-unknown` for stricter CI probes.

Nonzero exit codes mean a tool error or an explicitly requested fail condition. They do not apply moves.

## Safety Rules

The router skips rather than guesses when:

- no deterministic target route is known;
- a target path collides with tracked source or another planned target;
- identity-sensitive material lacks a clear target owner;
- ABI/build-sensitive material lacks a validation tier;
- active Python package/module material would need import rewrites or shims;
- normative authority material would be demoted to docs-only;
- generated evidence policy is unclear;
- the target path would introduce forbidden naming segments from NAME-00.

## Batch Mapping

- Batch B: `templates/`, `models/`, `modding/`
- Batch C: `data/`, `packs/`, `profiles/`, `bundles/`
- Batch D: `compat/`, `locks/`, `repo/`, `safety/`, `security/`, `specs/`, `updates/`
- Batch E: `validation/`, `meta/`, `governance/`, `performance/`
- Batch F: `core/`, `control/`, `net/`
- Batch G: `lib/`, `libs/`

The router produces planning evidence only. Later MOVE-BULK gates must authorize exact subsets before any `git mv` can run.
