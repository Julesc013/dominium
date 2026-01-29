# FAQ

## Why not just simulate everything?

Because fully detailed simulation is impossible to scale and impossible to reproduce across platforms. Dominium models what matters using data‑driven processes, explicit budgets, and deterministic ordering. This keeps worlds believable without collapsing performance or correctness.

## Why not hardcode realism?

Hardcoded realism locks the platform to a narrow interpretation of the world. Dominium is built for many possible worlds, not one. Realism is a content choice, not a code decision.

## Why are there refusals?

Refusals are explicit “no” answers when required capabilities or constraints are missing. They prevent silent corruption and make behavior auditable. A refusal is a contract, not a crash.

## Why does my mod not load?

Most failures come from missing capabilities, invalid IDs, or schema violations. Run the validation tools and check the refusal payloads. Dominium will refuse instead of guessing.

## Why can’t old binaries run new mechanics?

New mechanics change meaning. Older binaries cannot honestly simulate what they do not understand. Dominium supports inspect‑only and replay modes for legacy builds, but it will refuse to fake behavior.
