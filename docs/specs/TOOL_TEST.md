Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# dominium-tools test

Deterministic test runner.

Usage:
```
dominium-tools test --suite <name> [--filter <pattern>] [--seed <n>]
```

- Runs a small set of deterministic smoke scenarios using a fixed seedable simulation hash.
- Reports PASS/FAIL per scenario; non-zero exit code on any failure or if no test matches filter.
- Uses `dsys_*` init/shutdown for consistent platform setup (no graphics required).