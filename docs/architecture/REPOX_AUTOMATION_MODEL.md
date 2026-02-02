Status: CANONICAL
Last Reviewed: 2026-01-29
Supersedes: none
Superseded By: none
STATUS: CANONICAL
OWNER: architecture
LAST_VERIFIED: 2026-01-29

# RepoX Automation Model (REPOX-AUTO-0)

This document is the canonical representation of PROMPT REPOX-AUTO-0.

Normative rules:
- RepoX must run the mandatory phase graph in order with no skips.
- Generated artifacts are tracked, regenerated, and must not be hand-edited.
- Pre-commit and pre-push hooks must block violations.
- RepoX generates changelogs; BUILD_NUMBER increments only after successful push.
- CI must run full RepoX + TestX and publish the Canon Compliance Report.
