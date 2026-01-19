# Setup Reproducibility Guarantees

## Byte-identical outputs (deterministic mode)
- `install_plan.tlv`
- `job_journal.tlv`
- `txn_journal.tlv`
- `installed_state.tlv`
- `setup_audit.tlv`
- CLI JSON outputs

## Allowed variance (non-deterministic mode)
- `run_id` may vary when deterministic mode is disabled.

## How to enable strict determinism
- CLI: `--deterministic 1`
- Request policy flag: `DSK_POLICY_DETERMINISTIC`

## Meta-test
- `ctest -R setup_conformance_repeat` runs the conformance suite twice and compares artifacts.
