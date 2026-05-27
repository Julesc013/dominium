# Registers — Dominium XStack Lab Galaxy Handoff

## 1. Workstream Register

| ID | Name | Label | Objective | Status | Priority | Next action |
| --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Dominium / Domino deterministic simulation architecture | FACT | Preserve and extend the deterministic universe simulation architecture based on Assemblies, Fields, Processes, Agents, and Law. | active | P0 | Verify current repo docs and schemas against the constitutional architecture and glossary. |
| WORKSTREAM-02 | XStack portable agentic development suite | FACT | Maintain XStack as a portable, removable, deterministic agentic development and governance suite. | active | P0 | Audit actual tools/xstack, scripts/dev/gate.py, .gitignore, and removability tests. |
| WORKSTREAM-03 | Lab Galaxy deterministic substrate | FACT | Create a reproducible deterministic Lab Galaxy build with pack-driven content, session boot, navigation, tool UI, ROI/SRZ scaffolding, and deterministic packaging. | active but verification pending | P0 | Perform a prompt-by-prompt deliverable audit against actual repository files and the transcript. |
| WORKSTREAM-04 | Canonical docs, glossary, and README/documentation front door | FACT | Create usable canonical documentation and an industry-standard README layer without dumping internal constitution into the README. | active | P1 | Audit docs for contradictions, duplicate canon, and unresolved TODOs that should be issue-tracked. |
| WORKSTREAM-05 | Survival and gameplay vertical slice | INFERENCE | After substrate verification, implement a real playable survival slice using profiles, law, processes, diegetic UI, needs/resources/hazards/crafting/shelter/death persistence. | future active plan | P2 after audit | After audit, generate a bounded Survival Vertical Slice prompt. |
| WORKSTREAM-06 | Future realism/domain pack extensibility | INFERENCE | Prepare architecture for astronomy-realistic skies, climate/weather, biology, evolution, materials/affordances, diseases, injuries, animals, chemistry, magic, and other realism/fantasy domains as optional packs. | future plan | P3 | Keep as design constraint; do not implement until survival/lab substrate verified. |

## 2. Decision Register

