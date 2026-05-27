# Aggregator Packet — Dominium Architecture I

## 1. Packet Metadata

- Chat label: Dominium Architecture I
- Date anchor: 2026-05-27 Australia/Melbourne
- Source scope: this visible chat only
- Coverage: partial
- Confidence: 3 / 5
- Staleness risk: high for external claims
- Merge priority: high
- Main limitations: skipped context; generated specs are drafts; duplicate/conflicting specs; no file inspection.

## 2. Ultra-Condensed Carry-Forward Capsule

This chat, labelled **Dominium Architecture I**, is a retired architecture/specification chat for the **Dominium Game** project. The visible thread is not a normal project-planning chat; it is primarily a long-running specification-generation session meant to prepare Dominium for automated implementation with **Codex 5.1 Max**. The user’s explicit workflow changed during the chat: the initial idea was for Codex to read a full transcript and compile a complete v3 “book of volumes,” but the user later decided that Codex could not reliably read the entire context at once. The workflow therefore shifted to creating a **set of `.txt` implementation-spec prompt files**, one per file in the intended repository tree.

The dominant artifact stream is a large **`devspec/` file tree**. The user provided the full directory/file list, skipped top-level `.txt` files because original Markdown docs already exist in `/docs/...`, and then repeatedly instructed the assistant to proceed in strict order. Visible generated specs cover much of the architecture: engine modules from math/memory/ECS/jobs/save/replay/network/log/config/serialization/locale; platform abstraction backends; render abstraction and backends; audio abstraction and backends; and systems modules through research. The game layer was started and visible generation reached `game/g_world.h.txt`. If continuing the same work, the next strict-order file is **`game/g_world.cpp.txt`**.

Core decisions that must not be lost: Dominium’s simulation core is intended to be deterministic and replay/lockstep safe; UTF-8 is canonical internally; retro ASCII/ANSI/SFN fallbacks are required for old platforms; semantic versioning must be `major.minor.patch`; build numbers/dates must not appear in filenames but must appear in metadata; systems must not depend on platform/render/UI/audio; dynamic allocation is prohibited in deterministic tick/hot paths; and generated file specs must include requirements, prohibitions, dependencies, functions, declarations, and implementation expectations.

This chat also contains important risks. The visible context is only partial because many earlier messages are collapsed. Top-level docs, legal/policy docs, context MDs, cross-dependencies, volume specs, and possibly early engine files are referenced but not fully visible. Several assistant-generated specs contradict one another or use inconsistent APIs. The most important conflicts are duplicate and incompatible specs for `dweather`, `dhydro`, and `dai_core`; inconsistent memory API names; inconsistent serialization API names; C89/C++98 claims that are violated by C99/C++11 constructs; and unverified platform/library support claims. These are not final decisions; they must be carried forward as unresolved issues requiring canonicalisation before implementation.

This report package repairs the prior transfer packet by assigning stable IDs to workstreams, decisions, tasks, constraints, questions, artifacts, risks, rejected options, and verification items. It is safe for aggregation **with caveats**: it should be treated as chat-specific source material, not a final whole-project spec, and all uncertain/skipped/external items must remain labelled until verified.

For aggregation, the most important facts are that this chat established the **per-file devspec workflow** and generated a large visible sequence of implementation-spec prompts. It should feed the master Project Spec Book as source material for architecture, file list, coding rules, automation workflow, and artifact provenance. It must not be merged as final canonical API text until conflicts are resolved. User statements are higher priority than assistant-generated pseudo-code.

The current sequence point matters: **`game/g_world.cpp.txt`** is next if continuing file-spec generation. However, if the aggregator is preparing implementation rather than continuing documentation, it should prioritise canonicalisation of duplicate systems and core API mismatches.

## 3. Top Carry-Forward Items

| Priority | Item | Type | Why it matters | Label | Confidence |
|---|---|---|---|---|---|
| 1 | Resume file generation at game/g_world.cpp.txt if continuing strict sequence. | Next action | Prevents lost sequence state. | FACT | high |
| 2 | Per-file .txt specs are the primary Codex workflow. | Workflow | Codex context limit workaround. | FACT | high |
| 3 | Use UTF-8 internally with retro fallbacks. | Decision | Affects dlocale/data/UI/font/platform paths. | FACT | high |
| 4 | Semantic versioning with metadata build provenance. | Decision | Affects packaging/build files. | FACT | high |
| 5 | Determinism is core. | Constraint | Affects all sim systems. | FACT | high |
| 6 | Skip top_level devspec because /docs originals exist. | Decision | Prevents duplicate top-level work. | FACT | medium |
| 7 | Duplicate dweather/dhydro/dai_core specs must be reconciled. | Open issue | Prevents API conflict. | FACT | high |
| 8 | dmem and dserialize APIs are inconsistent in drafts. | Risk | Core compile/integration issue. | FACT | high |
| 9 | C89/C++98 compliance is intended but violated in drafts. | Risk | Legacy compiler support. | FACT | medium-high |
| 10 | External platform/tool/legal claims require verification. | Verification | Avoid stale false claims. | FACT | high |

## 4. Workstream Summaries

### WORKSTREAM-01 — Final report package for retired chat
- Objective: Produce downloadable, shareable, reusable report files for this individual old chat.
- Current state: Active in this response; package generated from the visible chat and previous transfer packet.
- Desired end state: Markdown/YAML/ZIP package saved and usable for later aggregation.
- Priority: highest
- Decisions: Use chat-specific scope; create report/YAML/aggregator/register/brief/audit/manifest files; create ZIP if tools are available.
- Tasks: TASK-01, TASK-02.
- Constraints: CONSTRAINT-01 through CONSTRAINT-05, CONSTRAINT-19, CONSTRAINT-20.
- Artifacts: This report package files.
- Risks: RISK-01, RISK-09, RISK-10.
- Open questions: see open question register.
- Next action: Download and store the package; use it to bootstrap new chat.

