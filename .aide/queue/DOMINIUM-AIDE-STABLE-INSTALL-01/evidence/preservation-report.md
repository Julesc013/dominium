# Preservation Report

## Preserved

- `.aide/memory/**`: preserved.
- `.aide/queue/**`: preserved, with only Q50 packet added.
- `.aide/context/dominium-doctrine-refs.md`: preserved.
- Existing `.aide/context/latest-*`: regenerated only by Dominium-local AIDE commands.
- `.aide/reports/dominium-*`: preserved or updated as Q50 top-level reports.
- Golden tasks: source portable golden tasks merged without deleting target catalog coverage.
- `AGENTS.md`: unchanged; manual doctrine and managed sections preserved.
- Doctrine/canon/spec/data refs: unchanged.
- XStack/AuditX/RepoX/TestX and existing validators: unchanged, not moved, not renamed, not executed unexpectedly.
- Product/source roots: untouched.
- `.aide.local/**`: untouched and ignored.

## Excluded Source State

- Source AIDE memory was not copied.
- Source AIDE queue/history was not copied.
- Source generated context/reports were not copied as target truth.
- Source local state, raw prompts, raw responses, and secrets were not copied.

