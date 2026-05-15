# AIDE Command Contracts

AIDE command contracts define stable wrapper surfaces for Dominium checks.
The wrapper name is the future-facing command; the current tool path remains
behind the adapter until evidence proves it can be migrated.

These contracts are deliberately conservative:

- old tools are preserved behind wrappers;
- unknown tools are not executed;
- commands are no-apply unless a contract explicitly allows otherwise;
- network and writes are disabled by default;
- wrappers do not rename, move, delete, or weaken existing validators.

Use these contracts as planning and execution boundaries for AIDE-controlled
validation. Do not treat transitional names such as XStack, AuditX, RepoX, or
TestX as durable Dominium architecture.