### WORKSTREAM-02 — Dominium Game architecture
- Objective: Carry forward the architecture of the Dominium deterministic simulation/game project.
- Current state: Architecture/specification phase; many implementation-spec prompts generated.
- Desired end state: Complete source tree implemented and validated from specs.
- Priority: highest
- Decisions: Determinism, UTF-8, semantic versioning, per-file specs, strict layers.
- Tasks: TASK-10, TASK-21, TASK-22.
- Constraints: CONSTRAINT-07 through CONSTRAINT-17.
- Artifacts: Spec v3, devspecs, docs.
- Risks: RISK-02 through RISK-07, RISK-11 through RISK-15.
- Open questions: see open question register.
- Next action: Either continue specs or canonicalise before coding.

### WORKSTREAM-03 — Codex per-file devspec automation
- Objective: Create one .txt implementation-spec prompt per repo file for Codex 5.1 Max.
- Current state: Generated through game/g_world.h.txt visibly; many later files remain pending.
- Desired end state: Complete devspec tree covering every listed file.
- Priority: highest
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-04 — Spec v3 volume corpus
- Objective: Earlier volume/subvolume book describing the whole project.
- Current state: Referenced but many contents are collapsed/skipped in visible context.
- Desired end state: Recovered or cross-linked into later master spec book.
- Priority: high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-05 — Top-level docs, context MDs, and legal/policy docs
- Objective: README, context MD files, legal/policy docs, cross-dependencies.
- Current state: Requested/generated earlier but contents mostly not visible; user said originals exist in /docs/.
- Desired end state: Verified docs aligned with current spec.
- Priority: high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-06 — Engine core specs
- Objective: Low-level deterministic engine modules.
- Current state: Many visible specs generated; dcore/dtime not visible in accessible segment.
- Desired end state: Canonical, C89-compliant engine API implemented.
- Priority: high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-07 — Platform abstraction specs
- Objective: Cross-platform platform layer and backends.
- Current state: dplat.h/common/win32/sdl2/x11/macos/headless visible; fs/input/time listed but not visible.
- Desired end state: Complete platform abstraction with file system, input, time, backends.
- Priority: high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-08 — Rendering specs
- Objective: Renderer abstraction, 2D helpers, software/GL/DX9 backends, font rendering.
- Current state: Visible specs generated through dr_font.c.
- Desired end state: Consistent render API and backends.
- Priority: high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-09 — Audio specs
- Objective: Audio abstraction and null/SDL/OpenAL backends.
- Current state: Visible specs generated.
- Desired end state: Deterministic mixer and platform backends, null fallback.
- Priority: medium-high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-10 — Systems layer specs
- Objective: Core deterministic simulation systems.
- Current state: Visible specs generated through dresearch.c; weather/hydro/AI duplicated with conflicts.
- Desired end state: Canonical APIs and implementations for all systems.
- Priority: highest
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-11 — Game layer specs
- Objective: High-level game orchestration and domain registries.
- Current state: g_core.h, g_core.cpp, g_world.h visible; g_world.cpp onward pending.
- Desired end state: Complete game layer specs through g_sim_loop.
- Priority: high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-12 — UI layer specs
- Objective: UI framework, input, map/3D/economy/research/blueprints/launcher UI.
- Current state: Listed but not generated visibly.
- Desired end state: Complete UI implementation-spec prompts.
- Priority: medium-high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-13 — Launcher specs
- Objective: Launcher main/detect/config/CLI.
- Current state: Listed but not generated visibly.
- Desired end state: Complete launcher specs.
- Priority: medium-high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-14 — Mods and base Lua specs
- Objective: C/C++ Lua API, loader, base mod scripts.
- Current state: Listed but not generated visibly.
- Desired end state: Complete mod API/loader/base Lua specs.
- Priority: medium-high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-15 — Tools specs
- Objective: World editor, asset pipeline, modkit, replay viewer, profiler, CLI tools.
- Current state: Listed but not generated visibly.
- Desired end state: Complete tool specs.
- Priority: medium
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-16 — Data schema specs
- Objective: JSON schemas/content expectations for entities/machines/vehicles/materials/research/economy/locales.
- Current state: Listed but not generated visibly.
- Desired end state: Complete data schema specs aligned with systems/game APIs.
- Priority: high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-17 — Test specs
- Objective: Determinism, ECS, math, networks, economy, climate, save/load, replay, mod API tests.
- Current state: Listed but not generated visibly.
- Desired end state: Complete test prompt specs and eventual test implementation.
- Priority: high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-18 — Build and CI script specs
- Objective: Build scripts and CI verification scripts.
- Current state: Listed but not generated visibly.
- Desired end state: Portable build scripts and determinism CI.
- Priority: medium-high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-19 — API canonicalisation and contradiction repair
- Objective: Resolve duplicated/conflicting specs and inconsistent APIs before coding.
- Current state: Identified as necessary by visible contradictions.
- Desired end state: Canonical API/register and corrected spec pack.
- Priority: highest before coding
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

### WORKSTREAM-20 — External compatibility, legal, and tool verification
- Objective: Verify external claims such as Codex, SDL/OpenAL/DX9/OpenGL, old OS support, and legal docs.
- Current state: Not verified in this chat.
- Desired end state: Current verified support/legal matrix.
- Priority: medium-high
- Decisions: See decision register for related decisions.
- Tasks: See task register.
- Constraints: See constraint register.
- Artifacts: See artifact ledger.
- Risks: See risk register.
- Open questions: see open question register.
- Next action: Continue strict order or canonicalise as appropriate.

## 5. Registers for Merge

