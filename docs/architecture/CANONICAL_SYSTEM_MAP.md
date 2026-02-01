Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Canonical System Map (CANON0)





Status: binding.


Scope: single-source dependency map and forbidden edges for Dominium/Domino.





This map locks the project into one mental model. It is written for humans and


is the authoritative dependency direction statement. "A -> B" means A depends


on B and must not be inverted.





## Canonical system stack (textual diagram)


This stack is a navigation and integration view. Dependency direction remains


authoritative in the sections below.





ENGINE -> GAME -> SERVER/CLIENT -> LAUNCHER/SETUP -> TOOLS





## Invariants


- Dependency direction is authoritative and must not be inverted.


- Engine and game responsibilities remain separated.


- Law gates and audit are mandatory for authoritative effects.


- Engine and game are content-agnostic executables; content lives in data.


- Launcher and setup are orchestration surfaces only.


- Tools are read-only by default and mutate state only via ToolIntents.





## Responsibilities and forbidden dependencies (quick map)


Responsibilities:


- engine: mechanisms, determinism, storage, execution substrate, law gates


- game: meaning, rules, process emission, law targets, content interpretation


- server/client: product shells that compose engine + game


- launcher/setup: orchestration, installation, profiles, compatibility


- tools: validation, inspection, authoring, and audit-friendly workflows





Forbidden dependencies (summary):


- engine -> game, launcher, setup, tools, libs contracts


- game -> launcher, setup, tools, libs contracts


- launcher/setup/tools -> game rule mutation paths


- client/server -> launcher, setup, tools


- tools -> authoritative mutation outside ToolIntents





## 1) Engine vs Game Boundary


Engine defines mechanisms; game defines meaning; data defines configuration.


Tools are read-only observers unless they emit explicit ToolIntents that are


law-gated and audited.





Dependency direction:


ENGINE: platform + syscaps -> execution substrate -> ECS storage -> world services


(domains, travel, time, law gates)


GAME: rules -> intents -> Work IR -> engine execution substrate


PRODUCTS: client/server -> engine + game


CONTROL PLANE: launcher/setup -> libs/contracts


TOOLS: tools -> libs/contracts (+ engine public API only, read-only)


SCHEMA: schema -> data formats only (no runtime logic)





Forbidden dependencies:


- engine -> game/launcher/setup/tools/libs


- game -> launcher/setup/tools/libs


- launcher/setup/tools -> game (no rule mutation)


- client/server -> tools/launcher/setup


- tools -> authoritative mutation outside ToolIntents





## 2) Execution Substrate


All authoritative work is expressed as Work IR with Access IR declarations.


Law admission gates sit before scheduling, before execution, and before commit.





Dependency direction:


game systems -> Work IR + Access IR -> scheduler backends -> deterministic commit


law kernel -> admission gates -> task/effect execution


budgets + SysCaps -> execution policy -> backend selection





Forbidden dependencies:


- gameplay code bypassing Work IR or spawning threads


- derived/presentation tasks writing authoritative state


- scheduler policy encoded inside game rules





## 3) Storage (ECS)


ECS schemas define component meaning; storage layout is an engine backend choice.


Game code depends on logical components, not layout or memory order.





Dependency direction:


schema/ecs -> engine storage -> game rules -> Work IR tasks





Forbidden dependencies:


- gameplay logic depending on physical storage layout


- storage backends altering component semantics or determinism





## 4) Space & Domains
Domain volumes define where reality exists and which laws apply. Domain queries
are deterministic, budgeted, and SDF-based.

Dependency direction:
domain volumes -> reachability + law jurisdictions -> travel + refinement

Forbidden dependencies:
- implicit world bounds or rectangular assumptions
- domain checks bypassing domain query API

Terrain truth (TERRAIN0) is field-defined and provider-resolved.

Dependency direction:
domain volumes -> terrain field stack -> provider chain -> overlays -> queries

Forbidden dependencies:
- meshes treated as authoritative truth
- per-tick global erosion
- planet/station special casing in terrain truth



## 5) Existence & Refinement


Existence states are explicit; transitions are effects. Refinement contracts


deterministically realize micro state; collapse preserves truth and provenance.





Dependency direction:


existence state -> refinement contract -> visitability -> travel arrival


law kernel + Work IR -> existence transitions





Forbidden dependencies:


- implicit existence creation/destruction


- refinement without a contract


- history edits without archival fork





## 6) Travel & Reachability


All movement is scheduled travel over explicit edges with cost/capacity rules.


Visitability gates arrival.





Dependency direction:


travel graph -> ACT scheduling -> law/capability checks -> arrival effects


domain permissions + existence/refinement -> visitability decision





Forbidden dependencies:


- teleportation without a TravelEdge


- arrival into non-refinable or archived targets


- bypassing law or visitability gates





## 7) Time & Perception


ACT is authoritative and monotonic. Observer clocks derive perception without


changing schedules. Replay uses the same model.





Dependency direction:


ACT -> scheduler -> authoritative effects


observer clocks -> presentation/replay views





Forbidden dependencies:


- ACT warping for gameplay pacing


- perception clocks affecting authoritative scheduling


- future leakage beyond allowed buffers





## 8) Authority, Law & Integrity


Capabilities grant power; laws decide outcomes; policy constrains behavior.


Integrity signals inform law but never mutate state.





Dependency direction:


capabilities + law targets + policy -> law kernel -> accept/refuse/transform


law outcomes -> effects + audit + refusal explanations





Forbidden dependencies:


- isAdmin/mode checks in code


- admin/cheat bypass without law + audit


- silent fallbacks in the face of denial





## 9) Distribution & Sharding


Shard ownership is deterministic and domain-driven. Cross-shard messages are


ordered deterministically; no synchronous cross-shard reads.





Dependency direction:


domain partition -> shard ownership -> message ordering -> commit





Forbidden dependencies:


- nondeterministic shard placement


- state teleportation or silent migration


- synchronous cross-shard reads





## 10) Tooling & Omnipotence


Tooling is capability-gated. Omnipotence is the union of capabilities and is


still law-gated, audited, and constrained by archival rules.





Dependency direction:


ToolIntents -> law kernel -> effects -> audit


omnipotent intent -> same path





Forbidden dependencies:


- tool-side mutation outside ToolIntents


- history edits without archival fork + audit


- bypassing law or integrity gates





## Forbidden assumptions


- Dependency inversion is acceptable for convenience.


- Tooling can mutate authoritative state directly.





## Dependencies


- `docs/architecture/ARCH0_CONSTITUTION.md`


- `docs/architecture/INVARIANTS.md`





## See also


- `docs/architecture/ARCH0_CONSTITUTION.md`


- `docs/architecture/EXECUTION_MODEL.md`


- `docs/architecture/REALITY_MODEL.md`


- `docs/architecture/REALITY_LAYER.md`


- `docs/architecture/REALITY_FLOW.md`


- `docs/architecture/AUTHORITY_MODEL.md`


- `schema/execution/README.md`


- `schema/existence/README.md`


- `schema/domain/README.md`


- `schema/travel/README.md`


- `schema/time/README.md`


- `schema/authority/README.md`


- `schema/distribution/README.md`
