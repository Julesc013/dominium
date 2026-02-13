Status: DERIVED
Last Reviewed: 2026-02-13
Supersedes: none
Superseded By: none

# XStack Bottleneck Analysis

Source profile: `docs/audit/xstack/PROFILE_BASELINE.json` (STRICT, cold cache).

| Rank | Phase | Runtime (s) | % Total | Bound Type | Cached | Parallelizable | Incrementalizable |
| --- | --- | ---: | ---: | --- | --- | --- | --- |
| 1 | `subprocess.repox_runner` | 769.057 | 98.44% | CPU + IO mixed | Yes | No (root dependency) | Partial (via shared cache key) |
| 2 | `subprocess.testx.group.runtime.verify` | 7.434 | 0.95% | CPU | Yes | Yes | Yes |
| 3 | `subprocess.auditx.group.core.policy` | 6.409 | 0.82% | CPU + IO mixed | Yes | Yes | Yes |
| 4 | `subprocess.testx.group.core.invariants` | 3.427 | 0.44% | CPU | Yes | Yes | Yes |
| 5 | `plan.generate` | 1.296 | 0.17% | CPU | N/A | N/A | Yes |

## Findings

- The dominant bottleneck is cold `RepoX` execution; all other phases are low single-digit seconds.
- TestX/AuditX group execution is already sharded and parallelized, but was still paying avoidable misses across profiles before shared cache keys.
- Full mode originally risked unbounded runtime due monolithic verification behavior; that was reduced by profile-driven group selection and lightweight full-group sharding.

## Applied Impact Order

1. Cache-path stability fixes (`docs/audit/**` and tool cache directories excluded from state hash input).
2. Group command lightweighting (strict/full group runners avoid monolithic suite calls in default lanes).
3. Cross-profile cache sharing for stable runner commands.
4. Full-mode non-fail-fast scheduling (collect complete shard diagnostics instead of first-error abort).
5. Full-mode impacted-group selection by default (`DOM_GATE_FULL_ALL=1` to force exhaustive all-groups run).
