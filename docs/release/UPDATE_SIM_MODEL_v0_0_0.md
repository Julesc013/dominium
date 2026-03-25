Status: DERIVED
Stability: stable
Future Series: OMEGA
Replacement Target: Frozen offline update-channel simulation contract for v0.0.0-mock.

# Update Simulation Model v0.0.0

- update_sim_version = `0`
- stability_class = `stable`
- channel_id = `mock`
- execution_mode = `offline_only`

## Scope

Ω-6 freezes an offline update-channel harness for the existing update model. It proves that baseline install state, latest-compatible selection, yanked exclusion, trust refusal, and rollback all remain deterministic under local release-index fixtures.

## Scenario A: Baseline Install

- Install policy: `policy.exact_suite`
- Release index fixture: `data/baselines/update_sim/release_index_baseline.json`
- Entrypoint: `setup update plan` semantics via the authoritative resolver
- Expected outcome:
  - deterministic plan generation
  - no network access
  - selected component set matches the baseline suite snapshot
  - installed component set hash is recorded

## Scenario B: Latest-Compatible Upgrade

- Install policy: `policy.latest_compatible`
- Release index fixture: `data/baselines/update_sim/release_index_upgrade.json`
- Expected outcome:
  - a newer compatible component candidate is selected deterministically
  - plan hash is stable across repeated runs
  - apply path records the transaction metadata required for rollback

## Scenario C: Yanked Candidate Exclusion

- Install policy: `policy.latest_compatible`
- Release index fixture: `data/baselines/update_sim/release_index_yanked.json`
- Expected outcome:
  - yanked candidate is excluded from selection
  - `selected_yanked_component_ids` remains empty
  - skipped yanked candidates remain machine-visible through ordered explain rows

## Scenario D: Strict Trust Refusal

- Install policy: `policy.latest_compatible`
- Trust policy: `trust.strict_ranked`
- Release index fixture: `data/baselines/update_sim/release_index_strict.json`
- Expected outcome:
  - unsigned governed artifact is refused deterministically
  - refusal code and warnings are stable
  - no fallback to permissive trust behavior occurs

## Scenario E: Rollback

- Start from the baseline install state.
- Apply the deterministic latest-compatible upgrade.
- Roll back to the baseline release using the recorded install transaction log.
- Expected outcome:
  - restored component set hash matches the baseline component set hash
  - rollback transaction preserves `resolution_policy_id`, `install_plan_hash`, and `prior_component_set_hash`
  - no partial post-upgrade state remains

## Deterministic Rules

- All scenarios consume local release-index snapshots only.
- Candidate ordering remains governed by the existing update resolver.
- Yanking semantics remain governed by RELEASE-INDEX-POLICY-0.
- Trust semantics remain governed by TRUST-MODEL-0.
- Rollback selection remains governed by the install transaction log.
- No scenario may perform a silent upgrade, auto-migrate, or use wall-clock/network input.
