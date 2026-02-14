Status: DERIVED
Last Reviewed: 2026-02-14
Supersedes: none
Superseded By: none

# Governance Final Report

## Validation Runs

- `gate.py verify --profile-report` passed.
- `gate.py strict --profile-report` (cold) passed.
- `gate.py strict --profile-report` (warm) passed.
- `gate.py full --profile-report` passed.
- `python tools/auditx/auditx.py scan --changed-only --format json` passed.

## Runtime Metrics

From `docs/audit/xstack/PROFILE_*.json`:

- STRICT cold runtime: `897.040s` (`cache_hits=0`, `cache_misses=4`)
- STRICT warm runtime: `0.053s` (`cache_hits=4`, `cache_misses=0`)
- FULL runtime: `1023.451s` (`cache_hits=0`, `cache_misses=9`)
- FAST warm runtime: `0.003s` (`cache_hits=3`, `cache_misses=0`)

## Cache and Incremental Behavior

- Warm STRICT reused the strict plan hash and produced full cache-hit replay.
- FULL executed sharded TestX/AuditX groups in parallel and completed with deterministic aggregation.
- RepoX emits per-group profile telemetry to `docs/audit/repox/REPOX_PROFILE.json`.

## Remaining Known Risks

- Cold RepoX remains the dominant throughput bottleneck.
- STRICT/FULL target throughput is achieved for warm-cache workflows but not for cold-cache runs.
- Additional RepoX dependency narrowing is still required to reduce cold-path cost.