### Decision Register
| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| DECISION-01 | Use UTF-8 Unicode as canonical internal text encoding. | final design intent | Visible localisation discussion and dlocale specs. | Support modern localisation while allowing retro fallback. | All text/data/mod/config should be UTF-8 internally. | WORKSTREAM-02 | high | FACT |
| DECISION-02 | Provide retro ASCII/ANSI/SFN fallbacks for legacy platforms. | final design intent | dlocale specs include ANSI/SFN helpers. | Retro builds may not support Unicode/long filenames. | Requires filename sanitisation, SFN generation, fallback fonts. | WORKSTREAM-06 | medium-high | FACT |
| DECISION-03 | Use major.minor.patch semantic versioning for all components/packages and the complete game. | final | User explicitly stated this. | Clean package/component version policy. | Build/package metadata design. | WORKSTREAM-02 | high | FACT |
| DECISION-04 | Do not include build numbers/dates in filenames. | final | User explicitly stated this. | Avoid filename clutter. | Build info must be in metadata instead. | WORKSTREAM-02 | high | FACT |
| DECISION-05 | Include build numbers/dates and useful provenance in metadata. | final | User explicitly stated this. | Preserve traceability without filename clutter. | Metadata schema needed. | WORKSTREAM-02 | high | FACT |
| DECISION-06 | Use per-file .txt implementation specs for Codex. | final workflow | User explicitly requested one .txt per git file. | Codex cannot read full chat at once. | Devspec generation is main autocode prep. | WORKSTREAM-03 | high | FACT |
| DECISION-07 | Skip top-level devspec .txt files. | final for current workflow | User said original MD files exist in /docs/. | Avoid duplicating existing docs. | Need verify /docs content later. | WORKSTREAM-05 | medium-high | FACT |
| DECISION-08 | Proceed through file specs in strict directory order. | final workflow | User repeatedly corrected assistant to use same order. | Avoid gaps/confusion. | Resume at game/g_world.cpp.txt if continuing. | WORKSTREAM-03 | high | FACT |
| DECISION-09 | Determinism is a core hard requirement. | final architecture | Repeated throughout specs. | Replay/lockstep/save consistency. | All core systems must be deterministic. | WORKSTREAM-02 | high | FACT |
| DECISION-10 | Systems must not depend on render/UI/audio/platform. | final architecture | Repeated prohibitions. | Layer separation and deterministic core. | Systems APIs must be pure and data-oriented. | WORKSTREAM-10 | high | FACT |
| DECISION-11 | No dynamic allocation in simulation hot paths/ticks. | final architecture | Repeated specs. | Performance and determinism. | Use fixed pools/preallocation. | WORKSTREAM-06 | high | FACT |
| DECISION-12 | Prefer integer/fixed-point for simulation state. | final for most systems | Repeated specs. | Cross-platform determinism. | dmath/fixed math foundation needed. | WORKSTREAM-10 | high | FACT |
| DECISION-13 | Use deterministic lockstep for networking. | final design intent | dnet_core specs. | Multiplayer/replay determinism. | Input aggregation and hash checks. | WORKSTREAM-06 | high | FACT |
| DECISION-14 | Null audio backend must exist and do no-op output. | final design intent | daudio_null spec. | Headless/server/CI fallback. | Audio events can run without hardware. | WORKSTREAM-09 | high | FACT |
| DECISION-15 | Software renderer fallback must exist. | final design intent | dr_soft spec. | Low-end/headless/offline capture/testing. | Render system must abstract hardware. | WORKSTREAM-08 | high | FACT |
| DECISION-16 | Research system is numeric substrate; tech tree lives in game layer. | final design intent | dresearch specs. | Separation of numeric progress from unlock logic. | g_research_tree owns dependencies/effects. | WORKSTREAM-10 | high | FACT |
| DECISION-17 | AI core should be primitives/substrate, not full high-level behaviour. | final v1 intent but duplicated API conflict | dai_core specs. | Keep deterministic AI foundation simple. | High-level AI should live in game layer. | WORKSTREAM-10 | medium | FACT |
| DECISION-18 | Weather/hydrology/climate should be simplified deterministic models, not CFD/GCM. | final v1 intent | dclimate/dweather/dhydro specs. | Low cost, reproducible, property/planet scale. | Use scalar/bucket models. | WORKSTREAM-10 | high | FACT |
| DECISION-19 | C89 for C modules and C++98 for game/UI are intended standards. | intended but inconsistent | Many specs state C89; game specs state C++98. | Legacy portability. | Generated specs need compliance audit. | WORKSTREAM-19 | medium | FACT |
| DECISION-20 | Canonical dweather/dhydro/dai_core versions are not yet selected. | pending | Duplicate conflicting specs visible. | Avoid implementing wrong API. | Canonicalisation required. | WORKSTREAM-19 | high | FACT |
| DECISION-21 | No full book generation via Codex from entire transcript for now. | superseded option | User said Codex cannot read whole context. | Per-file specs replace full-book workflow. | Full spec book may be built later from reports. | WORKSTREAM-04 | high | FACT |
| DECISION-22 | This report package is for this chat only. | final handoff rule | User explicitly scoped output. | Do not summarise whole project. | Aggregation later must preserve provenance. | WORKSTREAM-01 | high | FACT |

