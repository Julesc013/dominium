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

# Decision Docket

This docket records decision-shaped archive evidence. It is a review queue, not a declaration of canon.

## Settled-Looking Decisions To Confirm Against Current Authority

- Another tradeoff is simulation realism versus compute cost. The chosen solution is deterministic sparse materialization rather than global brute-force simulation.
- DECISION-14 matters because `PACKAGE-MOUNT-SLICE-01` has only proven fixtures and reports. Treating it as package runtime would create false implementation claims.
- - "Which recommendations in this chat are actually accepted decisions, and which are just candidate architecture?" - "What exactly did we decide about Milestone 0?"
- The conversation made several strong decisions or near-decisions, but not all should be treated as final implementation law. The strongest accepted directions were:
- The final tradeoff was engine-first versus game-first. The conclusion was neither: build minimal vertical slices that are simultaneously game work and engine proof.
- **DECISION-10 - No-assets GUI floor.** The UI baseline doc already requires a zero-asset GUI floor. The chat expanded this into a product-grade primitive UI system.
- The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved.
- - Which decisions in this chat were clearly accepted by me, and which are still assistant recommendations? - Which compatibility promises should be made stable first?
- - "Which recommendations are actual decisions and which are only assistant suggestions?" - "Which decisions should become formal requirements in the master spec book?"
- 9. **Database/persistence system.** Event sourcing, snapshots, sparse chunk diffs, rollback, and audit trails were proposed, but no database technology or schema was chosen.
- Many architecture items are strong recommendations but not yet explicit user decisions. A future assistant should not say "the project decided X" unless the user ratifies it.
- The conclusion was "stable at the boundary, ruthless inside." Internal implementation can be rewritten if public contracts, tests, formats, and migration/refusal behavior hold.
- This preservation package explains the chat, records decisions, tasks, artifacts, risks, and open questions, and exports a structured spec/aggregation packet for future merging.
- The user likely wants future assistants to challenge weak framing, preserve uncertainty, avoid shallow "best practice" lists, and focus on decisions that survive future rewrites.
- - "Which decisions in this chat are final, and which are only tentative?" - "What decision would most likely need revisiting if the live repo contradicts our assumed queue state?"
- Do not merge the full universe/MMO/CAD material as near-term implementation requirements. They belong as long-term architecture context unless later accepted as staged requirements.
- Do not merge assistant brainstorming as final user decisions unless user accepted it. Do not overclaim full green. Do not add new roots. Verify live repo state before executing tasks.
- 4. "Which decisions are final, and which are still tentative?" 5. "Why did we reject Workbench as a monolithic editor?" 6. "Why is full CTest not blocking current product-spine work?"

## User Or Future Queue Decisions Needed

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

## Superseded Or Rejected Directions To Preserve

- This chat is a major planning pivot. It began with a Windows UI Editor/Tool Editor design and ended with a broader Dominium Workbench Platform architecture. The old editor plan is superseded as a final product. Its useful pieces should be recycled into Workbench modules.
- - Did applied Codex prompts fully succeed? - Has launcher hardening already run? - Do command graph/UI IR/binding validator exist? - Does launcher run with zero packs and missing locale? - Does launcher refuse BUILD-ID mismatches? - Are any shared headers ambiguously owned?
- Earlier proposed layouts using `setup/adapters`, adapter-local packaging, and `core/source` were superseded. The canonical setup layout is `setup/core/{fetch,verify,install,rollback}`, `setup/include/{dsk,dsu}`, `setup/packages`, `setup/platform`, `setup/tests`, and `setup/ui`.
- - Domino = engine core; Dominium = game/runtime/tooling layer. - Specs are normative; README is descriptive. - 286+ full engine target; CP/M limited only. - Unified source hierarchy for all platforms. - No divergent port implementations. - Capability-based graceful degradation. - Lockstep is canonical. - Disk versions immutable. - `content.lock` mismatch fatal until reconciled.
- - Candidates: `135` - Source conversations represented: `45` - Noisy or archival-process candidates: `17` - Overlong candidates: `44` - Candidates with `not_checked` repo conflict: `135`
- At the beginning, the discussion was narrow: the user was choosing fixed-point coordinate precision for a world divided into powers-of-two spatial units. That quickly expanded into a much larger architecture question: how should an enormous procedural world be represented, simulated, saved, streamed, rendered, modified, and extended without becoming inconsistent, bloated, or impossible to maintain?
