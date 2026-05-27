# Reader Brief — Domino/Dominium Portability, Assurance, and Future-Proof Architecture

## What this chat was about

Domino/Dominium future-proof architecture: standards-informed assurance, portability, modularity, extensibility, replaceability, public contracts, data compatibility, deterministic replay, testing, and preservation.

## Top 20 things to know

- The explicit user requirement is portable, modular, extensible, reusable, replaceable, future-proof code.
- The strongest proposed doctrine is stable public contracts with replaceable internals.
- Domino should be reusable engine/runtime/toolchain; Dominium should be one product using it.
- Modularity must be proven by conformance tests, not just folders.
- Data compatibility is as important as code compatibility.
- Saves, packs, replays, schemas, protocols, IDs, and migrations need policy from the beginning.
- Standards should inform the project but not become compliance claims.
- DDAP/DIL is proposed, not yet user-ratified.
- The actual repo was not inspected.
- The best next action is repo boundary audit plus first policy/registry/conformance pilot.

Additional points: DDAP/DIL is proposed; repo not inspected; conformance tests prove modularity; data compatibility must be formalized; generated output needs validation; future aggregation must preserve recommendation-vs-decision labels.

## Decisions

See `04_registers.md`, especially DECISION-01 through DECISION-09.

## Pending tasks

Highest priority: TASK-02, TASK-03, TASK-04, TASK-05, TASK-06, TASK-10.

## Open questions

Main unresolved issues: DDAP acceptance, actual repo structure, stable boundary list, toolchain strictness, first conformance pilot, compatibility guarantees.

## Artifacts

Primary artifacts: user standards paste, assistant DDAP answer, user portability question, assistant architecture answer, uploaded preservation prompt, generated files.

## Verification items

Verify standards, repo structure, toolchain targets, persistent formats, and cross-chat conflicts.

## Best next step

Inspect the actual repo and create a boundary audit.
