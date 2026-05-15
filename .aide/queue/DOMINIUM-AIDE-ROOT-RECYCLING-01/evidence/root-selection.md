# Root Selection

Status: needs_review

## Q51 Recommendation

Q51 recommended `ide/` as the first Q52 root family because it is small, tooling-adjacent, and outside product source, doctrine, and legacy tool-system roots.

## Current Available Roots

AIDE root inventory found 44 roots. Candidate low-risk families from the generic rule exist: `governance/`, `meta/`, `validation/`, `performance/`, and `ide/`.

## Selected Root Family

- Selected root family: `ide/`
- Selected root path: `ide/`
- Tracked files: 4
- Root status from AIDE: `review_required`
- Root risk from AIDE: `high`

## Why Selected

`ide/` was selected because Q51 explicitly recommended it, it has only four tracked files, and the root's generated project output boundary is already expressed through `.gitignore`:

- `/ide/**` ignored by default.
- `/ide/README.md` preserved.
- `/ide/manifests/**` preserved.

## Why Other Roots Were Deferred

- Product roots such as `runtime/`, `engine/`, `game/`, `apps/`, and `content/` are forbidden first-pilot roots.
- Doctrine/contract roots such as `docs/canon/`, `docs/planning/`, `specs/`, `data/`, and `contracts/` are protected or too semantically loaded for the first pilot.
- Tool roots such as `tools/`, `scripts/`, `validation/`, `repo/`, and `cmake/` are reserved for read-only evidence after Q51 tool absorption.
- `governance/` was deferred because Q51 flagged it as authority-sensitive.

## No-Apply Statement

Q52 does not move, delete, rename, rewrite, alias, shim, migrate, or apply any root change.
