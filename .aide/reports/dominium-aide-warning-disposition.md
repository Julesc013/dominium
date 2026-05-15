# Dominium AIDE Warning Disposition

Status: needs_review

All Q53 warnings are classified in:

`.aide/queue/DOMINIUM-AIDE-OPERATING-BASELINE-01/evidence/warning-disposition.md`

Blocking:

- Git write permission blocks committing Q52/Q53 evidence.

Deferred non-blocking:

- Full eval timeout.
- Unknown repo/root/tool classifications.
- Generated controller reference warnings.
- XStack wrappers are integrated at registry/contract level only; legacy execution remains disabled pending per-wrapper proof.

Expected target-specific:

- Diff-scope warnings while Q52/Q53 evidence is dirty.
- Earlier stale test/selftest failures from non-working interpreter path are superseded by Python 3.14 PASS results.
- Python launcher/default interpreter mismatch in this sandbox.
