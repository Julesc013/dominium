# Accompanying Detailed Human Summary and Conversation Report

**Chat label:** Domino Framework and Open-Source Provider Architecture  
**Prepared:** 2026-05-27 21:01 AEST  
**Purpose:** Human-readable companion report for the full handoff package.  
**Scope:** This report summarizes the visible conversation and the files generated from it. It does not claim to contain full transcripts of inaccessible past-chat links.

---

## 1. Executive Summary

This conversation developed a practical strategy for building **Dominium** and **Domino** using existing open-source code without surrendering the project’s architecture to any one library or engine.

The core conclusion was:

```text
Domino should be a service-first framework.
Domino engine implementations should provide services through replaceable providers.
Dominium should be a game implementation that consumes the framework.
Third-party code should be provider implementation detail, not project law.
```

The user began by asking whether the project could accelerate development by using existing open-source systems rather than starting from nothing. The answer evolved through several stages. First, the conversation compared the **framework approach** against the **fork/modification approach**. It strongly favored the framework approach: assemble the system from modular libraries, providers, and references instead of forking a full engine and letting that engine define Dominium’s data model, editor model, save format, networking, or simulation law.

The strongest first-wave provider suite identified was:

```text
raylib + rlgl + rlsw + raygui + raudio + SDL2 + pinned Lua
```

The conversation repeatedly stressed that this does **not** mean Dominium becomes a raylib game. raylib and its subprojects are tools and providers. Dominium and Domino own the contracts.

The final conceptual split was:

```text
Domino Framework
  Stable contracts, service APIs, provider ABI, capability/refusal law,
  profiles, conformance tests, deterministic boundaries, diagnostics.

Domino Engine Implementation
  One implementation of the framework, composed from providers.

Dominium Game Implementation
  The actual game rules, content, worldgen, simulation, UI documents,
  commands, packs, agents, machines, and Workbench semantics.

Providers
  raylib, SDL2, Lua, rlgl, rlsw, raygui, raudio, software, null,
  later direct OpenGL 3.3, Direct3D 11, Metal, Vulkan, native platform APIs.
```

This architecture lets the project move fast now while keeping the long-term ability to replace raylib, SDL2, Lua, or any other provider.

---

## 2. What Was Discussed

### 2.1 Open-source acceleration

The conversation started with a high-level question: could the project use existing open-source systems instead of building everything from scratch? The answer was yes, but only under strong boundaries.

The reasoning was:

* Open-source code can accelerate platform, rendering, audio, UI, scripting, asset import, and tooling.
* It should not define Dominium’s simulation, save format, replay format, command system, module format, asset identity, Workbench document model, or provider law.
* Large engine forks are risky because they tend to bring their own object model, build system, editor workflow, rendering assumptions, and content format.
* Small modular providers are easier to replace and test.

The conversation settled on a doctrine:

```text
Fork for speed only in experiments.
Wrap for control.
Test for proof.
Replace by provider boundary.
Never let third-party code define Dominium law.
```

### 2.2 Framework approach versus modification approach

The user later pasted a summary comparing two ways to build an engine:

1. Assemble modular libraries into a framework.
2. Fork and customize a full engine.

The user said they liked the framework approach. That became a pivotal moment. The conversation then reframed the project as a **Domino Framework** that can be provided by any compatible Domino engine implementation and consumed by any compatible Dominium game implementation.

This means:

```text
A game should not directly depend on raylib, SDL2, Lua, ImGui, OpenGL, or OS APIs.
A game should depend on Domino services.
A Domino engine implementation chooses providers.
Profiles choose provider combinations.
```

### 2.3 Platform and language targets

The user gave target constraints including:

```text
Windows 7 SP1+
macOS 10.9.5+
Linux
C17 / C++17
Win32
Cocoa
SDL2
OpenGL 3.3
```

The report notes an unresolved verification issue: one assistant response indicated that the current visible repository still seemed to have C90/C++98 CMake settings, while a pasted transcript claimed the repo had moved to C17/C++17. This must be verified before implementation.

### 2.4 raylib and its ecosystem

raylib was the most heavily discussed third-party project. The user liked raylib and wanted to know how much of it could be used.

The conclusion was: **use it aggressively, but fence it.**

The raylib ecosystem was classified as follows:

| Component | Dominium role | Boundary |
|---|---|---|
| `raylib` | Broad first visible provider suite | Provider only, not architecture |
| `rlgl` | OpenGL-family abstraction provider | Not final direct `opengl33` law |
| `rlsw` | raylib software-render provider | Not canonical Dominium reference renderer |
| `raygui` | Early Workbench/debug UI provider | Not Workbench UI document law |
| `raudio` | Early audio provider | Presentation/audio provider only |
| `raymath` | Render/editor math helper | Not deterministic simulation math |
| `rtextures` / image loaders | Import/preview helpers | Not asset identity law |
| `rmodels` / model loading | Model import/preview | Not canonical scene graph or save format |

