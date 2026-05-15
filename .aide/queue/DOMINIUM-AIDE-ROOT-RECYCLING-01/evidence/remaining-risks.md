# Remaining Risks

Status: needs_review

- Full AIDE `eval run` timed out.
- AIDE root inventory still marks 43 of 44 roots high-risk and all roots unknown-owned.
- Baseline AIDE classifier does not yet identify projection example JSON files as fixtures.
- `ide/` contains authority-sensitive and identity-sensitive files, so future moves require review.
- Root recycling beyond `ide/` remains blocked until Q53 establishes the operating baseline and a future task chooses another root family.
- Unknown file/tool classifications remain outside this selected-root pilot.
