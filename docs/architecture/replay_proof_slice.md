Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: REPLAY-PROOF-SLICE-01
Owner: contracts.replay

# Replay Proof Slice

`REPLAY-PROOF-SLICE-01` proves one deterministic command-level replay/proof path. It uses package mount because that slice already has governed fixtures and does not require runtime package loading.

## Target

```text
command: dominium.package.mount.plan.v1
input: tests/contract/package/fixtures/valid_package_mount_input.json
result: tests/contract/package/fixtures/valid_package_mount_result.json
proof validator: tools/validators/contracts/check_replay_proof.py
```

## Proof Chain

```text
valid_package_mount_input.json
-> valid_replay_input_package_mount.json
-> valid_package_mount_result.json
-> valid_replay_expected_result_package_mount.json
-> valid_replay_event_log_package_mount.json
-> valid_proof_hash_package_mount.json
-> valid_proof_manifest_package_mount.json
-> valid_replay_manifest_package_mount.json
-> valid_replay_verification_result_package_mount.json
```

The app-level proof test recomputes the canonical hashes and checks that the verification result matches the proof hash.

## Negative Fixtures

The slice also records refused shapes for:

```text
hash mismatch
missing evidence
unknown command
noncanonical input
path-as-identity
world/runtime replay claim
fixture-only runtime support claim
expected result schema mismatch
```

These fixtures ensure replay proof is not used to silently promote unsupported runtime behavior.

## Relationship To Package Mount

Package mount remains fixture-level proof. The replay slice reuses package mount input/result/evidence refs and checks deterministic hash replay around them. It does not mount content, execute package payloads, load mods, select providers, or launch a product.

## Remaining Work

Later work may add broader replay contracts, runtime replay adapters, product replay, save/load proof, or gameplay simulation replay. Those tasks must provide new implementation evidence and must not treat this fixture proof as runtime support.