A key decision was that `rlsw` and `software` should not be conflated:

```text
runtime/render/providers/software/
  Dominium-owned deterministic/reference software renderer.

runtime/render/providers/rlsw/
  raylib ecosystem software renderer for headless screenshots, CI evidence,
  low-end fallback, and comparison.
```

Similarly, `rlgl` and `opengl33` should be separate:

```text
runtime/render/providers/rlgl/
  raylib OpenGL-family abstraction provider.

runtime/render/providers/opengl33/
  later direct Dominium-owned OpenGL 3.3 provider.
```

### 2.5 SDL2

SDL2 was treated as complementary to raylib, not replaced by it. SDL2 is a first-wave provider for platform, input, and possibly audio.

A likely profile could be:

```toml
[providers]
platform = "sdl2"
input    = "sdl2"
render   = "raylib" # or rlgl
audio    = "sdl2"   # or raudio
ui       = "raygui"
```

SDL2 gives the project another portability path and avoids assuming raylib must own the whole host/input stack forever.

### 2.6 Lua

The user said Lua support seemed wise for modules, packs, mods, CLI, or all of them. The conversation agreed, with a boundary:

```text
Lua is a script provider.
Dominium script API is the law.
Raw Lua ABI is not mod law.
```

The chat repeatedly recommended pinning a specific Lua provider such as:

```text
runtime/script/providers/lua54/
```

or:

```text
runtime/script/providers/lua55/
```

while exposing a stable Dominium script API such as:

```text
dominium.script.v1
```

Lua should be used for pack scripts, scenario scripts, CLI automation, Workbench automation, debug commands, import/export transforms, and non-authoritative hooks. Authoritative deterministic simulation logic should use Lua only after sandboxing, determinism testing, and replay proof.

### 2.7 Service-first provider architecture

An early directory sketch used paths like:

```text
runtime/render/raylib
runtime/audio/raylib
runtime/input/raylib
```

The conversation later refined that to:

```text
runtime/<service>/providers/<provider>
```

Example:

```text
runtime/platform/providers/raylib/
runtime/input/providers/raylib/
runtime/render/providers/raylib/
runtime/render/providers/rlgl/
runtime/render/providers/rlsw/
runtime/audio/providers/raudio/
runtime/ui/providers/raygui/
runtime/script/providers/lua54/
```

This matters because the repository should be organized around **Domino services**, not around third-party vendors.

The stable rule became:

```text
Service identity is first-party.
Provider implementation is replaceable.
Profiles select providers.
Apps do not hardwire providers.
```

### 2.8 Provider profiles

The conversation rejected backend-specific app identities as the main architecture. Instead of this:

```text
apps/client/rendered/raylib/
apps/client/rendered/sdl2_opengl33/
```

use generic apps:

```text
apps/client/
apps/workbench/
apps/server/
```

and provider profiles:

```text
release/profiles/client.raylib.toml
release/profiles/client.sdl2_raylib.toml
release/profiles/workbench.raylib.toml
release/profiles/server.null.toml
```

Profiles choose provider combinations; app identity remains stable.

### 2.9 Current `julesc013/dominium` comparison

The conversation included inspection of the current repository through GitHub connector calls. The earlier report concluded that Dominium already had useful seams such as system and render abstractions, including `dsys`, `d_gfx`, soft/null/stub backends, and command-buffer style rendering.

The important takeaway was that raylib should slot into existing or planned seams rather than replacing the architecture.

However, repo findings are marked **UNVERIFIED/STALENESS-RISK** because current branch state may have changed.

### 2.10 SpaceEngine, Celestia, PCGUniverse2, and pgg

The user asked whether these projects could help:

```text
https://spaceengine.org/
https://celestiaproject.space/
https://github.com/CelestiaProject/Celestia
https://github.com/mylescardiff/PCGUniverse2
https://github.com/Valian/pgg
```

The conclusions were:

| Project | Use directly? | Use as reference? | Main value |
|---|---:|---:|---|
| SpaceEngine | No | Yes | Universe-scale UX, addon model, catalogs, procedural fill, navigation |
| Celestia | Only with GPL-compatible strategy | Yes | Space visualization, catalogs, object navigation, coordinate handling |
| PCGUniverse2 | No unless license clarified | Yes | Galaxy/system/planet generation concepts, simplex noise, L-systems |
| Valian/pgg | No unless license clarified | Yes | Spherical terrain, chunked LOD, shader displacement |

