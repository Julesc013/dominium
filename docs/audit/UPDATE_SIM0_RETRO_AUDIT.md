Status: DERIVED
Stability: stable
Future Series: OMEGA
Replacement Target: Frozen offline update simulation baseline for v0.0.0-mock distribution gating.

# Update Simulation 0 Retro Audit

## Update Resolver And Transaction Logs

- Authoritative update resolution is implemented in `src/release/update_resolver.py`.
- `resolve_update_plan(...)` already computes deterministic plans for `policy.exact_suite`, `policy.latest_compatible`, and `policy.lab`.
- Release-index trust checks are already integrated through `verify_artifact_trust(...)` before plan acceptance.
- Update plans already record:
  - `deterministic_fingerprint`
  - `prior_component_set_hash`
  - `target_component_set_hash`
  - `selected_yanked_component_ids`
  - ordered verification steps
- Install transaction logs already preserve:
  - `resolution_policy_id`
  - `install_plan_hash`
  - `prior_component_set_hash`
  - `selected_component_ids`
- Rollback selection is already deterministic through `select_rollback_transaction(...)`.

## Release Index Policy And Yanking

- RELEASE-INDEX-POLICY-0 is already frozen through `tools/release/release_index_policy_common.py`.
- `policy.latest_compatible` excludes yanked candidates deterministically.
- `policy.exact_suite` may retain a suite-pinned yanked descriptor and must surface that selection explicitly.
- `policy.lab` may include yanked candidates only under explicit operator opt-in.
- Existing fixture coverage already exercises:
  - latest-compatible selection
  - yanked exclusion
  - rollback transaction field preservation

## Trust Enforcement

- UPDATE-MODEL-0 integrates trust checks at two points:
  - release-index trust inside `resolve_update_plan(...)`
  - release-manifest trust inside `tools/setup/setup_cli.py` during `setup update apply`
- Strict trust already refuses unsigned governed artifacts.
- Default mock trust already warns on unsigned artifacts without silently bypassing hash validation.

## Setup Command Surface

- Current deterministic setup entrypoints already exist:
  - `setup update check`
  - `setup update plan`
  - `setup update apply`
  - `setup rollback`
- `setup update apply` refuses on failed resolution, refuses on failed release-manifest verification, and returns explicit completion when no update is required.
- `setup rollback` restores from the recorded backup path chosen by the transaction log and appends a deterministic `update.rollback` transaction.

## Operational Constraints For Ω-6

- Ω-6 can remain fully offline by using local release-index fixtures only.
- Ω-6 does not need new update semantics; it needs a frozen harness around the existing resolver/apply/rollback path.
- Ω-6 must not weaken trust checks, relax yanked exclusion, or convert explicit no-op update completion into silent upgrade behavior.