| id | decision | status | label | evidence_or_basis | rationale | implications | related_workstreams | uncertainty |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Use Assemblies, Fields, Processes, Agents, and Law as the core ontology. | accepted | FACT | Repeatedly specified in the conversation and constitutional prompt. | Provides a minimal stable model for simulation, gameplay, extension, and governance. | All mechanics must reduce to these primitives. | WORKSTREAM-01 | Repository implementation must be verified. |
| DECISION-02 | All mutation must occur through Processes. | accepted | FACT | User repeatedly wanted process-only mutation; AGENTS/canon prompts enforce it. | Preserves deterministic replay and prevents hidden state changes. | UI/tools/camera/survival actions must emit intents/processes, not mutate fields directly. | WORKSTREAM-01, WORKSTREAM-03, WORKSTREAM-05 | Need code audit for violations. |
| DECISION-03 | TruthModel, PerceivedModel, and RenderModel must remain separated. | accepted | FACT | Prompt 7 and prior design; renderer must never access TruthModel. | Prevents epistemic leakage and multiplayer/client cheating. | UI binds only to PerceivedModel; renderer consumes RenderModel only. | WORKSTREAM-01, WORKSTREAM-03 | Need test/build boundary verification. |
| DECISION-04 | Use named RNG streams, fixed-point authoritative logic, and replay hashes for determinism. | accepted | FACT | Multiple canon/AGENTS requirements. | Ensures reproducible simulation across hardware/thread counts. | No nondeterministic wall-clock inputs in canonical state. | WORKSTREAM-01 | Thread-count invariance is reported partly stubbed. |
| DECISION-05 | XStack must be portable and removable from runtime. | accepted | FACT | User explicitly stated XStack should be a portable agentic development suite and removable with no impact on code/data runtime. | Avoids development tooling contaminating engine/game. | Runtime must not import tools/xstack. | WORKSTREAM-02 | Need actual removability test pass. |
| DECISION-06 | Mechanical blockers must be remediated instead of halting and asking the user. | accepted | FACT | User repeatedly expressed frustration with Codex stopping at gates. | Maintains autonomous queue development. | Prompts/gate/ControlX should self-heal mechanical failures. | WORKSTREAM-02 | Agent behavior depends on future prompts/tools. |
| DECISION-07 | Use FAST/STRICT/FULL profiles with caching/sharding rather than full verification on every prompt. | accepted | FACT | Extensive gate optimization work and later transcript using tools/xstack/run profiles. | Prevents governance throughput collapse. | Local iteration should use FAST; strict/full only as needed. | WORKSTREAM-02 | Need reconcile old gate.py with new tools/xstack/run. |
| DECISION-08 | Run-meta should not dirty tracked files; snapshot mode is the intended tracked-report writer. | accepted but potentially contradicted | FACT | Final XStack polish established no tracked writes outside snapshot mode; transcript later committed docs/audit artifacts. | Keep repo clean after verification. | Need audit docs/audit tracking policy. | WORKSTREAM-02 | Potential contradiction with later audit snapshot commit. |
| DECISION-09 | Prefer tools/xstack/run as stable XStack surface in the 13-prompt substrate. | accepted in transcript | FACT | Prompt 5/13 explicitly made tools/xstack/run the stable orchestrator and reported pass. | Consolidates XStack commands. | Future prompts may use tools/xstack/run fast/strict/full. | WORKSTREAM-02, WORKSTREAM-03 | Need verify interaction with scripts/dev/gate.py. |
| DECISION-10 | Use data-only packs and typed contributions. | accepted | FACT | Prompts 3, 4, 9, 10, 11 use packs and typed contributions. | Allows modular content without runtime hardcoding. | No executable code inside packs. | WORKSTREAM-03, WORKSTREAM-06 | Need verify pack manifests and loader enforce it. |
| DECISION-11 | Compile pack contributions into deterministic registries and lockfiles before runtime. | accepted | FACT | Prompts 4 and 13; registry_compile and lockfile_build reported. | Prevents runtime merging and improves reproducibility. | Session boot/launcher must enforce lockfile. | WORKSTREAM-03 | Need validate lockfile commands. |
| DECISION-12 | Lab Galaxy build uses headless/deterministic verification, not necessarily full interactive GUI. | accepted by implementation | FACT | Prompt 10 notes actual interactive GUI session not run; verification used deterministic headless UI tests. | Keeps milestone verifiable and low-risk. | Do not overclaim interactive gameplay yet. | WORKSTREAM-03 | Actual client interactivity remains to be built. |
| DECISION-13 | SRZ v1 remains single-process/single-shard ready, no networking yet. | accepted | FACT | Prompt 12 constraints and reported TODOs. | Prepare sharding without nondeterministic networking complexity. | Distributed SRZ is future work. | WORKSTREAM-03 | Need verify SRZ tests. |
| DECISION-14 | README should be an accessible front door; Constitution/glossary remain deeper docs. | accepted conceptually | FACT | User asked about README and accepted direction. | Avoid overwhelming lay users while preserving technical depth. | README links to architecture/canon docs. | WORKSTREAM-04 | Need verify README generated or updated. |
| DECISION-15 | Glossary should be normative rather than merely descriptive. | accepted | FACT | User explicitly said glossary/dictionary should be normative. | Prevents conceptual drift. | Deprecated/reserved terms can be enforced. | WORKSTREAM-04 | Need verify glossary quality. |
| DECISION-16 | Survival default should be diegetic-only with no non-diegetic HUD/freecam/console. | accepted conceptually | FACT | User explicitly wanted survival-style gameplay with no non-diegetic epistemic UI/HUD. | Supports immersive survival and epistemic integrity. | HUD/debug/freecam must be law/lens gated. | WORKSTREAM-05 | Not implemented as survival yet. |
| DECISION-17 | Hardcore, Creative, Observer, Lab are law/profile deltas rather than mechanics forks. | accepted | FACT | Repeated design and mode refactor discussions. | Avoids hardcoded branching. | Modes are labels only; code uses profiles. | WORKSTREAM-05 | Need future code enforcement. |
| DECISION-18 | Survival vertical slice should be bounded: needs, hazards, resources, crafting, shelter, death persistence. | planned | INFERENCE | Assistant/user planning, not yet executed. | Avoid meta spiral and deliver play. | Likely next feature after audit. | WORKSTREAM-05 | User may choose different next work. |
| DECISION-19 | Realism extensions should be domain/model packs + solver tiers + observation layers. | accepted conceptually | FACT | User asked broad realism questions; assistant proposed and user continued with architecture. | Avoid impossible global micro-simulation. | Astronomy/weather/biology/magic can be optional packs. | WORKSTREAM-06 | Not all domains implemented. |
| DECISION-20 | Graceful degradation must change fidelity/presentation, not epistemics or determinism. | accepted conceptually | FACT | User explicitly asked degradation without degrading epistemics/fidelity/information/determinism; design responded with budget/fidelity policies. | Avoid lag and truth leakage. | Refuse or degrade solver tier deterministically. | WORKSTREAM-06 | Implementation limited to Prompt 11 scaffolding. |

## 3. Task Register

