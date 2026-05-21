Status: PROVISIONAL
Last Reviewed: 2026-05-22
Stability: provisional

# Workbench Document Patch Workflows

Workbench is not authority. Workbench inspectors display document state, diagnostics, evidence, and transaction history supplied by lawful contracts and commands.

A visual edit follows this sequence:

```text
pointer/key/menu gesture -> command intent -> capability/refusal check -> patch envelope -> transaction dry-run -> validation diagnostics -> evidence -> commit/export/refusal
```

Panels must not keep private truth. A drag, rename, text edit, property toggle, theme change, module descriptor edit, pack edit, or release/export adjustment is a nicer way to issue a lawful patch command.

Agent Work Board features may create, inspect, compare, and review transactions. They must show status, dry-run result, diagnostics, refusal refs, affected documents/artifacts, and evidence refs. They must not silently write source truth or package outputs outside an accepted transaction.

Future Workbench modules should use document refs for identity, artifact refs for persisted artifacts, patch refs for proposed changes, and transaction refs for accepted or refused change records.