### Task Register
| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Recommended next step | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|---|---|
| TASK-01 | Save/download this report package. | highest | immediate | User | none | Download links | Local saved package | Download Markdown/YAML/ZIP. | WORKSTREAM-01 | FACT |
| TASK-02 | Use this package in the next chat. | highest | immediate | User / future assistant | TASK-01 | Package files | Continuity restored. | Paste or upload report/ZIP into new chat. | WORKSTREAM-01 | FACT |
| TASK-03 | If continuing spec generation, generate game/g_world.cpp.txt next. | high | next if continuing | Future assistant | This packet | Current file order | Next per-file spec. | Resume strict order. | WORKSTREAM-11 | FACT |
| TASK-04 | Resolve duplicate dweather specs. | high | before coding | Future assistant/user | none | Both dweather variants | Canonical weather API/spec. | Run canonicalisation pass. | WORKSTREAM-19 | FACT |
| TASK-05 | Resolve duplicate dhydro specs. | high | before coding | Future assistant/user | none | Both dhydro variants | Canonical hydrology API/spec. | Run canonicalisation pass. | WORKSTREAM-19 | FACT |
| TASK-06 | Resolve duplicate dai_core specs. | high | before coding | Future assistant/user | none | Both dai_core variants | Canonical AI API/spec. | Run canonicalisation pass. | WORKSTREAM-19 | FACT |
| TASK-07 | Normalise dmem API. | high | before coding | Future assistant/Codex | none | dmem specs and call sites | Single memory API. | Create correction register. | WORKSTREAM-19 | INFERENCE |
| TASK-08 | Normalise dserialize API. | high | before coding | Future assistant/Codex | none | dserialize specs and call sites | Single serialization API. | Create correction register. | WORKSTREAM-19 | INFERENCE |
| TASK-09 | Audit C89/C++98 compliance. | high | before coding | Future assistant/Codex | none | All specs | Corrected language-standard plan. | List invalid constructs. | WORKSTREAM-19 | INFERENCE |
| TASK-10 | Verify external platform/library/tool claims. | medium-high | before build/release | User/future assistant | none | Current docs | Verified support matrix. | Browse/verify when asked. | WORKSTREAM-20 | FACT |
| TASK-11 | Recover or inspect /docs top-level docs. | high | before aggregation/coding | User/future assistant | none | /docs files | Verified doc inventory. | Ask user to provide or inspect files. | WORKSTREAM-05 | FACT |
| TASK-12 | Finish platform dplat_fs/input/time specs if missing. | medium-high | before platform implementation | Future assistant | WORKSTREAM-07 | File list | Missing platform specs. | Generate or recover. | WORKSTREAM-07 | INFERENCE |
| TASK-13 | Finish game specs. | high | after g_world.cpp | Future assistant | TASK-03 | Game file list | All game file specs. | Continue strict order. | WORKSTREAM-11 | FACT |
| TASK-14 | Finish UI specs. | medium-high | after game or when requested | Future assistant | WORKSTREAM-12 | UI file list | UI devspecs. | Continue strict order. | WORKSTREAM-12 | FACT |
| TASK-15 | Finish launcher specs. | medium-high | after UI | Future assistant | none | Launcher file list | Launcher devspecs. | Continue strict order. | WORKSTREAM-13 | FACT |
| TASK-16 | Finish mods/base Lua specs. | medium-high | after launcher | Future assistant | none | Mods file list | Mod devspecs. | Continue strict order. | WORKSTREAM-14 | FACT |
| TASK-17 | Finish tools specs. | medium | later | Future assistant | none | Tools file list | Tool devspecs. | Continue strict order. | WORKSTREAM-15 | FACT |
| TASK-18 | Finish data schema specs. | high | before content coding | Future assistant | none | Data file list | JSON schema/content specs. | Continue strict order. | WORKSTREAM-16 | FACT |
| TASK-19 | Finish tests specs. | high | before validation | Future assistant | none | Test file list | Test devspecs. | Continue strict order. | WORKSTREAM-17 | FACT |
| TASK-20 | Finish build/CI script specs. | medium-high | before repo build | Future assistant | none | Script file list | Build/CI specs. | Continue strict order. | WORKSTREAM-18 | FACT |
| TASK-21 | Convert devspec content into actual repo files. | high | after specs/canonicalisation | User/Codex | Specs complete enough | Generated text | devspec tree on disk. | Create files in repo. | WORKSTREAM-03 | INFERENCE |
| TASK-22 | Start Codex implementation. | high | after prompts/canonical APIs | User/Codex | TASK-21, TASK-04, TASK-05, TASK-06, TASK-07, TASK-08 | Repo/devspec | Source implementation. | Feed per-file specs to Codex. | WORKSTREAM-03 | FACT |

### Constraint Register
| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
|---|---|---|---|---|---|---|---|---|
| CONSTRAINT-01 | Scope this package to this visible chat only. | handoff | hard | User | Do not summarise whole Project. | high | high | FACT |
| CONSTRAINT-02 | Label important items as FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT. | handoff | hard | User | Preserve provenance. | high | high | FACT |
| CONSTRAINT-03 | Do not invent facts or silently infer. | handoff | hard | User | Mark gaps explicitly. | high | high | FACT |
| CONSTRAINT-04 | Direct user statements outrank assistant suggestions. | source hierarchy | hard | User | Do not treat assistant drafts as final decisions unless user accepted them. | high | high | FACT |
| CONSTRAINT-05 | External-world/tool/legal/platform facts require verification before use. | verification | hard | User | Avoid stale claims. | medium-high | high | FACT |
| CONSTRAINT-06 | Strict file generation order. | workflow | hard | User | Resume at correct next file. | medium | high | FACT |
| CONSTRAINT-07 | Use deterministic simulation. | technical | hard | Specs/user | Same inputs produce same outputs. | very high | high | FACT |
| CONSTRAINT-08 | No hidden randomness/time/OS dependence in sim. | technical | hard | Specs | Replay/lockstep consistency. | very high | high | FACT |
| CONSTRAINT-09 | No dynamic allocation in sim tick/hot paths. | technical/resource | hard | Specs | Use fixed pools. | high | high | FACT |
| CONSTRAINT-10 | No systems dependency on render/UI/audio/platform. | architecture | hard | Specs | Layer purity. | high | high | FACT |
| CONSTRAINT-11 | C89 for C modules. | language | hard but currently violated in drafts | Specs | Audit generated specs. | high | medium | FACT |
| CONSTRAINT-12 | C++98 for game/UI C++ modules. | language | hard but currently violated in drafts | Specs | Avoid modern C++ syntax. | medium-high | medium | FACT |
| CONSTRAINT-13 | UTF-8 canonical internal text. | technical/design | hard | User/specs | Data/mod/UI text UTF-8. | medium | high | FACT |
| CONSTRAINT-14 | Retro ANSI/SFN fallback support. | technical/platform | hard for retro builds | User/specs | dlocale/platform file path helpers. | medium | medium | FACT |
| CONSTRAINT-15 | Major.minor.patch semantic versioning. | packaging | hard preference | User | Version policy. | low | high | FACT |
| CONSTRAINT-16 | No build date/number in filenames. | packaging | hard preference | User | Put provenance in metadata. | low | high | FACT |
| CONSTRAINT-17 | Build date/number in metadata. | packaging | hard preference | User | Metadata schema required. | medium | high | FACT |
| CONSTRAINT-18 | Use per-file `.txt` prompts to support Codex context limits. | workflow | hard | User | Keep specs modular. | high | high | FACT |
| CONSTRAINT-19 | Preserve rejected/deprioritised options. | handoff | hard | User | Avoid repeated work. | medium | high | FACT |
| CONSTRAINT-20 | Do not reveal hidden chain-of-thought. | handoff/reasoning | hard | User/system | Only visible rationale. | high | high | FACT |

