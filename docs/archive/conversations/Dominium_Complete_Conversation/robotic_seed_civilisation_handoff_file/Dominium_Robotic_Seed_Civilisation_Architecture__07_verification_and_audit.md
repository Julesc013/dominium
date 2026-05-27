# SELF-AUDIT AND REVISION — Dominium Robotic Seed-Civilisation Architecture

## 32. Adversarial Self-Audit

| Issue | Severity | Correction needed | Correction applied? | Residual risk |
|---|---|---|---|---|
| Potential overstatement of assistant recommendations as decisions | High | Label assistant recommendations separately and mark not ratified. | Yes | Future merger could still ignore labels. |
| Possible hidden prior chat not visible | Medium | State access limitation and scope. | Yes | Cannot recover invisible turns. |
| User brainstorm contains tentative language | High | Mark many items as tentative design directions. | Yes | Some user-stated preferences may later change. |
| External facts from assistant answers could be stale | Medium | Place Unreal/NASA/MMO facts in verification queue. | Yes | Needs future browsing/research. |
| Very large request could cause over-compression | Medium | Create files with detailed registers and in-chat summary. | Yes | In-chat answer may still be shorter than full files. |
| Artifact confusion: uploaded file is instruction prompt, not gameplay artifact | Low | Identify uploaded file accurately as preservation prompt. | Yes | None significant. |
| Risk of missing no-NPC rationale | High | Added decision, rejected option, risk, tasks, and narrative coverage. | Yes | Future spec must still address city liveliness. |
| Risk of missing first vertical slice | High | Added tasks and recommended first action. | Yes | Needs conversion into separate detailed spec. |
| Risk of not preserving rejected ideas | Medium | Created rejected/superseded register. | Yes | Some minor rejected ideas may remain implicit. |
| Risk of treating official MMO as launch requirement | Medium | Marked MMO as active but high uncertainty. | Yes | User still needs to decide mode priority. |

## 33. Corrections Applied

The package explicitly distinguishes FACT, INFERENCE, and UNCERTAIN / UNVERIFIED items; marks Domino/Unreal and vertical-slice recommendations as assistant-derived unless accepted later; identifies the uploaded file as the preservation prompt; moves current/external facts to verification; and preserves rejected/deprioritised options including worker NPC labour, manual planet painting as primary workflow, arbitrary sliders, unlimited mothership fabrication, and per-part machine simulation.

## 34. Final Reliability Assessment

* Completeness rating: 4/5 for visible chat.
* Reliability rating: 4/5 for visible chat, 3/5 for external technical claims until verified.
* Human-readability rating: 4/5.
* Aggregation-readiness rating: 4/5 with caveats.
* Main remaining uncertainty sources: hidden/invisible prior context, lack of user ratification for assistant recommendations, unverified Unreal/software/science claims, no exact implementation details yet.
* Manual review before merge: Yes. The aggregator should especially review decisions DECISION-11 and DECISION-12 and confirm which brainstorm ideas become formal requirements.

## Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Current Unreal Engine 5/6 capabilities: LWC, World Partition, MassEntity, Iris, Nanite, runtime mesh/dynamic terrain, networking limits. | Engine features change over time and prior assistant answers used potentially stale external facts. | Official Unreal documentation and prototype tests. | P1 | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | JPL Horizons/SPICE/IAU data suitability and licensing for real Solar System recreation. | Real-data pipeline and licensing/provenance matter. | NASA/JPL/NAIF/IAU documentation and license review. | P1 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Physical plausibility models for atmosphere retention, climate, orbital stability, tidal locking, magnetospheres, and planet generation. | Science-bounded generator requires reliable models. | Planetary science references and simplified gameplay model review. | P1 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Determinism risks across CPU/GPU/platforms, floating point, multithreading, and physics. | Domino’s premise depends on deterministic replay. | Technical prototype tests and deterministic-simulation literature. | P0 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Sparse terrain/voxel/SDF storage and runtime meshing options. | Cut/fill and terraforming depend on practical editable terrain representation. | Engine research, prototypes, storage tests. | P0 | WORKSTREAM-03 / WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | MMO scalability strategies and realistic player-count claims. | Initial question asked about millions, shards, low latency, high FPS. | Network architecture research, MMO case studies, load testing. | P1 | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Security model for client-shared compute with fog-of-war and anti-cheat. | Client compute was proposed but is risky. | Security review and adversarial testing. | P1 | WORKSTREAM-07 / WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
