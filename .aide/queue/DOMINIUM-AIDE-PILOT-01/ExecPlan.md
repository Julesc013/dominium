# ExecPlan

1. Verify Dominium repo identity, dirty state, canonical governance, source pack
   availability, and pack manifest/policy/checksum metadata.
2. Import only portable AIDE Lite target files; preserve existing `AGENTS.md`;
   keep source AIDE queue, memory, generated context, reports, local state,
   credentials, raw prompts, and raw responses out of Dominium.
3. Initialize Dominium-specific `.aide/profile.yaml` and compact memory files.
4. Generate Dominium-local snapshot, repo map, test map, context packet, task
   packet, review packet, route/cache metadata, verification report, token
   ledger, and golden-task evidence.
5. Measure compact packet size against an objective doctrine-heavy baseline.
6. Record import, doctrine, quality, validation, changed-files, and risk
   evidence; leave status as `needs_review`.

Non-goals: no Dominium product implementation, runtime work, doctrine rewrite,
Gateway forwarding, provider/model/network calls, or autonomous loop.
