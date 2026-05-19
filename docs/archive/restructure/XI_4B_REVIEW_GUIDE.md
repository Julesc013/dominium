Status: DERIVED
Last Reviewed: 2026-03-27
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: XI-5
Replacement Target: approved mapping lock for XI-5

# XI-4B Review Guide

## Read Order

1. `docs/restructure/XI_4B_UNBLOCK_REPORT.md`
2. `docs/restructure/STRUCTURE_OPTIONS_REPORT.md`
3. `docs/restructure/SRC_DOMAIN_MAPPING_REPORT.md`
4. `data/restructure/src_domain_mapping_lock_proposal.json`

## Decisions Required

- Approve preferred layout option `C` or choose an alternative.
- Resolve `48` conflicts where the mapping confidence stays below `0.72` or multiple domains remain plausible.
- Confirm the `40` bounded runtime-critical blockers that XI-5 must clear first.

## Xi-5 Prerequisites

- human approval of the provisional mapping lock
- explicit decision on attic routes
- explicit resolution of runtime-critical conflicts
- bounded XI-5 execution against the approved lock