### Open Questions Register
| ID | Question / issue | Why it matters | Known information | Unknown information | What would resolve it | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|---|---|
| QUESTION-01 | Which dweather spec is canonical? | Duplicate APIs create implementation conflict. | Two dweather variants visible. | User preference/final choice. | Canonicalisation pass/user confirmation. | high | WORKSTREAM-19, WORKSTREAM-10 | FACT |
| QUESTION-02 | Which dhydro spec is canonical? | Duplicate APIs create implementation conflict. | Two dhydro variants visible. | User preference/final choice. | Canonicalisation pass/user confirmation. | high | WORKSTREAM-19, WORKSTREAM-10 | FACT |
| QUESTION-03 | Which dai_core spec is canonical? | Duplicate AI APIs conflict. | Two dai_core variants visible. | User preference/final choice. | Canonicalisation pass/user confirmation. | high | WORKSTREAM-19, WORKSTREAM-10 | FACT |
| QUESTION-04 | Were dcore.h/c and dtime.h/c generated in skipped turns? | Foundational engine specs missing from visible context. | They are listed. | Actual contents. | Recover transcript/files or regenerate. | high | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | Were dplat_fs.c, dplat_input.c, dplat_time.c generated elsewhere? | Platform folder completeness. | Listed, not visible. | Whether specs exist. | Recover transcript/files or regenerate. | medium-high | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Are `/docs/...` originals complete and current? | Top-level specs skipped because of them. | User says they exist. | Content/currentness. | Inspect files. | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | What is the canonical dmem API? | Many specs call different memory functions. | Inconsistency visible. | Final function names/signatures. | API normalisation. | high | WORKSTREAM-19 | FACT |
| QUESTION-08 | What is the canonical dserialize API? | Save/replay/codegen depends on it. | Multiple naming patterns visible. | Final stream/buffer model. | API normalisation. | high | WORKSTREAM-19 | FACT |
| QUESTION-09 | How strict are the retro target requirements? | Old OS support may be costly/unrealistic. | Specs mention DOS/Win3.x/Win9x/Win2000. | Actual tiers/toolchains. | User confirmation + external verification. | medium-high | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| QUESTION-10 | Is internal double allowed in dclimate? | dclimate specs conflict. | Header and source spec differ. | Final determinism model. | Canonicalisation. | medium-high | WORKSTREAM-10 | FACT |
| QUESTION-11 | What does Codex 5.1 Max currently support? | Automation workflow depends on it. | User intends to use it. | Current tool availability/context limits. | Verify current docs. | medium | WORKSTREAM-03, WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| QUESTION-12 | Are legal docs valid? | Distribution risk. | Docs requested/generated. | Legal sufficiency. | Legal review. | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |

