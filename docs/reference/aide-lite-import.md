# AIDE Lite Import

Dominium has a local AIDE Lite import under `.aide/` for compact
doctrine-aware task packets and review evidence.

Use `.aide/context/latest-task-packet.md` as the compact task handoff when a
future task explicitly opts into AIDE Lite context. Full Dominium doctrine
remains authoritative in repo docs and specs; AIDE packets should cite those
paths rather than inline whole doctrine files.

Local state, credentials, traces, raw prompts, and raw responses belong outside
the repo under `.aide.local/`, which is gitignored. The committed
`.aide.local.example/` directory contains examples only.

Q23 evidence lives at `.aide/queue/DOMINIUM-AIDE-PILOT-01/`.

Q33 canonical governance sync evidence lives at
`.aide/queue/DOMINIUM-AIDE-SYNC-01/`. The sync imported portable commit,
WorkUnit recovery, changelog preview, and Git workflow governance from the
canonical AIDE Lite Pack without copying AIDE source queue/history, source
memory, generated branch reports, or Dominium doctrine content into AIDE
memory.
