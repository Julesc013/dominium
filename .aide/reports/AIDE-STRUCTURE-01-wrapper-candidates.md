# AIDE-STRUCTURE-01 Wrapper Candidates

## Recommended First Wrapper Family

Recommended first wrapper family: `aide_lite_validation_family`

Primary path:

- `.aide/scripts/aide_lite.py`

Candidate commands:

- `py -3 .aide/scripts/aide_lite.py tools validate`
- `py -3 .aide/scripts/aide_lite.py roots validate`
- `py -3 .aide/scripts/aide_lite.py repo validate`
- `py -3 .aide/scripts/aide_lite.py xstack validate`

## Reason

This family is the safest next wrapper target because prior AIDE baseline,
DCHECK, DOM-AIDE-02, and AIDE-STRUCTURE-00 evidence show it validates no-apply
control-plane evidence and keeps legacy tool execution disabled. It is useful
for future root recycling and tool absorption without running unknown XStack,
AuditX, RepoX, or TestX commands directly.

## Execution Recommendation

- `execution_allowed`: false by default
- `apply_allowed`: false
- `network_allowed`: false
- `writes_allowed`: false unless the exact wrapper contract limits writes to
  reviewed `.aide/**` evidence
- unknown tool execution: false

## Ranked Candidates

| Rank | Candidate | Disposition | Notes |
|---|---|---|---|
| 1 | AIDE Lite validation family | Recommended | Best evidence, no-apply, legacy execution disabled. |
| 2 | `tools/build/validate_build_contract.py` | Good second candidate | Read-only build contract validation, no binary build. |
| 3 | Distribution/component validators | Good second candidate | Passed validation; document Python 3.8 TOML fallback warning. |
| 4 | Repo layout/root allowlist validators | Deferred | Useful, but strict runs are blocked by ignored generated `build/` and `out/` roots in this checkout. |
| 5 | Supplemental docs/build/UI/ABI validators | Deferred | Passed as validation, but scripts remain existing surfaces to wrap later without modifying `scripts/**`. |

## Required Contract Path For Next Task

Suggested path:

- `.aide/tools/wrapper-contracts/aide-structure-02.validation-family.toml`

## Blockers

- Unknown/high-risk tools remain preserved but execution-disabled.
- Broad XStack FAST/FULL, full CTest, full eval, package generation, release
  publication, and GitHub mutation remain out of scope.
- Existing repo layout/root allowlist strict validators are blocked by ignored
  local generated `build/` and `out/` roots.
- No old tool renames should begin until wrappers and consumer references are
  proven.