The recommendation was to create research/reference notes, not vendor these projects as providers.

### 2.11 Other open-source engines and games

The conversation later widened into other possible projects. The rough classification was:

#### Real dependency/provider candidates

```text
raylib
SDL2
Lua
SQLite
Dear ImGui
Nuklear
stb libraries
cgltf / tinygltf / meshoptimizer
Jolt / Box2D later if needed
```

#### Mostly reference projects

```text
Luanti / Minetest
Cuberite
Terasology
OpenRA
Spring RTS
0 A.D.
Freeciv
Widelands
Mindustry
Endless Sky
Pioneer
Celestia
FreeOrion
Godot
O3DE
Torque3D
```

The reason for reference-only status varies: license, wrong language/stack, too large, wrong architecture, or risk of overwriting Dominium law.

### 2.12 Deterministic sparse delegated simulation

The user asked how to build a deterministic and sparse game where clients dynamically take on load from the host and contribute processing power, while allowing players/agents/NPCs to build arbitrary/infinite things anywhere.

The conversation coined or refined this idea:

```text
sparse deterministic delegated simulation
```

The proposed architecture was:

```text
infinite address space
finite active set
sparse materialization
deterministic local simulation islands
event-sourced state
client-contributed work
server/host-verified authority
```

The key correction was:

```text
Clients may compute.
Clients should not be blindly authoritative.
```

Clients can help with:

```text
meshing
LOD generation
pathfinding proposals
NPC planning proposals
CAD preview simulation
blueprint compilation
asset cooking
visibility/occlusion candidates
local prediction
compression
non-authoritative forecasts
```

But valuable shared state must be verified by the host/server before commit.

### 2.13 Work leases and verification

The proposed mechanism was work leases:

```text
Host assigns deterministic work packet.
Client computes result.
Client returns result + trace + state hash.
Host verifies by replay, quorum, spot-checking, invariant checks, trust tiers, or delayed finality.
Only verified deltas enter authoritative event log.
```

This should become a formal protocol later.

### 2.14 Infinite world and sparse state

The world should be infinite by addressability, not by simulating everything.

The cold/warm/active model was:

```text
COLD       seed + saved deltas only
WARM       metadata loaded, no full simulation
SCHEDULED  low-frequency analytic updates
ACTIVE     full deterministic simulation
HOT        combat/visible/contested/high-priority simulation
```

Untouched space can be a generator seed. Touched space is seed plus deltas. Busy areas are active states plus event logs. Dormant constructs can compact back into snapshots and summaries.

### 2.15 CAD, machines, arbitrary inventions

The user wants CAD-style creation systems, machines, inventions, and arbitrary things built anywhere by players, NPCs, and agents.

The conversation concluded that this is only feasible if design-time freedom is separated from runtime boundedness.

Design-time can allow:

```text
freeform CAD
parametric sketches
voxel/block editing
mesh import
mechanism design
logic circuits
fluid networks
electrical networks
materials
gears/belts/shafts
programmable controllers
blueprints
subassemblies
```

But compile-time should convert that into bounded structures:

```text
CAD document
  -> validation
  -> topology graph
  -> mass/inertia approximation
  -> collision hulls
  -> port graph
  -> machine graph
  -> render LODs
  -> damage graph
  -> blueprint hash
```

Runtime should simulate:

```text
physics proxy
machine graph
signal graph
resource graph
damage graph
ownership graph
render proxy
```

not arbitrary raw geometry forever.

### 2.16 Unified build transaction system

Players, agents, and NPCs should all mutate the world through the same command/event/build transaction system.

This gives:

```text
replayability
auditability
anti-cheat
debuggability
mod support
consistent AI/player rules
```

Agents should not directly alter world state. They submit build intents and actions through the same authority and validation pipeline.

### 2.17 Preservation/export task

The user uploaded a preservation prompt asking for a maximum-fidelity report, registers, spec sheet, aggregator packet, audit, and downloadable files. The previous package was generated with files numbered `00` through `09` plus a ZIP.

This new accompanying report extends that package with a more narrative, human-readable summary and an integrity/check manifest.

---

## 3. What Was Decided

The following are the strongest decisions or accepted directions from the conversation.