### Artifact Ledger
| ID | Artifact / file / prompt / output | Type | Purpose | Status | Where it came from | Carry forward? | Notes | Label |
|---|---|---|---|---|---|---|---|---|
| ARTIFACT-001 | Spec v3 volumes/subvolumes | Specification corpus | Whole-project architecture | Referenced; contents partly skipped | Visible user/assistant context | yes |  | FACT |
| ARTIFACT-002 | BUILDING.MD | Context MD | Building/spec details | Requested/generated earlier; content skipped | Visible user request | yes |  | FACT |
| ARTIFACT-003 | DATA_FORMATS.MD | Context MD | Data format policy | Requested/generated earlier; content skipped | Visible user request | yes |  | FACT |
| ARTIFACT-004 | LANGUAGE_POLICY.MD | Context MD | Language/localisation policy | Requested/generated earlier; content skipped | Visible user request | yes |  | FACT |
| ARTIFACT-005 | MILESTONES.MD | Context MD | Development milestones | Requested/generated earlier; content skipped | Visible user request | yes |  | FACT |
| ARTIFACT-006 | STYLE.MD | Context MD | Style/code conventions | Requested/generated earlier; content skipped | Visible user request | yes |  | FACT |
| ARTIFACT-007 | SPEC_CORE.MD | Context MD | Core spec summary | Requested/generated earlier; content skipped | Visible user request | yes |  | FACT |
| ARTIFACT-008 | README.md | GitHub doc | Repo introduction | Requested/generated earlier; content skipped | Visible user request | yes |  | FACT |
| ARTIFACT-009 | LICENSE/LICENCE_MASTER.md | Legal doc | Licensing | Requested/generated earlier; content skipped | Visible user request | yes | Needs legal review | FACT |
| ARTIFACT-010 | EULA.md | Legal doc | End-user license | Requested/generated earlier; content skipped | Visible user request | yes | Needs legal review | FACT |
| ARTIFACT-011 | TOS.md | Legal doc | Terms of service | Requested/generated earlier; content skipped | Visible user request | yes | Needs legal review | FACT |
| ARTIFACT-012 | WARRANTY.md | Legal doc | Warranty/disclaimer | Requested/generated earlier; content skipped | Visible file list | yes | Needs legal review | FACT |
| ARTIFACT-013 | PRIVACY_POLICY.md | Legal doc | Privacy | Requested/generated earlier; content skipped | Visible file list | yes | Needs legal/privacy review | FACT |
| ARTIFACT-014 | SAFETY_GUIDELINES.md | Policy doc | Safety | Requested/generated earlier; content skipped | Visible file list | yes |  | FACT |
| ARTIFACT-015 | MULTIPLAYER_POLICY.md | Policy doc | Multiplayer/server behaviour | Requested/generated earlier; content skipped | Visible file list | yes |  | FACT |
| ARTIFACT-016 | SERVER_OPERATORS_GUIDE.md | Policy/guide | Server operation | Requested/generated earlier; content skipped | Visible file list | yes |  | FACT |
| ARTIFACT-017 | CROSS_DEPENDENCIES.md | Dev doc | Developer detail of cross dependencies | Requested/generated earlier; content skipped | Visible user request | yes |  | FACT |
| ARTIFACT-018 | /docs/... originals | Repo docs path | Existing top-level docs | Referenced but not inspected | User statement | yes | Verify contents | UNCERTAIN / UNVERIFIED |
| ARTIFACT-019 | engine/dmath.h.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-020 | engine/dmath.c.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-021 | engine/dmem.h.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-022 | engine/dmem.c.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-023 | engine/decs.h.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-024 | engine/decs.c.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-025 | engine/djob.h.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-026 | engine/djob.c.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-027 | engine/dsave.h.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-028 | engine/dsave.c.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-029 | engine/dreplay.h.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-030 | engine/dreplay.c.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-031 | engine/dnet_core.h.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-032 | engine/dnet_core.c.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-033 | engine/dlog.h.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-034 | engine/dlog.c.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-035 | engine/dcfg.h.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-036 | engine/dcfg.c.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-037 | engine/dserialize.h.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-038 | engine/dserialize.c.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-039 | engine/dlocale.h.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-040 | engine/dlocale.c.txt | implementation-spec prompt | Codex source-file guidance | generated visibly | visible assistant output | yes | Carry forward with API/C89 audit. | FACT |
| ARTIFACT-041 | engine/dcore.h.txt | implementation-spec prompt | Engine source-file guidance | listed but not visible in accessible context | user file list | yes | Recover or regenerate. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-042 | engine/dcore.c.txt | implementation-spec prompt | Engine source-file guidance | listed but not visible in accessible context | user file list | yes | Recover or regenerate. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-043 | engine/dtime.h.txt | implementation-spec prompt | Engine source-file guidance | listed but not visible in accessible context | user file list | yes | Recover or regenerate. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-044 | engine/dtime.c.txt | implementation-spec prompt | Engine source-file guidance | listed but not visible in accessible context | user file list | yes | Recover or regenerate. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-045 | platform/dplat.h.txt | implementation-spec prompt | Platform source-file guidance | generated visibly | visible assistant output | yes |  | FACT |
| ARTIFACT-046 | platform/dplat_common.c.txt | implementation-spec prompt | Platform source-file guidance | generated visibly | visible assistant output | yes |  | FACT |
| ARTIFACT-047 | platform/dplat_win32.c.txt | implementation-spec prompt | Platform source-file guidance | generated visibly | visible assistant output | yes |  | FACT |
| ARTIFACT-048 | platform/dplat_sdl2.c.txt | implementation-spec prompt | Platform source-file guidance | generated visibly | visible assistant output | yes |  | FACT |
| ARTIFACT-049 | platform/dplat_x11.c.txt | implementation-spec prompt | Platform source-file guidance | generated visibly | visible assistant output | yes |  | FACT |
| ARTIFACT-050 | platform/dplat_macos.c.txt | implementation-spec prompt | Platform source-file guidance | generated visibly | visible assistant output | yes |  | FACT |
| ARTIFACT-051 | platform/dplat_headless.c.txt | implementation-spec prompt | Platform source-file guidance | generated visibly | visible assistant output | yes |  | FACT |
| ARTIFACT-052 | platform/dplat_fs.c.txt | implementation-spec prompt | Platform source-file guidance | listed but not visible in accessible context | user file list | yes | Recover or generate. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-053 | platform/dplat_input.c.txt | implementation-spec prompt | Platform source-file guidance | listed but not visible in accessible context | user file list | yes | Recover or generate. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-054 | platform/dplat_time.c.txt | implementation-spec prompt | Platform source-file guidance | listed but not visible in accessible context | user file list | yes | Recover or generate. | UNCERTAIN / UNVERIFIED |
| ARTIFACT-055 | render/drender.h.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-056 | render/drender.c.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-057 | render/dr_vec2d.h.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-058 | render/dr_vec2d.c.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-059 | render/dr_tex2d.h.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-060 | render/dr_tex2d.c.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-061 | render/dr_soft.h.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-062 | render/dr_soft.c.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-063 | render/dr_gl1.h.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-064 | render/dr_gl1.c.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-065 | render/dr_gl2.h.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-066 | render/dr_gl2.c.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-067 | render/dr_dx9.h.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-068 | render/dr_dx9.c.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-069 | render/dr_font.h.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-070 | render/dr_font.c.txt | implementation-spec prompt | Render source-file guidance | generated visibly | visible assistant output | yes | Audit type/API mismatches. | FACT |
| ARTIFACT-071 | audio/daudio.h.txt | implementation-spec prompt | Audio source-file guidance | generated visibly | visible assistant output | yes |  | FACT |
| ARTIFACT-072 | audio/daudio.c.txt | implementation-spec prompt | Audio source-file guidance | generated visibly | visible assistant output | yes |  | FACT |
| ARTIFACT-073 | audio/daudio_null.c.txt | implementation-spec prompt | Audio source-file guidance | generated visibly | visible assistant output | yes |  | FACT |
| ARTIFACT-074 | audio/daudio_sdl.c.txt | implementation-spec prompt | Audio source-file guidance | generated visibly | visible assistant output | yes |  | FACT |
| ARTIFACT-075 | audio/daudio_openal.c.txt | implementation-spec prompt | Audio source-file guidance | generated visibly | visible assistant output | yes |  | FACT |
| ARTIFACT-076 | systems/dterrain.h.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-077 | systems/dterrain.c.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-078 | systems/dchunks.h.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-079 | systems/dchunks.c.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-080 | systems/dnet_power.h.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-081 | systems/dnet_power.c.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-082 | systems/dnet_fluid.h.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-083 | systems/dnet_fluid.c.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-084 | systems/dnet_data.h.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-085 | systems/dnet_data.c.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-086 | systems/dinventory.h.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-087 | systems/dinventory.c.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-088 | systems/dlogistics.h.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-089 | systems/dlogistics.c.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-090 | systems/deconomy.h.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-091 | systems/deconomy.c.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-092 | systems/dclimate.h.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-093 | systems/dclimate.c.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly; conflicts with C89/fixed-point constraints; repair before coding. | FACT |
| ARTIFACT-094 | systems/dweather.h.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly but duplicated/conflicting in this chat; canonicalise before coding. | FACT |
| ARTIFACT-095 | systems/dweather.c.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly but duplicated/conflicting in this chat; canonicalise before coding. | FACT |
| ARTIFACT-096 | systems/dhydro.h.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly but duplicated/conflicting in this chat; canonicalise before coding. | FACT |
| ARTIFACT-097 | systems/dhydro.c.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly but duplicated/conflicting in this chat; canonicalise before coding. | FACT |
| ARTIFACT-098 | systems/dai_core.h.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly but duplicated/conflicting in this chat; canonicalise before coding. | FACT |
| ARTIFACT-099 | systems/dai_core.c.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly but duplicated/conflicting in this chat; canonicalise before coding. | FACT |
| ARTIFACT-100 | systems/dresearch.h.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-101 | systems/dresearch.c.txt | implementation-spec prompt | Systems source-file guidance | generated visibly | visible assistant output | yes | Generated visibly. | FACT |
| ARTIFACT-102 | game/g_core.h.txt | implementation-spec prompt | Game source-file guidance | generated visibly | visible assistant output | yes | Current sequence interrupted after g_world.h. | FACT |
| ARTIFACT-103 | game/g_core.cpp.txt | implementation-spec prompt | Game source-file guidance | generated visibly | visible assistant output | yes | Current sequence interrupted after g_world.h. | FACT |
| ARTIFACT-104 | game/g_world.h.txt | implementation-spec prompt | Game source-file guidance | generated visibly | visible assistant output | yes | Current sequence interrupted after g_world.h. | FACT |
| ARTIFACT-105 | game/g_world.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-106 | game/g_property.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-107 | game/g_property.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-108 | game/g_company.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-109 | game/g_company.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-110 | game/g_workers.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-111 | game/g_workers.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-112 | game/g_building.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-113 | game/g_building.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-114 | game/g_machines.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-115 | game/g_machines.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-116 | game/g_vehicles.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-117 | game/g_vehicles.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-118 | game/g_research_tree.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-119 | game/g_research_tree.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-120 | game/g_blueprints.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-121 | game/g_blueprints.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-122 | game/g_economy_game.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-123 | game/g_economy_game.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-124 | game/g_sim_loop.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-125 | game/g_sim_loop.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-126 | ui/ui_core.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-127 | ui/ui_core.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-128 | ui/ui_inputs.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-129 | ui/ui_inputs.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-130 | ui/ui_mapview.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-131 | ui/ui_mapview.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-132 | ui/ui_3dview.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-133 | ui/ui_3dview.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-134 | ui/ui_overlays.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-135 | ui/ui_overlays.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-136 | ui/ui_economy.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-137 | ui/ui_economy.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-138 | ui/ui_research.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-139 | ui/ui_research.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-140 | ui/ui_blueprints.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-141 | ui/ui_blueprints.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-142 | ui/ui_launcher.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-143 | ui/ui_launcher.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-144 | launcher/launcher_main.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-145 | launcher/launcher_detect.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-146 | launcher/launcher_config.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-147 | launcher/launcher_cli.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-148 | mods/mod_api.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-149 | mods/mod_api.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-150 | mods/mod_loader.h.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-151 | mods/mod_loader.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-152 | mods/base/base_init.lua.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-153 | mods/base/base_entities.lua.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-154 | mods/base/base_recipes.lua.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-155 | mods/base/base_research.lua.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-156 | mods/base/base_ui.lua.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-157 | tools/t_worldedit.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-158 | tools/t_asset_pipeline.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-159 | tools/t_modkit.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-160 | tools/t_replay_viewer.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-161 | tools/t_profiler.cpp.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-162 | tools/t_cli_tools.c.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-163 | data/data_entities.json.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-164 | data/data_machines.json.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-165 | data/data_vehicles.json.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-166 | data/data_materials.json.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-167 | data/data_research.json.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-168 | data/data_economy.json.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-169 | data/data_locale_en.json.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-170 | data/data_locale_xx.json.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-171 | tests/test_determinism.c.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-172 | tests/test_ecs.c.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-173 | tests/test_math.c.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-174 | tests/test_networks.c.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-175 | tests/test_economy.c.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-176 | tests/test_climate.c.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-177 | tests/test_save_load.c.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-178 | tests/test_replay.c.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-179 | tests/test_mod_api.c.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-180 | scripts/build_all.sh.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-181 | scripts/build_win.bat.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-182 | scripts/build_linux.sh.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-183 | scripts/build_macos.sh.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-184 | scripts/ci_verify_determinism.sh.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |
| ARTIFACT-185 | scripts/ci_run_tests.sh.txt | implementation-spec prompt | Source/data/script guidance | listed but not generated visibly | user file list | yes | Pending in strict order. | FACT |