| id | task | priority | urgency | owner | dependencies | inputs_needed | expected_output | next_step | related_workstreams | label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Verify current repository state after the 13-prompt run. | P0 | immediate | new assistant / user with repo access |  | Repository checkout | Factual status report: clean/dirty, commits, files, verification results. | Run git status/log and tools/xstack/run fast. | WORKSTREAM-02, WORKSTREAM-03 | FACT |
| TASK-02 | Audit old gate.py versus new tools/xstack/run to avoid divergence. | P0 | high | new assistant/Codex | TASK-01 | scripts/dev/gate.py, tools/xstack/run, docs/testing/xstack_profiles.md | Entrypoint map and recommended canonical command path. | Inspect files and docs. | WORKSTREAM-02 | INFERENCE |
| TASK-03 | Verify XStack removability. | P0 | high | new assistant/Codex | TASK-01 | Removability test if present | Pass/fail proof that runtime does not depend on tools/xstack. | Run reported removability test or equivalent. | WORKSTREAM-02 | FACT |
| TASK-04 | Audit tracking/ignore policy for generated outputs and docs/audit artifacts. | P1 | high | new assistant/Codex | TASK-01 | .gitignore, git ls-files docs/audit, artifact contract registry | List of tracked/ignored artifacts and policy discrepancies. | Run git ls-files and inspect .gitignore. | WORKSTREAM-02 | FACT |
| TASK-05 | Perform prompt-by-prompt completion audit for prompts 1–13. | P0 | immediate | new assistant/Codex | TASK-01 | transcript.txt, repo tree | Deliverable matrix: present/missing/partial/contradictory. | Build checklist from transcript and compare to files. | WORKSTREAM-03 | FACT |
| TASK-06 | Run or verify Lab Galaxy deterministic build pipeline. | P1 | medium-high | new assistant/Codex | TASK-01, TASK-05 | setup/build, launcher/launch, bundle.base.lab | Reproduced dist hashes/composite hash or discrepancy report. | Run packaging/launcher commands if feasible. | WORKSTREAM-03 | FACT |
| TASK-07 | Audit canonical docs/glossary/AGENTS.md consistency. | P1 | medium | new assistant | TASK-01 | docs/canon, AGENTS.md, docs/contracts | Doc consistency report and list of unresolved TODOs. | Inspect docs and run glossary/canon checks. | WORKSTREAM-01, WORKSTREAM-04 | FACT |
| TASK-08 | Produce or verify industry-standard README/docs entry layer. | P2 | medium | future assistant/Codex | TASK-05, TASK-07 | Actual repo docs/code | README/CONTRIBUTING/ARCHITECTURE/XSTACK docs if missing or refined. | Audit README against actual code. | WORKSTREAM-04 | INFERENCE |
| TASK-09 | Plan first Survival Vertical Slice prompt after audit. | P2 | after audit | user + assistant | TASK-05 | Verified substrate state | Bounded implementation prompt for needs/hazards/resources/crafting/shelter/death. | Confirm user wants survival next. | WORKSTREAM-05 | INFERENCE |
| TASK-10 | Implement survival diegetic lens enforcement when survival work begins. | P2 | after survival starts | Codex/future assistant | TASK-09 | Lens/law profile registries | Tests proving no HUD/freecam/console in survival default. | Include in survival prompt. | WORKSTREAM-05 | FACT |
| TASK-11 | Prepare future realism domain pack strategy. | P3 | low | future assistant | TASK-05, TASK-09 | Domain registry, solver tiers, budget/fidelity policies | Roadmap for optional realism packs. | Do not implement until core gameplay direction clear. | WORKSTREAM-06 | INFERENCE |
| TASK-12 | Decide whether to amend/rebase poor first commit message. | P3 | before push if not pushed | user | TASK-01 | Remote push status | Clean or accepted commit history. | If not pushed, consider interactive rebase/amend. | WORKSTREAM-03 | FACT |

## 4. Constraint Register

