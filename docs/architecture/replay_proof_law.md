Status: DERIVED
Last Reviewed: 2026-05-22
Supersedes: none
Superseded By: none
Stability: provisional
Task: REPLAY-PROOF-SLICE-01
Owner: contracts.replay

# Replay Proof Law

Replay proof records deterministic evidence for a bounded command path. It does not make a product, renderer, package runtime, save system, world simulation, or gameplay replay engine.

The first governed target is:

```text
dominium.package.mount.plan.v1
```

The command was chosen because `PACKAGE-MOUNT-SLICE-01` already provides fixture-level input, typed result, lock/report refs, diagnostics, refusals, and evidence without requiring package runtime execution.

## Model

The narrow replay/proof chain is:

```text
command input fixture
-> command/result schema refs
-> expected command result fixture
-> ordered replay event log
-> proof hash over canonical material
-> replay manifest
-> verification result
```

Replay material is derived evidence. It is not source truth. Stable identity must come from command IDs, schema IDs, artifact IDs, proof IDs, and replay IDs, not paths.

## Canonicalization

`REPLAY-PROOF-SLICE-01` uses:

```text
dominium.canonical_json.sorted_utf8.v1
sha256
```

Hashes are over canonical sorted UTF-8 JSON material. They are not over native object layout, pointer width, filesystem order, process order, timestamps, or platform-specific serialization.

## Refusal Behavior

Replay proof must refuse typed mismatch and unsupported claims. The first refusal set covers:

```text
dominium.refusal.replay.input_invalid
dominium.refusal.replay.expected_hash_missing
dominium.refusal.replay.hash_mismatch
dominium.refusal.replay.command_unknown
dominium.refusal.replay.unsupported_target
dominium.refusal.replay.evidence_missing
dominium.refusal.replay.noncanonical_input
dominium.refusal.replay.fixture_only_no_runtime_support
```

Mismatch is not degradation. A mismatched expected hash, missing evidence ref, unknown command, noncanonical input, or runtime support claim must remain refused until repaired or explicitly moved to a later reviewed implementation task.

## Non-Goals

This law does not implement:

```text
full replay runtime
save/load replay
world replay
gameplay replay
package runtime
provider runtime
runtime module loading
Workbench shell
renderer/native GUI
release support
```

Future runtime replay must derive from these contracts and provide its own conformance evidence before claiming implementation support.
