# AIDE-STRUCTURE-02 Wrapper Plan

## Status

- Status: PROVISIONAL
- Result target: PASS_WITH_WARNINGS
- Scope: `.aide/**`, `docs/aide/**`, `tools/aide/**`

## Selected Command Family

The first implementation wraps the AIDE-native validation family:

- `aide.tools`
- `aide.roots`
- `aide.repo`

These commands are backed by AIDE Lite validators already used in the operating
baseline and AIDE-STRUCTURE-01 wrapper-candidate evidence.

## Command Names

| AIDE command | Underlying command |
| --- | --- |
| `aide.tools` | `py -3 .aide/scripts/aide_lite.py tools validate` |
| `aide.roots` | `py -3 .aide/scripts/aide_lite.py roots validate` |
| `aide.repo` | `py -3 .aide/scripts/aide_lite.py repo validate` |

## Execution Status

Execution is enabled for this small family because the commands are read-only,
no-apply AIDE validators with prior baseline evidence. The command contract
still forbids apply behavior, network access, writes, and unknown tool
execution.

## Dry-Run Status

Dry-run is supported for every selected command. Dry-run prints the underlying
command and does not execute it.

## Blockers

- Unknown and high-risk tools remain preserved but execution-disabled.
- Broad XStack/AuditX/RepoX/TestX commands are not wrapped here.
- Full eval, full CTest, build, package, release, and GitHub mutation remain
  deferred.
- Strict legacy repo layout validators may still fail locally when ignored
  generated roots such as `build/` and `out/` are present.

## Next Wrapper Candidates

- Existing strict distribution and component validators once local generated
  root blockers are separated from execution proof.
- Build contract validation if it remains read-only and evidence-backed.
- Additional AIDE-native quality/status wrappers after contract review.
