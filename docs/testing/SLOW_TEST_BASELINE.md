Status: DERIVED
Last Reviewed: 2026-05-18
Supersedes: none
Superseded By: none

# Slow Test Baseline

## Current Slow Lane

| Test | Label set | Measured seconds | Timeout | Owner surface |
| --- | --- | ---: | ---: | --- |
| `tools_auditx` | `audit`, `auditx`, `slow`, `nightly`, `testx` | 798.97 | 1200 | AuditX scan artifacts |
| `tools_auditx_hash_stability` | `audit`, `auditx`, `slow`, `nightly`, `testx` | 15.95 | 1200 | AuditX canonical hash stability |
| `tools_auditx_changed_only` | `audit`, `auditx`, `slow`, `nightly`, `testx` | 9.47 | 1200 | AuditX changed-only behavior |

Measured shard total: 824.573 seconds.

## Policy

AuditX is slow because `tools_auditx` runs a cold full semantic scan and validates canonical artifact shape. It remains a required test. The remediation is explicit sharding and timeout policy, not skipping or weakening AuditX.

## Known Non-Performance Failures

| Test | Result | Disposition |
| --- | --- | --- |
| `slice0_hardcoded_ids` | FAIL | semantic lint repair |
| `slice1_hardcoded_constants` | FAIL | semantic lint repair |

These failures are not part of slow-test policy and must not be reclassified as warnings.
