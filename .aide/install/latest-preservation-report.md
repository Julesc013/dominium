# Install Preservation Report

- preserved_paths: 4331
- source_generated_skips: 0
- local_state_skips: 0
- secret_skips: 0
- managed_sections: 1
- no_apply: true

## Preservation Classes

- target `.aide/memory/**`, `.aide/queue/**`, generated reports, context packets, target golden tasks, docs/canon, tools, and manual AGENTS.md content are preserved by default.
- Source-generated state from `.aide/context/latest-*`, `.aide/reports/**`, `.aide/repo/*.json`, `.aide/roots/latest-*`, `.aide/tools/latest-*`, `.aide/refactors/current-*`, and `.aide/install/latest-*` is skipped.
- `.aide.local/**`, `.env`, secrets, raw prompts, and raw responses are never install candidates.