| ID | Decision | Status |
|---|---|---|
| D1 | Use a framework/provider approach instead of making Dominium a fork of a large engine. | Accepted direction |
| D2 | raylib should be used heavily as the first visible provider suite. | Accepted direction |
| D3 | Domino/Dominium own simulation, contracts, replay, saves, packs, commands, UI documents, provider law, and asset identity. | Core doctrine |
| D4 | Third-party libraries are providers, not architecture. | Core doctrine |
| D5 | Use `runtime/<service>/providers/<provider>`. | Accepted direction |
| D6 | Keep apps generic and use profiles to select providers. | Accepted direction |
| D7 | SDL2 remains a first-wave platform/input/audio provider. | Accepted direction |
| D8 | Lua is useful but must be pinned behind a Dominium script API. | Accepted direction |
| D9 | `rlsw` can be used, but not as canonical Dominium software reference renderer. | Recommended direction |
| D10 | `rlgl` can be used, but not as final direct OpenGL 3.3 law. | Recommended direction |
| D11 | External projects like SpaceEngine/Celestia/PCGUniverse2/pgg are mostly reference material. | Recommended direction |
| D12 | Sparse deterministic delegated simulation is the right conceptual model for the large game vision. | Recommended architecture |
| D13 | Client-contributed compute must be host/server verified. | Recommended architecture |
| D14 | Arbitrary CAD creations must compile to bounded runtime graphs/proxies. | Recommended architecture |
| D15 | Create a preservation/handoff package for future aggregation. | Completed in prior package, extended here |

---

## 4. What We Actually Did

During the conversation, we:

1. Defined the overall open-source acceleration doctrine.
2. Compared framework assembly against full-engine modification.
3. Evaluated raylib as a first provider suite.
4. Broke down raylib subcomponents and classified their roles.
5. Discussed SDL2 and Lua as first-wave providers.
6. Refined the source tree from vendor-shaped to service-first/provider-backed layout.
7. Compared the idea to visible structures in `julesc013/dominium`.
8. Evaluated SpaceEngine, Celestia, PCGUniverse2, and Valian/pgg.
9. Surveyed other open-source engines and games for research value.
10. Designed the high-level sparse deterministic delegated simulation doctrine.
11. Designed a high-level CAD/machine/invention runtime strategy.
12. Articulated the Domino Framework / Domino Engine / Dominium Game split.
13. Generated a prior handoff package with report, registers, spec sheet, aggregation packet, and ZIP.
14. In this follow-up, added an accompanying detailed human-readable report and package integrity manifest.

---

## 5. What Was Put Off for Later

The conversation intentionally did **not** resolve everything. The following items were put off for later implementation or verification.

### 5.1 Verification put off

```text
Verify actual repo C17/C++17 baseline.
Verify exact raylib version and old OS support.
Verify exact SDL2 version and old OS support.
Verify Lua 5.4 vs 5.5 choice.
Verify licenses for all second-wave dependencies.
Verify SpaceEngine/Celestia/PCGUniverse2/pgg legal boundaries before using anything.
```

### 5.2 Implementation put off

```text
Implement Domino Framework ABI.
Implement provider registry.
Implement provider manifests.
Implement null providers.
Implement raylib providers.
Implement SDL2 providers.
Implement Lua provider.
Implement conformance tests.
Implement Workbench proof.
Implement sparse simulation prototype.
Implement CAD/construct graph prototype.
Implement client work lease prototype.
```

### 5.3 Design put off

```text
Exact C ABI function tables.
Exact service list and service IDs.
Exact provider profile format.
Exact deterministic math policy.
Exact save/replay versioning policy.
Exact machine graph schema.
Exact CAD document schema.
Exact work lease verification policy.
Exact license/provenance policy.
Exact Workbench document/action/view model.
```

### 5.4 Project governance put off

```text
Dependency update policy.
Third-party patch policy.
GPL/LGPL quarantine policy.
CI platform matrix.
Compatibility lab for Windows 7/macOS 10.9.5/Linux.
Spec-book integration policy.
Generated-file preservation policy.
```

---

## 6. Things Not Explicitly Mentioned Enough but Worth Adding

The conversation covered architecture well, but future work should also cover these areas.

### 6.1 Security and anti-cheat threat model

Client-contributed compute needs a formal threat model. Questions include:

```text
What can malicious clients fake?
Which results are high-value?
Which work can be accepted without full replay?
What invariants are cheap to check?
When do we require quorum?
When can local co-op trust be relaxed?
```

### 6.2 Save migration and data compatibility

If Dominium is built around long-lived worlds, it needs explicit migration law:

```text
save schema versions
replay schema versions
provider profile versions
script API versions
asset cache versions
worldgen generator versions
construct blueprint versions
```

### 6.3 Performance budgets

The arbitrary CAD/machine system needs budgets at every level:

