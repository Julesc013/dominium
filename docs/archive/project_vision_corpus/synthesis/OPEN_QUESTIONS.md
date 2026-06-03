Status: DERIVED
Last Reviewed: 2026-06-03
Supersedes: none
Superseded By: none
Stability: provisional
Authority Class: advisory_synthesis
Source Root: `docs/archive/conversations/`
Promotion Status: not_promoted
Canon impact: unchanged
Contract/schema impact: unchanged
Implementation impact: unchanged
Release impact: unchanged
Queue impact: unchanged

# Open Questions

The main unresolved issues are not lack of ideas; they are authority, scope, sequencing, and verification questions.

- The unresolved detail is the exact representation: voxel chunks, signed-distance functions, heightfields, material fields, climate grids, graph overlays, or hybrid systems.
- Open questions remain around body templates, death/backup rules, communication range, respawn cost, body upgrading, and whether player identity is software, hardware, or both.
- Workbench remains unresolved at the implementation level: read-only first is agreed, but exact UI shell design, renderer path, modules, and self-hosting milestones remain future tasks.
- The most blocking unresolved issues are repo baseline verification, exact dependency pins, minimal framework ABI, provider profile order, deterministic simulation spec, and license policy.
- - semantically known files move to canonical owners; - unknown or ambiguous files go to `archive/quarantine/<root>/`; - bad roots should not remain as active source; - active exceptions require owners and retirement plans.
- Unresolved issues include whether the official server is one designed star system, how many players can occupy a local area, what clients are allowed to compute, how region ownership works, and how to handle failure/recovery.
- The user explicitly wanted machine functions summarised into simple process steps where possible. This is a major performance strategy. The unresolved risk is how to keep player-designed machines expressive without creating exploits.
- The most important unresolved issue is formal classification. Without knowing which entities are strict SemVer components, suite versions, product release IDs, build fields, or capabilities, the rest of the policy cannot be enforced safely.
- A fifth tradeoff was open-source reuse versus licensing risk. Permissive libraries can be providers. GPL/proprietary/unclear projects should be research references unless the project deliberately adopts a compatible license/quarantine strategy.
- This topic matters because it ties together respawn, HUD, construction, automation, progression, and lore. It remains unresolved whether the long-term story is human restoration, robot autonomy, human embryo arrival, mystery lore, or player faction divergence.
- This is not just lore. It creates a physical economy around respawn, exploration, risk, remote bases, communications, and industrial capacity. Open questions include body templates, balance, backup/mind-state rules, death penalties, and single-player versus MMO differences.
- Future work should convert this into a dependency policy: use permissive/weak-copyleft libraries as providers where appropriate; use GPL/proprietary/unclear projects as research references unless explicitly quarantined; require provider manifests, license manifests, and conformance tests.
- The mothership should be powerful but limited. It can fabricate early bodies and precision items, but finite resources, low throughput, heat, wear, and mission reserves force players to mine, refine, fabricate, and build industry. The exact limits remain unresolved and are a top design task.
- The user prefers source-grounded, audit-ready technical reasoning, direct structure, and careful distinction between facts, recommendations, and unresolved issues. PROJECT-CONTEXT indicates Dominium values C89/C++98 portability, deterministic architecture, CLI/TUI support, and clean platform/runtime separation.
- The strongest unresolved issue is implementation focus. The project should not jump directly to galaxy/MMO scale. It should prove the mothership-to-remote-spawn-lab loop first. That loop tests the key systems: procedural terrain, robot spawning, fog of war, cut/fill, nanobot construction, resource accounting, fabrication, and sparse deterministic persistence.
- The exact first playable slice remains unresolved. The first provider wedge is clear, but exact sequence between client/workbench gameplay, Robot OS, and gameplay mechanics still needs a formal milestone. The exact Lua version, Linux baseline, current repo status, and external library/version support need verification. The exact degree of Unreal involvement remains unclear.
- Technical open questions include how soon provider manifests should be implemented relative to projection conformance, how to split raylib provider wedge into manifest/service/fence/implementation tasks, which Lua version to pin, whether `external/upstream` or `external/vendor` matches repo convention, and how full-gate tests should be routed without weakening active structure gates.
- Still unresolved: - verify latest live repo state after user-pasted Wave 1 completion; - generate/run `COMMAND-RESULT-VIEW-SLICE-01`; - prove package mount, replay proof, barebones client shell; - instantiate domain constitutions; - stabilize playable baseline; - build Workbench shell and tools; - classify/fix full CTest/T4 debt; - merge this chat with other old-chat reports into a master spec book.
- The user's most concrete design contribution was the robotic mothership premise. In the lore, humans sent a robotic seed ship to another solar system. It finds or lands on a suitable planet and begins manufacturing robot bodies that can rebuild civilisation. The user also floated mystery/lore possibilities around later human payloads, embryos, or future ships, but those remain optional and unresolved.
- The strongest technical identity is sparse deterministic simulation. The world should be generated from seeds and data, modified through sparse deltas and event logs, and expanded into visual detail only when sensed. Distant machines become process equations. Unknown terrain remains hidden. Unseen regions remain collapsed. Clients can assist with safe work, but hidden truth and authority-critical state remain server-controlled in MMO mode.
- This distinction became one of the most important conceptual tools from the chat. A distant planet can exist as procedural data and sparse edits without being actively simulated at per-object fidelity. A factory can exist and produce resources as a graph/rate model without every belt item being simulated. A hidden base can be authoritative on the server but unknown to the client. A region can be collapsed into macrostate and later refined when observed.
- The user became increasingly impatient because the visible root mess persisted after many tasks. The assistant eventually shifted from tiny low-risk moves to a deterministic bad-root router model: known files should move to their canonical homes, and unknown files should be routed to `archive/quarantine/<root>/`, rather than blocking cleanup. This was a major change in tempo. It preserved the principle of not guessing unknown semantics while allowing the directory structure to become clean.
- - `handoff`: `2` - `json`: `1` - `manifest`: `4` - `markdown`: `9` - `png`: `10` - `primary_report`: `3` - `prompt`: `4` - `reader_brief`: `5` - `registers`: `3` - `source_input`: `1` - `spec_sheet`: `2` - `text`: `1` - `unknown`: `10` - `verification`: `3` - `zip`: `4`
- - The exact first playable slice remains unresolved. The first provider wedge is clear, but exact sequence between client/workbench gameplay, Robot OS, and gameplay mechanics still needs a formal milestone. The exact Lua version, Linux baseline, current repo status, and external library/version support need verification. The exact degree of Unreal involvement remains unclear. - 1. Verify and pin external library/toolchain facts. - It remains uncertain how much the user wants Unreal in the near-term after raylib-first discussion. It also remains uncertain whether Lua 5.4 or 5.5 is preferred; the user appears to value pinning and stab...
