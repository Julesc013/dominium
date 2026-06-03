Status: DERIVED
Last Reviewed: 2026-06-03
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Roots: `docs/archive/project_vision_corpus/`; `tmp/project_vision_corpus/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Future Codex Tasks

## PROJECT-VISION-SPEC-READINESS-01

Purpose: classify book claims into narrative, spec-ready, verification-needed, user-decision, and blocked categories.

Allowed paths: `docs/archive/project_vision_book/**` and a new derived spec-readiness output root.

Protected paths: canon, architecture, contracts, schema, implementation, release, and current queue state.

Expected outputs: spec-readiness map, user decision packet, verification queue, future task list.

Validation: docs checks, protected-path check, `git diff --check`, AIDE doctor and validate.
