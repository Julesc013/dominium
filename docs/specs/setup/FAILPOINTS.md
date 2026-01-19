# Setup Failpoints

Failpoints allow deterministic failure injection for tests.

## Environment Variable
- `DSK_FAILPOINT=<name>`

## Supported Names
- `after_stage_extract`
- `after_verify`
- `mid_commit_step_N` (replace `N` with the step number, e.g., `mid_commit_step_3`)
- `before_write_state`

## Usage
- Windows: `set DSK_FAILPOINT=after_stage_extract`
- POSIX: `DSK_FAILPOINT=after_stage_extract`
