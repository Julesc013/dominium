# Verification and Audit — Dominium Deterministic Solar-System Architecture

## Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Current Unreal Engine capabilities and limitations for Large World Coordinates, World Partition, Iris, Replication Graph, MassEntity, PCG, runtime mesh/geometry, and networked physics. | Assistant made feasibility claims based on sources that may change. | Official Unreal Engine documentation and prototype tests. | P1 | WORKSTREAM-11 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Current JPL Horizons/SPICE/IAU data access, licensing, and suitability for real Solar System data. | Real-data planet/system generation may depend on external datasets and licensing. | NASA/JPL/NAIF/IAU official sources and license review. | P1 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Feasibility of deterministic fixed-point/double hybrid for planet-scale coordinates. | Core architecture depends on precision and determinism. | Prototype benchmarks and deterministic replay tests. | P0 | WORKSTREAM-01 | INFERENCE |
| VERIFY-04 | Network scale assumptions for millions across shards versus in one interaction bubble. | Marketing/scope claims must be accurate. | Load tests, MMO architecture references, bandwidth/server budget estimates. | P1 | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Sparse terrain/delta representation performance for cut/fill at intended resolution. | Terraforming and construction depend on it. | Prototype with voxel/SDF/field deltas and chunk meshing. | P0 | WORKSTREAM-03, WORKSTREAM-06 | INFERENCE |
| VERIFY-06 | Whether player-created machine graphs can be made expressive while compiling safely. | A core gameplay promise may be technically hard. | Compiler design prototype and exploit tests. | P0 | WORKSTREAM-07 | INFERENCE |


## 32. Adversarial Self-Audit

| Issue | Severity | Correction needed | Correction applied? | Residual risk |
| --- | --- | --- | --- | --- |
| Assistant recommendations could be mistaken for user decisions. | High | Label recommendations as INFERENCE and decision status as recommended/not accepted. | Yes | Future aggregation could still over-promote them. |
| The chat contains broad brainstorms that may not be final. | High | Preserve tentative status and open questions. | Yes | User review still required. |
| External Unreal/NASA/JPL/network scale claims may be stale. | Medium | Move them to verification queue. | Yes | Requires later web/source verification. |
| The user’s “galaxy” terminology may be ambiguous. | Medium | Record as open question: star system versus galaxy scope. | Yes | Needs explicit scope decision. |
| No direct access to hidden prior project history. | Medium | State access as partial and source scope as this chat. | Yes | Other chats may contain conflicting decisions. |
| Risk of over-compressing the anti-NPC automation shift. | High | Give it a dedicated topic, decision, risk, and spec contribution. | Yes | Aggregator must preserve it. |
| Generated file package must not be claimed before creation. | High | Files are created in section 35 and linked after creation. | Yes | None after export. |
| Some user preferences are inferred from tone and repeated design moves. | Medium | Mark inferred preferences separately. | Yes | User may correct them. |


## 33. Corrections Applied

Corrections applied during assembly:

- Decision statuses were revised to distinguish user-stated directions from assistant recommendations.
- Unreal and external data-source claims were moved to the verification queue rather than treated as stable facts.
- The “galaxy versus star system” ambiguity was recorded as QUESTION-01.
- The anti-worker-NPC automation shift was added to decisions, preferences, rejected options, risks, and spec-book contributions.
- The mothership’s finite-resource role was separated from its knowledge/recipe role to avoid implying unlimited fabrication.
- The first vertical slice was marked as recommended, not user-approved.

## 34. Final Reliability Assessment

* Completeness rating 1–5: 4
* Reliability rating 1–5: 4
* Human-readability rating 1–5: 4
* Aggregation-readiness rating 1–5: 4
* Main remaining uncertainty sources: hidden prior project context, exact user acceptance of assistant recommendations, current engine/documentation facts, exact implementation constraints, and cross-chat conflicts.
* Manual review before merging: Yes. This should be manually reviewed before it becomes a binding master spec, especially decisions marked INFERENCE or UNCERTAIN / UNVERIFIED.

