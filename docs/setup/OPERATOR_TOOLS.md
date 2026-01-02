# Setup Operator Tools

## Commands
- `dominium-setup doctor --state <file> --plan <file> --journal <file> --txn-journal <file> --audit <file> [--json]`
- `dominium-setup explain-refusal --audit <file> [--json]`
- `dominium-setup audit dump --in <file> --out <file> --format json`

## Diagnostics
- `doctor` validates TLVs and reports actionable issues.
- `explain-refusal` maps refusal codes to stable labels.
- `audit dump` emits deterministic JSON for audit evidence.

## Determinism
- JSON outputs use stable key ordering.
- No timestamps when deterministic mode is enabled.
