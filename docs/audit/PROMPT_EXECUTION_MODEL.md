Status: DERIVED
Last Reviewed: 2026-02-07
Supersedes: none
Superseded By: none

# Prompt Execution Model (Content-Verified Gates)

Git tags are **not** execution gates.

Canon state is asserted by:
- RepoX
- TestX
- `repo/canon_state.json`

Prompts that say “verify canon-clean-2 tag exists” are interpreted as:
“verify `repo/canon_state.json` + RepoX + TestX”.

Prompt text is not modified; this document is an interpretation layer only.