| id | constraint | type | hard_or_soft | source_or_basis | implication | violation_risk | confidence | label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | No hardcoded mode flags; use profiles/law/parameters. | architecture | hard | User/canon | Search and reject survival_mode/creative_mode/hardcore_mode/debug_mode/godmode/sandbox identifiers. | high | 5 | FACT |
| CONSTRAINT-02 | All simulation mutation through Processes only. | determinism | hard | User/canon | UI/session tools must emit intents/processes. | high | 5 | FACT |
| CONSTRAINT-03 | TruthModel/PerceivedModel/RenderModel separation. | epistemic | hard | User/canon/Prompt 7 | Renderer/UI cannot access TruthModel directly. | high | 5 | FACT |
| CONSTRAINT-04 | Deterministic replay and hash equivalence. | determinism | hard | User/canon | No nondeterministic clocks/timestamps in canonical outputs. | high | 5 | FACT |
| CONSTRAINT-05 | XStack must be portable/removable. | tool/runtime boundary | hard | User explicit concern | Runtime cannot import tools/xstack. | high | 5 | FACT |
| CONSTRAINT-06 | Mechanical blockers should be remediated automatically. | agentic workflow | hard preference | User statements during gate/UAEP discussion | Do not stop and ask whether to fix obvious gate/tool issues. | high | 5 | FACT |
| CONSTRAINT-07 | Verification must be fast, incremental, cached, sharded. | performance | hard practical | Gate performance work | Avoid monolithic local testx_all/full scans. | high | 5 | FACT |
| CONSTRAINT-08 | Run-meta must not dirty tracked files except explicit snapshot/canonical reports. | artifact hygiene | hard unless superseded | XStack final polish | Audit docs/audit tracking. | medium-high | 4 | FACT |
| CONSTRAINT-09 | Do not add governance without concrete failure class. | process | soft/hard preference | User desire to stop governance spiral | Prefer feature work after audit. | medium | 4 | INFERENCE |
| CONSTRAINT-10 | Packs are data-only. | pack system | hard | Prompts 3 and 10 | No executable code inside packs. | medium | 5 | FACT |
| CONSTRAINT-11 | Runtime uses compiled registries and lockfiles, not raw pack merging. | integration | hard | Prompts 4, 6, and 13 | Session boot/launcher enforces lockfile. | medium-high | 5 | FACT |
| CONSTRAINT-12 | Glossary is normative. | documentation/governance | hard | User explicit instruction | Definitions constrain code/docs; deprecated terms enforced. | medium | 5 | FACT |
| CONSTRAINT-13 | README should be accessible; deep doctrine belongs in docs/canon or architecture docs. | documentation | soft | README discussion | Do not dump Constitution into README. | low-medium | 4 | FACT |
| CONSTRAINT-14 | Survival default has no non-diegetic HUD/freecam/console. | UX/epistemic | hard for survival | User explicit preference | Survival UI must be diegetic lens/instrument driven. | high when survival begins | 5 | FACT |
| CONSTRAINT-15 | Hardcore is law/parameter delta, not separate mechanics fork. | game architecture | hard | Mode refactor decisions | No hardcore branch. | medium | 4 | FACT |
| CONSTRAINT-16 | No survival/crafting/economy in Lab Galaxy substrate prompts. | scope | hard for prompts 7-13 | Transcript prompts | Do not misrepresent Lab Galaxy as survival gameplay. | medium | 5 | FACT |
| CONSTRAINT-17 | Graceful degradation must not degrade epistemics or determinism. | performance/epistemic | hard | User realism/performance discussion | Use budget/fidelity policies and refusal, not nondeterministic degradation. | medium-high | 4 | FACT |

## 5. User Preference Register

| id | preference | source_basis | strength | implication | risk | label |
| --- | --- | --- | --- | --- | --- | --- |
| PREFERENCE-01 | Responses should start with model/date/time prefix. | User profile instructions. | explicit | Use prefix in future replies if not overridden. | User may see responses as noncompliant. | PROJECT-CONTEXT |
| PREFERENCE-02 | Prioritize epistemic accuracy and long-term correctness. | User profile. | explicit | Label uncertainty and verify current facts. | Overconfident answers damage trust. | PROJECT-CONTEXT |
| PREFERENCE-03 | Do not ask obvious permission to fix mechanical issues. | Repeated user statements in chat. | explicit | Provide concrete remediation or execute if tool available. | User frustration. | FACT |
| PREFERENCE-04 | Avoid arbitrary time/token limits that halt autonomous work. | User statements during gate optimization. | explicit | Use structural bounding/caching instead of hard stop limits. | Development stalls. | FACT |
| PREFERENCE-05 | Keep systems modular, extensible, robust, reliable, future-proof. | Repeated user phrasing. | explicit | Evaluate designs through modularity/portability. | Short-term hacks accumulate. | FACT |
| PREFERENCE-06 | XStack must remain portable/removable. | Explicit user concern. | explicit | Audit runtime coupling. | Wrong architecture. | FACT |
| PREFERENCE-07 | Detailed prompts and reports are acceptable when useful. | User repeatedly requested mega prompts and maximum-fidelity packets. | explicit | Do not over-compress critical handoffs. | Context loss. | FACT |
| PREFERENCE-08 | After governance is stable, move to actual game/engine/client work. | User repeatedly wanted survival/building/playing. | inferred/explicit | Avoid unnecessary governance churn after audit. | Meta spiral. | INFERENCE |

## 6. Open Questions Register