```text
per-cell tick budget
per-construct component budget
per-machine graph edge budget
per-script time/memory budget
per-client work lease budget
per-render LOD budget
per-agent planning budget
```

### 6.4 Accessibility and localization

Workbench and game UI should eventually include:

```text
text scaling
color contrast
action remapping
input modality abstractions
localization packs
screen-reader/native accessibility strategy
```

raygui/ImGui can bootstrap tools, but they should not be the final accessibility law.

### 6.5 Observability and diagnostics

The system should expose:

```text
state hashes
provider diagnostics
frame captures
work lease traces
replay diff tools
desync reports
asset provenance reports
performance counters
profile selection traces
```

### 6.6 Content moderation and user-generated content safety

Since players may build arbitrary things and use scripts/mods/packs, future design should consider:

```text
pack trust levels
script permissions
network-distributed content
user-generated names/textures/models
server policy enforcement
content signing
unsafe asset quarantine
```

### 6.7 Legal/provenance workflow

Before using external code/assets/data, create:

```text
third_party.toml
license manifests
source URL and commit pins
patch logs
asset provenance records
GPL/LGPL quarantine rules
unclear-license rejection policy
```

---

## 7. Recommended First Implementation Wedge

The strongest next implementation step remains:

```text
DOMINO-FRAMEWORK-WEDGE-01
```

Suggested deliverables:

```text
framework/include/domino/framework.h
framework/include/domino/engine.h
framework/include/domino/game.h
framework/include/domino/provider.h

contracts/provider/provider.schema.json
contracts/capability/capability.schema.json

runtime/platform/providers/null/
runtime/input/providers/null/
runtime/render/providers/null/
runtime/audio/providers/null/

runtime/platform/providers/raylib/
runtime/input/providers/raylib/
runtime/render/providers/raylib/
runtime/render/providers/rlgl/
runtime/render/providers/rlsw/
runtime/audio/providers/raudio/
runtime/ui/providers/raygui/

release/profiles/client.raylib.toml
release/profiles/server.null.toml

tools/validators/boundary/check_forbidden_includes.py
tools/validators/provider/check_provider_manifest.py
tools/validators/third_party/check_third_party_licenses.py
```

Acceptance tests:

```text
server.null profile:
  runs deterministic tick
  no raylib dependency
  same state hash on replay

client.raylib profile:
  opens window
  draws rect/text/debug scene
  receives input
  runs same deterministic game tick
  renders non-authoritative presentation

validators:
  no third-party headers in contracts/framework/game/content/saves/replays
  provider manifests validate
  third-party license manifests exist
```

---

## 8. Final Architectural Doctrine

The best distilled doctrine is:

```text
Domino is a framework contract and provider system.
A Domino engine implementation satisfies the framework.
A Dominium game implementation consumes the framework.
raylib, SDL2, Lua, ImGui, raygui, raudio, rlgl, rlsw, and other libraries are provider implementations, not the engine’s law.
```

For the game itself:

```text
Dominium is a sparse deterministic delegated simulation game.
The universe is infinite by addressability, not by always-live simulation.
Active cells are deterministic and event-sourced.
Clients may compute but host/server verifies commits.
Arbitrary CAD creations compile into bounded runtime graphs and proxies.
Players, NPCs, and agents submit the same command/build transactions.
```

---

## 9. Most Important Cautions

1. Do not make raylib the architecture.
2. Do not trust client compute without verification.
3. Do not copy GPL/proprietary/unclear-license code into the project by default.
4. Do not assume current repo state without checking.
5. Do not confuse `rlsw` with Dominium’s canonical reference renderer.
6. Do not confuse `rlgl` with final direct OpenGL 3.3 provider.
7. Do not let app folder names encode provider choices as permanent architecture.
8. Do not let raw Lua ABI become mod law.
9. Do not simulate arbitrary raw CAD geometry forever.
10. Do not treat all assistant recommendations as final user decisions.

---

## 10. Package Check Summary

This accompanying report was added to the prior package. A separate integrity/check manifest was also generated with file names, sizes, and SHA256 hashes. The complete package ZIP includes:

```text
Original pasted instruction file
Previous manifest/report/context/spec/register/aggregator/audit/bootstrap/in-chat-reader files
This new accompanying detailed human summary and report
New package integrity check file
```

The ZIP does not include the older ZIP inside itself to avoid nested archive confusion. It includes the individual files directly.

---

## 11. Suggested Next Question

The most productive next request is:

```text
Draft DOMINO-FRAMEWORK-WEDGE-01 as a complete implementation checklist with exact file paths, minimal C ABI headers, provider manifest schemas, profiles, validators, and acceptance tests.
```
