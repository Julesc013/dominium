# Import Report

Source pack:

- `D:/Projects/AIDE/aide/.aide/export/aide-lite-pack-v0`
- manifest schema: `q21.aide-lite-pack-manifest.v0`
- source repo: `julesc013/aide`
- source commit recorded by pack: `e2088aed6dd32674c00b8d4701ce8c8be784fdde`

Import method:

- Ran source command dry-run:
  `py -3 D:/Projects/AIDE/aide/.aide/scripts/aide_lite.py import-pack --pack D:/Projects/AIDE/aide/.aide/export/aide-lite-pack-v0 --target . --dry-run`
- Dry-run result: 127 operations, 0 conflicts, no provider/model/network calls.
- Performed manual manifest/policy-guided import because the command importer
  would also copy broad `core/**` and `docs/reference/**` pack surfaces outside
  Q23's target path scope.

Imported portable target files:

- `.aide/**` portable scripts, policies, prompts, context config, verification
  templates, eval starter templates, routing/cache/provider/gateway metadata,
  and adapter templates.
- `.aide.local.example/**` example-only local-state boundary files.
- Managed AIDE guidance sections in `AGENTS.md`.
- `.gitignore` `.aide.local/` protection.

Excluded source-state classes:

- no source AIDE `.aide/queue/` history
- no source AIDE `.aide/memory/project-state.md`, decisions, or open risks
- no source AIDE generated context
- no source AIDE generated reports
- no source AIDE latest route decisions
- no source AIDE cache-key reports
- no source AIDE Gateway status reports
- no source AIDE provider status reports
- no source AIDE controller/outcome ledgers
- no `.aide.local/`
- no `.env`
- no provider keys, credentials, raw prompts, or raw responses

Target initialization:

- `.aide/profile.yaml` is Dominium-specific.
- `.aide/memory/project-state.md`, `decisions.md`, and `open-risks.md` describe
  Dominium and Q23, not AIDE source state.
- Snapshot, repo map, context packet, task packet, review packet, route/cache
  reports, token ledger, verifier report, and eval reports were generated inside
  Dominium after import.

Existing guidance:

- Existing `AGENTS.md` was preserved. AIDE added managed sections rather than
  replacing canonical governance.
- Existing `CLAUDE.md` was inspected and not modified.
- A target-local selftest fallback was added inside `.aide/scripts/aide_lite.py`
  so optional tests can validate Gateway/provider no-call metadata without
  importing live source `core/**` into Dominium.