| id | question | why_it_matters | known | unknown | resolution_path | priority | related_workstreams | label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Which verification entrypoint is canonical now: scripts/dev/gate.py or tools/xstack/run? | Avoid two diverging governance systems. | Earlier chat hardened gate.py; later transcript implemented tools/xstack/run. | Actual repo integration and intended future command. | Inspect docs/testing/xstack_profiles.md, scripts/dev/gate.py, tools/xstack/run, AGENTS.md. | P0 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-02 | Are docs/audit run-meta artifacts intentionally tracked or accidentally committed? | Conflicts with run-meta isolation policy. | Transcript reports a commit refreshing audit snapshots and proof manifests. | Whether these are canonical snapshots or run-meta drift. | Inspect derived artifact contract, docs/audit files, .gitignore, and git ls-files. | P1 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| QUESTION-03 | Did all 13 prompts actually implement their deliverables in the repo? | User explicitly asked to ensure completion and consistency. | Transcript reports success. | Actual file-level completeness and correctness. | Prompt-by-prompt repo audit. | P0 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-04 | Is the Lab Galaxy milestone truly complete or only headless/tooling complete? | Affects whether to proceed to gameplay or finish UX. | Prompt 13 marks milestone complete; prompt 10 notes interactive GUI not manually run. | User expectations for complete. | Run dist/launcher and inspect milestone doc. | P1 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| QUESTION-05 | Does runtime code fully preserve the process-only mutation and truth/render boundary? | Core architecture depends on it. | Tests reportedly added. | Actual code path coverage. | Run/inspect boundary tests and static scans. | P1 | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| QUESTION-06 | Are README and high-level docs polished and consistent with actual implementation? | Project needs human-readable front door. | Discussed and prompts may have updated docs. | Actual README quality. | Audit README/CONTRIBUTING/docs. | P2 | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| QUESTION-07 | Should next feature work be survival vertical slice or Lab Galaxy refinement? | Determines next prompt direction. | Survival was strongly discussed; Lab Galaxy substrate just ran. | User current preference after audit. | Ask after audit, or present options. | P2 | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-08 | Should survival be observer-first or embodied first? | Changes implementation shape. | Observer-first was recommended earlier; user wants actual playing/building. | Final user choice. | Confirm after substrate audit. | P2 | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| QUESTION-09 | When should advanced realism domains be implemented? | Avoid scope explosion. | Architecture should support them as packs. | Priority after survival/lab. | Keep as roadmap; implement only after bounded milestone. | P3 | WORKSTREAM-06 | INFERENCE |
| QUESTION-10 | Are the 10 thematic commits already pushed? | Determines whether history can be cleaned or must be preserved. | Transcript says branch ahead by 10 commits and clean. | Remote state. | git status --branch; git log origin/main..HEAD. | P0 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |

## 7. Artifact Ledger

