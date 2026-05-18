# MOVE-ROUTER-02 Root Exception Repairs

Status: PASS_WITH_WARNINGS
Generated: 2026-05-18

All configured former bad roots have zero tracked files after MOVE-ROUTER-01 and
the MOVE-ROUTER-02 repair pass.

## Current Matrix

- Bad roots checked: 24.
- Tracked files under bad roots: 0.
- Nonempty bad roots: 0.
- Nonempty bad roots without exception: 0.

Strict root/layout validators pass at this boundary. Remaining failures are
active reference, import, registry, frozen-hash, and test-path failures, not
tracked bad-root presence.
