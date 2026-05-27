# 29. Context Transfer Packet for a Future Chat

## 29.1 Ultra-Condensed Bootstrap Brief

This chat focused on the Domino engine and Dominium game: what the project is, whether the engine is working, how to make it portable/modular/extensible, how to support CAD-like building and sparse destruction, whether B-Rep/CSG/NURBS should replace voxel-first construction, how to handle full-scale solar systems and planets, and how to sequence the project without making it impossible.

The core architecture established in the chat is: Domino should be the reusable deterministic simulation substrate; Dominium should be one game/rules/product layer on top. Engine owns mechanisms such as deterministic execution, Work IR/Access IR, domains, fields, replay, capabilities, registries, and law gates. Game owns meanings such as construction, fabrication, agents, economy, survival, civilization, and destruction. Client/render projects state and issues intents. Server/domain authority owns authoritative multiplayer truth.

The most important correction came near the end. The project has a real compiled deterministic substrate, but not a finished playable game engine. The user pasted a local readiness assessment: targeted build/tests and MP0 smoke paths reportedly pass, but the client advertises `support_claim_playable=false`; local playtest proof is blocked; server Python entrypoint has circular import issues; `session_create -> session_boot` is not hardened for the intended MVP bundle; and the time-anchor policy registry is missing/invalid. Therefore the next work is **Milestone 0: Make the baseline path honest** before any CAD/destruction/gameplay expansion.

Milestone 0 tasks: fix Python server/runtime circular import and CLI forwarding; make `session_create -> session_boot` pass for the intended baseline/MVP bundle; fix missing/invalid time-anchor policy registry; add one canonical repo-local playtest command; make `tools/validators/check_local_playtest_path.py --strict` pass; preserve/re-run local validation evidence as audit-grade logs.

After Milestone 0, the first game slice should be tiny: one deterministic accepted/refused build action, one deterministic removal/damage action, one replay/hash proof, one minimal projection/rendering path, and one pack-driven object/action. Do not start with full CAD, destruction, economy, agents, or broad multiplayer.

Long-term architecture: full-scale solar systems/planets/civilizations are possible only through collapsed multi-resolution domains, sparse overlays, event-driven schedules, fog-of-war epistemics, domain sharding, and proof-carrying client compute. Full fidelity everywhere is impossible. Unreal can help as a rendering/editor shell but should not be treated as the deterministic authoritative simulation substrate.

## 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted or corrected by the user.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences labelled as such.
7. Assistant suggestions not accepted by the user.
8. General model knowledge.

## 29.3 Operating Rules for Future Assistants

- Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels.
- Do not re-ask answered questions unless materially necessary.
- Verify stale repo facts and local build/test claims before relying on them as proof.
- Do not invent missing details.
- Do not treat assistant recommendations as final user decisions.
- Do not skip Milestone 0.
- Do not restart broad engine/game architecture discussion unless asked.
- Do not recommend CAD/destruction/MMO/universe work before baseline path is honest.
- Preserve artifacts and citations.
- Use structured task cards for implementation follow-up.

## 29.4 Active Workstreams

- WORKSTREAM-01: Maintain Domino/Dominium engine-game boundary.
- WORKSTREAM-02: Make baseline path honest.
- WORKSTREAM-03: Deterministic execution and proof.
- WORKSTREAM-04: Portability/modularity/reuse doctrine.
- WORKSTREAM-05: Pack/mod/capability architecture.
- WORKSTREAM-06: CAD/design/building substrate.
- WORKSTREAM-07: Geometry/destruction representation.
- WORKSTREAM-08: Sparse full-scale universe architecture.
- WORKSTREAM-09: Accessibility/low-performance support.
- WORKSTREAM-10: Preservation/spec aggregation.

## 29.5 Current Priorities

1. Fix local playtest blockers.
2. Make one canonical repo-local baseline command pass strict validation.
3. Verify or preserve user-reported local validation evidence.
4. Only then implement first deterministic build/remove slice.
5. Keep all ambitious systems as future contracts, not immediate tasks.

## 29.6 Current Open Questions

- What exact import graph causes the circular import?
- Which bundle should the baseline wrapper explicitly use?
- What time-anchor registry artifact is missing/invalid?
- What is the canonical playtest command interface?
- How should local validation evidence be captured?
- What minimal build action should follow Milestone 0?
- What future geometry provider strategy should be used?

## 29.7 Recommended First Action

Create an implementation prompt/task card for Milestone 0, starting with reproducing and fixing the server/runtime circular import and making `apps/server/server_main.py --help` or its canonical equivalent work without import failure.