| id | name_or_description | type | purpose | status | origin | carry_forward | notes | label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | Dominium Constitutional Architecture & Execution Contract v1 / constitution_v1.md | document | Canonical architecture doctrine. | reported created in transcript; must verify | This chat and Prompt 1/13 | yes | May overlap with older ARCH0_CONSTITUTION docs. | FACT |
| ARTIFACT-02 | Canonical glossary v1.0.0 / glossary_v1.md | document | Normative definitions and deprecated/reserved terms. | reported created in transcript; must verify | This chat and Prompt 1/13 | yes | Should be bound to RepoX eventually. | FACT |
| ARTIFACT-03 | AGENTS.md | control file | Binding rules for future agents. | reported created | Prompt 1/13 | yes | High priority to inspect. | FACT |
| ARTIFACT-04 | docs/contracts/*.md | contract docs | SessionSpec, AuthorityContext, LawProfile, Lens, Refusal, versioning etc. | reported created/updated | Prompts 1,2,6,7,8,10,12,13 | yes | Need consistency audit. | FACT |
| ARTIFACT-05 | UAEP-1 / UAEP-1H prefix | prompt policy | Autonomous execution prefix for bad prompts. | designed in chat | This chat | yes | Doctrine, not necessarily repo file. | FACT |
| ARTIFACT-06 | tools/xstack/run / run.cmd / run.py | tool command | Stable FAST/STRICT/FULL XStack entrypoint in 13-prompt substrate. | reported implemented | Prompt 5/13 | yes | Need verify against old gate.py. | FACT |
| ARTIFACT-07 | scripts/dev/gate.py | tool command | Earlier optimized gate system. | exists historically; current relation unknown | Earlier in this chat | yes but audit | Possible divergence. | FACT |
| ARTIFACT-08 | tools/xstack/repox, testx, auditx, controlx, performx, compatx, securex | tooling | Governance/verification suite modules. | reported implemented/expanded | Earlier hardening + Prompt 5/13 | yes | Need check modularity/removability. | FACT |
| ARTIFACT-09 | XStack production hardening reports | reports | Evidence of gate performance/removability/cache/determinism. | reported earlier | Previous part of chat | maybe | May be superseded by new tools/xstack substrate. | FACT |
| ARTIFACT-10 | .gitignore update for tools/xstack/out/** | repo policy | Ignore generated XStack run outputs. | reported committed | Final commit batching | yes | Commit message first attempt odd; verify file. | FACT |
| ARTIFACT-11 | schemas/*.schema.json | schemas | Canonical JSON schemas v1.0.0. | reported added | Prompts 2,6,9,10,11,12 | yes | Must validate. | FACT |
| ARTIFACT-12 | tools/xstack/compatx/schema_validate/version_registry | tooling | Deterministic schema validation and migration stubs. | reported implemented | Prompt 2 | yes | Need verify CLI. | FACT |
| ARTIFACT-13 | packs/* and bundles/bundle.base.lab | content/data | Pack-driven Lab Galaxy content and bundle profile. | reported committed | Prompts 3,6,8,9,10,11 | yes | Check pack schema validity. | FACT |
| ARTIFACT-14 | tools/xstack/registry_compile and lockfile tools | tooling | Deterministic registry compilation and bundle lockfile. | reported implemented | Prompt 4 | yes | Key for reproducibility. | FACT |
| ARTIFACT-15 | tools/xstack/sessionx and session_create/session_boot/session_script_run | tool/runtime harness | Headless deterministic session lifecycle and script runner. | reported implemented | Prompts 6,8,12 | yes | Clarify tool harness vs product runtime. | FACT |
| ARTIFACT-16 | engine/include/domino/truth_model_v1.h, client/observability, client/presentation | runtime boundary stubs | Truth/Perceived/Render separation proof. | reported implemented | Prompt 7/10 | yes | Need build verification. | FACT |
| ARTIFACT-17 | Astronomy packs: astronomy.milky_way, astronomy.sol, planet.earth | content packs | Milky Way/Sol/Earth navigation data and site registry. | reported implemented | Prompt 9 | yes | Data accuracy is minimal/coarse, not scientific-grade. | FACT |
| ARTIFACT-18 | Tool UI packs: navigation, inspector, time_control, log_viewer | tool packs | Descriptor-driven lab UI windows. | reported implemented | Prompt 10 | yes | Headless UI tests only; not manually interactive. | FACT |
| ARTIFACT-19 | tools/setup/build and tools/launcher/launch | tooling | Deterministic dist build and launcher lockfile enforcement. | reported implemented | Prompt 13 | yes | Important to verify. | FACT |
| ARTIFACT-20 | docs/architecture/*.md | architecture docs | Truth model, observation, pack system, registry compile, time, SRZ, packaging, etc. | reported created/updated | Multiple prompts | yes | May contain placeholders/TODOs. | FACT |
| ARTIFACT-21 | tools/xstack/skills/*.md | skill templates | Agentic task templates for repo audit/schema/pack/client UI/TestX. | reported created/updated | Prompt 1 and later | yes | Useful but may need alignment to final commands. | FACT |
| ARTIFACT-22 | Survival Vertical Slice prompt plan | future prompt/plan | Future survival implementation plan. | planned, not executed | This chat | yes | Only after audit. | INFERENCE |
| ARTIFACT-23 | Diegetic survival lens/profile doctrine | design decision | Survival no non-diegetic UI/HUD by default. | accepted conceptually | This chat | yes | Must be enforced when survival implemented. | FACT |
| ARTIFACT-24 | Future realism/domain pack doctrine | design rationale | Support realism/magic/weather/biology/etc via packs/solvers/budgets. | planned, not executed except astronomy scaffold | This chat | yes | Avoid scope creep. | FACT |
| ARTIFACT-25 | transcript.txt | uploaded file | Full transcript of new 13-prompt run and commit batching. | available in this chat file context | User upload | yes | Primary evidence for 13-prompt run. | FACT |

## 8. Rejected / Superseded Options Register

| id | option | status | reason | final_or_tentative | reconsider_conditions | related_workstreams | label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Hardcoded mode flags | rejected | Causes branching, drift, and violates profile doctrine. | final | None known. | WORKSTREAM-01, WORKSTREAM-05 | FACT |
| REJECTED-02 | Full gate/check suite on every prompt | rejected | Destroyed throughput and wasted agentic development time. | final | Only release/CI/full-all contexts. | WORKSTREAM-02 | FACT |
| REJECTED-03 | Runtime depends on XStack | rejected | XStack must be portable/removable. | final | None known. | WORKSTREAM-02 | FACT |
| REJECTED-04 | Dump constitutional contract into README | rejected | Too overwhelming; README should be accessible front door. | final | Never as the main README; deep docs can link. | WORKSTREAM-04 | FACT |
| REJECTED-05 | Live-switch law profiles mid-session for early survival | deprioritised | Complicates determinism; session restart boundary preferred. | tentative | After transition contract matures. | WORKSTREAM-05 | INFERENCE |
| REJECTED-06 | Global full micro-simulation for realism | rejected | Computationally infeasible; use macro capsules and interest regions. | final | Never as global default; micro-sim in activated contexts only. | WORKSTREAM-06 | FACT |
| REJECTED-07 | Rewrite gate/XStack in Rust or C++ before profiling | rejected/deprioritised | Bottleneck was algorithmic scoping/caching, not interpreter speed. | tentative | If true CPU-bound hotspot remains after incremental architecture. | WORKSTREAM-02 | FACT |
| REJECTED-08 | Manual prompt rewriting of all old prompts | rejected | Too much work; use UAEP/reconciliation/ControlX-like sanitization. | final | Only for specific high-risk prompt. | WORKSTREAM-02 | FACT |

## 9. Risk Register

| id | risk | consequence | likelihood | severity | mitigation | related_workstreams | label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Transcript overclaims implementation status. | Future work builds on missing/partial substrate. | medium | high | Verify repo files and run tests before proceeding. | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| RISK-02 | Old gate.py and new tools/xstack/run diverge. | Different agents use different verification paths. | medium | high | Entrypoint audit and docs update. | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-03 | Run-meta artifacts tracked in docs/audit. | Dirty repo, false changes, cache/policy confusion. | medium | medium-high | Tracking/ignore audit; mark snapshot vs run-meta. | WORKSTREAM-02 | FACT |
| RISK-04 | XStack contaminates runtime imports/builds. | Portable suite no longer removable. | medium | high | Run removability test and static import scan. | WORKSTREAM-02 | FACT |
| RISK-05 | Mode flags or direct mutation creep in. | Breaks core architecture and future modularity. | medium | high | RepoX/AuditX scan; enforce glossary/deprecated terms. | WORKSTREAM-01, WORKSTREAM-05 | FACT |
| RISK-06 | Governance creep continues despite production hardening. | User loses productivity again. | medium | medium | Freeze governance unless concrete failure appears. | WORKSTREAM-02 | INFERENCE |
| RISK-07 | Lab Galaxy is headless only but misrepresented as interactive gameplay. | Wrong expectations for next stage. | medium | medium | Document that UI host is headless/minimal and interactive GUI not manually verified. | WORKSTREAM-03 | FACT |
| RISK-08 | New packages/schemas docs inconsistent after rapid commits. | Future prompts encounter contradictions. | medium | medium-high | Prompt-by-prompt completion/consistency audit. | WORKSTREAM-03 | FACT |
| RISK-09 | Glossary over-freezes terms prematurely. | Bad abstractions become constraints. | low-medium | medium | Normative glossary with versioning and change workflow. | WORKSTREAM-04 | INFERENCE |
| RISK-10 | README/docs become too internal or overlong. | Less useful for laymen/developers. | medium | low-medium | Layer docs: README summary, architecture details, canon deep reference. | WORKSTREAM-04 | FACT |
| RISK-11 | Survival implementation becomes recipe/hardcoded-mode driven. | Breaks modular realism and profile doctrine. | medium | high | Use LawProfile/ExperienceProfile/ParameterBundle plus affordance/process graph. | WORKSTREAM-05 | INFERENCE |
| RISK-12 | Survival adds non-diegetic HUD by convenience. | Violates user desired survival epistemics. | medium | high | Strict survival diegetic lens tests. | WORKSTREAM-05 | FACT |
| RISK-13 | Future realism requests trigger impossible global micro-simulation. | Lag and architectural collapse. | medium | high | Domain packs, solver tiers, macro capsules, interest regions. | WORKSTREAM-06 | FACT |
| RISK-14 | Modded realism bypasses law/determinism/security. | Inconsistent or unsafe simulation. | medium | high | Pack schemas, registry compile, SecureX/lockfile enforcement. | WORKSTREAM-06 | INFERENCE |

## 10. Verification Queue

| id | item | why_verification_needed | suggested_source_type | priority | related_workstreams | label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Repository git state and commit history. | Transcript reports branch clean/ahead by 10 commits, but not independently verified. | git status/log | P0 | WORKSTREAM-02, WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | XStack canonical entrypoint(s). | Older gate.py and newer tools/xstack/run may coexist. | Inspect docs/scripts and run commands. | P0 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Run-meta / docs/audit tracking policy. | Potential contradiction between run-meta isolation and committed audit artifacts. | .gitignore, git ls-files, derived artifact contract. | P1 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Runtime can build/run without tools/xstack. | XStack removability is a hard user requirement. | Run removability test or temp copy build without tools/xstack. | P1 | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Prompt 1–13 deliverable checklist against repo files. | User said they are not sure what was actually done. | File inventory and test execution. | P0 | WORKSTREAM-03 | FACT |
| VERIFY-06 | tools/xstack/run fast passes from clean checkout. | Reported pass; must verify current state. | Command execution. | P0 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Canon/glossary/AGENTS consistency. | Multiple docs and old/new canon sources may overlap. | Doc scan and RepoX/AuditX. | P1 | WORKSTREAM-01, WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-08 | Deterministic dist build and launcher composite hash. | Prompt 13 reports reproducibility; must verify if needed. | tools/setup/build and tools/launcher/launch. | P1 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Reported hashes match actual outputs. | Hashes are key milestone evidence. | Run compile/build and compare outputs. | P2 | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | README/front-door docs quality. | User wanted industry-standard docs; may not yet exist or be final. | Manual doc review. | P2 | WORKSTREAM-04 | UNCERTAIN / UNVERIFIED |
| VERIFY-11 | Deprecated terms scan. | No mode flags is critical. | RepoX/rg scan. | P1 | WORKSTREAM-01, WORKSTREAM-05 | FACT |
| VERIFY-12 | Survival scope not accidentally implemented or misrepresented. | 13 prompts intentionally avoided survival/crafting/economy. | File/content scan. | P2 | WORKSTREAM-05 | INFERENCE |
| VERIFY-13 | Future realism remains pack/extensibility doctrine, not hardcoded code. | Prevent premature domain implementation. | Architecture/pack review. | P3 | WORKSTREAM-06 | INFERENCE |

## 11. Timeline Register

| sequence | event | changed | why | relevance | confidence |
| --- | --- | --- | --- | --- | --- |
| 1 | Initial Dominium planning and mega prompts | Discussed settings, UI, worldgen, session flow, gameplay readiness. | Established project scope and architecture. | Background; many concepts fed later canon. | 4 |
| 2 | Repeated Codex gate failures and user frustration | User demanded autonomous remediation and no more halt-on-gate behavior. | Drove UAEP, ControlX, gate/XStack hardening. | Still central to agent behavior. | 5 |
| 3 | UAEP / prompt firewall concept | Prompts treated as untrusted; mechanical failures remediated. | Needed for bad queued prompts. | Future prompt design. | 5 |
| 4 | XStack systems planned | RepoX/TestX/AuditX/ControlX/PerformX/CompatX/SecureX roles defined. | Created modular governance suite. | XStack remains key. | 5 |
| 5 | Gate throughput crisis | Gate.py optimized toward fast/cached profiles. | Prompt queue spent hours in gates. | Performance doctrine. | 5 |
| 6 | Run-meta isolation/removability/final hardening | XStack production hardened, snapshot mode and removability established. | Make governance set-and-forget. | Must not regress. | 5 |
| 7 | Glossary/dictionary work | Normative definitions, deprecated/reserved terms drafted. | Prevent conceptual drift. | Docs/canon audit. | 4 |
| 8 | User requested maximum-fidelity Context Transfer Packet | Previous assistant produced CTP with registers and handoff. | Prepare new chat continuity. | Source for this report. | 5 |
| 9 | User pasted/attached transcript of a new 13-prompt run | New Lab Galaxy substrate reported implemented and committed. | Need to ensure completion/accuracy/consistency. | Immediate audit target. | 5 |
| 10 | 13-prompt run summary | Reported canonical docs, schemas, packs, registry compile, XStack runner, session boot, observation, lab navigation, astronomy, UI, ROI, SRZ, packaging. | Potential milestone completion. | Must verify. | 4 |
| 11 | Thematic commits | Agent created 10 commits and reported branch clean/ahead. | Organized work into reviewable history. | Need verify/push state. | 4 |
| 12 | Current package request | User asked to turn CTP into downloadable report package. | Archive old chat for future aggregation/spec book. | This package. | 5 |

## 12. Spec Book Contribution Register

| ID | Contribution | Target section | Status | Label |
|---|---|---|---|---|
| SPEC-01 | Constitutional architecture and glossary doctrine | Architecture / Canon | Candidate | FACT |
| SPEC-02 | XStack governance and agentic development doctrine | Tooling / Governance | Candidate | FACT |
| SPEC-03 | Lab Galaxy deterministic substrate | Milestones / Lab Build | Candidate after verification | FACT |
| SPEC-04 | Survival diegetic-only doctrine | Gameplay / UX | Future candidate | FACT |
| SPEC-05 | Realism as domain packs and solver tiers | Extensibility / Domains | Candidate | INFERENCE |