### Risk Register
| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | Partial visible transcript omits earlier decisions/artifacts. | Missing or wrong aggregation. | high | high | Mark gaps; recover transcript/files. | WORKSTREAM-01 | FACT |
| RISK-02 | Duplicate specs implemented without reconciliation. | API conflicts and compile failures. | high | high | Canonicalisation before coding. | WORKSTREAM-19 | FACT |
| RISK-03 | Generated specs treated as compile-ready code. | Codex produces invalid code. | medium-high | high | Treat as requirements drafts; audit. | WORKSTREAM-03 | FACT |
| RISK-04 | C89/C++98 violations persist. | Legacy compilation fails. | high | high | Language compliance audit. | WORKSTREAM-19 | FACT |
| RISK-05 | dmem/dserialize API mismatch. | Widespread integration failure. | high | high | Normalise core APIs. | WORKSTREAM-19 | FACT |
| RISK-06 | External platform/library claims stale or wrong. | Bad support matrix/build failures. | medium | medium-high | Verify current docs/toolchains. | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| RISK-07 | Legal/policy docs over-trusted. | Legal/compliance risk. | medium | high | Professional review. | WORKSTREAM-05 | INFERENCE |
| RISK-08 | Future assistant restarts or skips file order. | Lost continuity and duplicate work. | medium | medium | Use continuation point. | WORKSTREAM-03 | FACT |
| RISK-09 | Assistant suggestions mistaken as user decisions. | Spec polluted with unaccepted choices. | medium | high | Prioritise user statements. | WORKSTREAM-01 | FACT |
| RISK-10 | Over-compression loses artifact list. | Aggregator cannot reconstruct work. | medium | high | Preserve artifact ledger. | WORKSTREAM-01 | FACT |
| RISK-11 | Retro support over-scoped. | Development burden and false claims. | medium | medium-high | Define support tiers. | WORKSTREAM-20 | INFERENCE |
| RISK-12 | Save/replay serialization inconsistencies. | Broken saves/desyncs. | medium | high | Serialization schema/tests. | WORKSTREAM-06 | FACT |
| RISK-13 | Floating point creeps into deterministic systems. | Cross-platform divergence. | medium | high | Fixed-point audit. | WORKSTREAM-10 | FACT |
| RISK-14 | Codex context/tool assumptions stale. | Automation plan fails. | medium | medium | Verify Codex capabilities. | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| RISK-15 | Unfinished game/UI/data/test specs delay coding. | Implementation incomplete. | high | medium-high | Finish file sequence. | WORKSTREAM-11, WORKSTREAM-12 | FACT |

