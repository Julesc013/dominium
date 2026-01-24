# Validation Checker

Status: canonical.
Scope: offline comparison and invariant checks for tool outputs.
Authority: canonical. This tool MUST fail loudly on mismatch.

## Purpose
- Compare expected vs actual tool outputs.
- Detect mismatches in refinement requests and plan summaries.
- Emit optional reports under `build/cache/assets/`.

## Rules
- Validation MUST NOT modify pack data.
- Validation MUST NOT assume engine runtime state.
- Any mismatch MUST be reported explicitly.
