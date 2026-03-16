Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: UPDATE/BOOTSTRAP
Replacement Target: dedicated bootstrap updater once trust policy and remote acquisition are formalized

# Setup Self Update

## Model

`binary.setup` is treated as a normal component-graph binary component.

When the update plan upgrades `binary.setup`, setup follows the same governed process as any other binary:

1. resolve target release through `release_index.json`
2. verify target `release_manifest.json`
3. stage managed paths for upgraded components
4. replace setup only after verification succeeds
5. record the transaction in `.dsu/install_transaction_log.json`

## Safety Rules

- Self-update never changes `build_id`.
- Self-update never bypasses release-manifest verification.
- Setup replacement is staged through a temporary `.new` file and only committed with `os.replace`.
- If any update step fails after backup creation, the install root is restored from the recorded backup.

## Mock-Channel Behavior

- Self-update remains explicit; mock channel does not auto-apply.
- Missing signatures are non-fatal in mock, but hash verification is always required.
- Rollback remains available through the deterministic transaction log.