### Verification Queue
| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Codex 5.1 Max availability/capabilities | Tool naming/features may be stale. | Current OpenAI/Codex docs | high | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | SDL2 support on old Windows/Win9x status | Platform claim external. | SDL docs/build matrix | medium | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | OpenAL support/headers/build viability | External dependency. | OpenAL docs/toolchain | medium | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Direct3D 9 on Windows 2000/XP target details | External OS/API/toolchain claim. | Microsoft/SDK docs | medium | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | OpenGL 1.x/2.x support across target OSes | Driver/API support varies. | Platform graphics docs | medium | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-06 | macOS 10.6 Cocoa/OpenGL shim feasibility | External toolchain/platform claim. | Apple SDK/toolchain docs | medium | WORKSTREAM-07 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | DOS/Win3.x/Win9x compiler and runtime feasibility | Retro support may be unrealistic. | Toolchain docs/user decision | high | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Legal docs validity | Legal enforceability depends on jurisdiction/product. | Legal review | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Privacy/multiplayer/server policies | Regulations can change. | Legal/privacy review | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | C89 availability of stdint.h/int32_t | C89 compilers may lack stdint.h. | Compiler/toolchain docs | high | WORKSTREAM-19 | FACT |
| VERIFY-11 | Existing /docs content | Top-level specs skipped based on it. | Repo inspection | high | WORKSTREAM-05 | FACT |
| VERIFY-12 | Skipped chat contents | May contain missing specs/decisions. | Full transcript export | high | WORKSTREAM-01 | FACT |
| VERIFY-13 | Semantic version metadata conventions for target packages | Package ecosystems may have constraints. | Package manager docs | low | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-14 | Actual current OpenAI model/tool naming | Old assistant labels may be stale. | Official docs | low | WORKSTREAM-20 | UNCERTAIN / UNVERIFIED |

## 6. Possible Cross-Chat Duplicates

- Spec v3 volumes and subvolumes.
- README/context MD/legal docs/cross-dependencies.
- Milestones/development plan.
- Systems/game architecture decisions.
- File list and devspec workflow may appear in other chats.

## 7. Possible Cross-Chat Conflicts

- Other chats may have newer canonical APIs for dweather, dhydro, dai_core.
- Other chats may have corrected dmem/dserialize names.
- Other chats may supersede retro platform support.
- Other chats may contain actual top-level docs that override skipped descriptions here.

## 8. Spec Book Integration Guidance

This chat should feed chapters on project architecture, deterministic design, Codex automation, file-by-file devspec workflow, engine/platform/render/audio/systems/game module map, and artifact provenance. Formal requirements should include deterministic sim, UTF-8, versioning policy, strict layering, and no tick allocation. Assistant-generated pseudo-code should remain background until audited. Duplicates/conflicts should not be merged prematurely.

## 9. Aggregator Warnings

- Do not treat this as the entire Project.
- Do not treat generated specs as compile-ready.
- Preserve uncertainty around skipped context.
- Preserve conflicts rather than collapsing them.
- Verify external claims.
