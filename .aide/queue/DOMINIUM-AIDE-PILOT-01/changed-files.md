# Changed Files

Base commit before Q23: `5a3f5d84a5e3cdeda52cd4fcc4c682e120dbd9d0`

Q23 commits:

- `cd2eaafff` `chore: import aide lite pack`
- `14da8a822` `chore: initialize dominium aide state`
- `47d7d148f` `chore: generate dominium aide snapshot and task packet`
- `b0feec713` `chore: harden aide lite selftest boundary`
- `docs: record dominium aide import pilot evidence` records this evidence
  bundle and compact docs pointer.

Changed path classes:

- `.aide/**`: imported portable pack files, Dominium memory, generated context,
  task/review packets, route/cache metadata, verification/eval/token reports,
  target-local selftest fixture hardening, and Q23 evidence.
- `.aide.local.example/**`: example-only local-state boundary files from the
  portable pack; no real `.aide.local/` state.
- `.gitignore`: added `.aide.local/` ignore rules.
- `.gitignore`: added common Python cache ignores required by AIDE local-state
  validation.
- `AGENTS.md`: preserved existing canonical governance and added managed AIDE
  portable/adapter guidance sections.
- `docs/reference/aide-lite-import.md`: compact documentation pointer for this
  pilot.

Pre-existing uncommitted files preserved outside Q23 commits:

- `data/audit/validation_report_FAST.json`
- `docs/audit/VALIDATION_REPORT_FAST.md`

No Dominium product source files were changed.
