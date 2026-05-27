# Structured Registers — AIDE_XStack_Dominium_Refactor_Control_Plane

## 17. Workstream Register

| ID | Name | Objective | Current state | Desired end state | Status | Priority | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WORKSTREAM-01 | Personal AI development workflow | Use ChatGPT/Codex/API/local tools efficiently without manual prompt relay | Conceptual recommendations established | ChatGPT plans/reviews; Codex implements; AIDE standardizes repo context | Active background | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-02 | Harness engineering doctrine | Shift from prompt tricks to environment/tool/context/evidence design | Doctrine accepted and reused | Harness quality becomes default design lens | Active | P0 | 5 | FACT |
| WORKSTREAM-03 | XStack scope and future | Prevent XStack from becoming universal product mythology | Decision made: XStack stays Dominium strict profile | XStack logic wrapped/recycled behind AIDE and retired as public ontology over time | Active | P0 | 5 | FACT |
| WORKSTREAM-04 | AIDE product definition | Define AIDE as portable repo-native operating layer | Evolved from broad app/runtime vision to Profiles+Harness+Compatibility+Bridge first | AIDE Lite Stable Control Plane then future Runtime/Hosts only if justified | Active | P0 | 5 | FACT |
| WORKSTREAM-05 | AIDE self-hosting and bootstrap | Make AIDE manage AIDE and bootstrap repos from small seed/import/template/bundle | Plan accepted; AIDE repo already has .aide profile/harness artifacts | AIDE can install/repair/upgrade/rollback safely and self-host | Active | P0 | 4 | FACT/INFERENCE |
| WORKSTREAM-06 | Dominium repo convergence and cleanup | Make Dominium structurally stable, build-proven, and playable | CONVERGE and POST-CONVERGE improved authority/build; CTest still not clean | Boring durable root layout, root exceptions retired, product/playtest proof achieved | Active | P0 | 5 | FACT |
| WORKSTREAM-07 | Topology authority and root recycling | Make structure self-enforcing and refactors reversible | Concept defined; next tasks AIDE-STRUCTURE/ROOT waves | AIDE inventories/classifies/migrates roots via salvage/move maps and ledgers | Active | P0 | 5 | FACT/INFERENCE |
| WORKSTREAM-08 | Existing tool absorption | Recycle XStack/AuditX/RepoX/TestX tools behind AIDE adapters | Plan accepted; not fully implemented | Useful checks survive under boring tools/aide/audit/repo/test homes | Active | P0 | 5 | FACT/INFERENCE |
| WORKSTREAM-09 | Versioning/release/capabilities | Separate release identity, compatibility truth, and provenance | Layered model accepted; schema specs pending | Capability contracts drive compatibility; versions identify releases; GBN/BII identify builds | Active | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-10 | Git workflow and WorkUnit recovery | Create branch/commit/resumption discipline for humans and agents | Plan accepted from AIDE discussion; implementation Q27-Q35 | AIDE detects branch roles, enforces structured commits, safe land/promote/prune | Active | P1 | 4 | FACT/INFERENCE |
| WORKSTREAM-11 | External project research | Mine Codex/Claude/OMX/claw-code/Graphify/claude-mem etc. for patterns | Several projects assessed; use as reference not foundation | AIDE borrows patterns while keeping canonical contracts provider-neutral | Ongoing | P2 | 4 | FACT/INFERENCE |
| WORKSTREAM-12 | Knowledge preservation and handoff | Preserve this long chat as future reference/spec input | Multiple canvas docs created; this package generated now | Downloadable package supports future aggregation and new chat bootstrap | Active | P0 | 4 | FACT |

## 18. Decision Register

| ID | Decision | Status | Evidence / basis | Rationale | Implications | Related workstream | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| DECISION-01 | Use harness engineering as central frame | Accepted | Repeatedly adopted by user | Models/prompts alone do not solve reliability; environment/contracts/evidence do | Shapes all future design | WORKSTREAM-02 | 5 | FACT |
| DECISION-02 | Keep ChatGPT/Codex roles distinct | Accepted | Early workflow discussion | ChatGPT for architecture/spec/review; Codex for repo-local implementation | Reduces manual prompt relay and drift | WORKSTREAM-01 | 4 | INFERENCE |
| DECISION-03 | XStack remains Dominium-specific strict profile | Accepted | Multiple user confirmations | XStack grew from Dominium and carries local law; universalizing it causes bloat | AIDE becomes public layer; XStack is bridge/profile | WORKSTREAM-03 | 5 | FACT |
| DECISION-04 | AIDE becomes new portable repo-native operating layer | Accepted | User named AIDE and accepted split | New clean identity avoids XStack baggage | AIDE repo owns portable profiles/harness/compatibility | WORKSTREAM-04 | 5 | FACT |
| DECISION-05 | AIDE v0 is Profiles + Harness + Compatibility + Dominium Bridge, not full runtime | Accepted | Repeated later synthesis | Existing tools already provide runtimes; missing layer is portable repo contract | Runtime/Hosts deferred | WORKSTREAM-04 | 5 | FACT |
| DECISION-06 | Profile and Harness are distinct | Accepted | AIDE discussion quoted and affirmed | Declarative truth and executable machinery must not blur | AIDE architecture uses Contract/Profile vs Harness split | WORKSTREAM-04 | 5 | FACT |
| DECISION-07 | AIDE must self-host from a small seed, not zero magic | Accepted | User supplied bootstrapping synthesis | Honest bootstrap requires repo kind/commands/policy seed | AIDE repo should manage itself through .aide | WORKSTREAM-05 | 4 | FACT |
| DECISION-08 | Use AIDE in Dominium as subordinate pack/control layer first | Accepted | Dominium/AIDE integration discussion | Dominium AGENTS/XStack authority must not be overwritten | AIDE imports must preserve local doctrine | WORKSTREAM-06 | 5 | FACT |
| DECISION-09 | Do not delete XStack checks; wrap/classify/migrate/retire | Accepted | Latest synthesis | Old names are bad, checks are valuable | AIDE absorbs old tools by adapters and inventories | WORKSTREAM-08 | 5 | FACT |
| DECISION-10 | Dominium cleanup must be file-by-file root recycling, not wholesale moves | Accepted | User supplied root recycling plan and asked for synthesis | Mixed roots contain source/docs/policy/tests/generated/history | Requires inventory, salvage maps, move maps, ledgers | WORKSTREAM-07 | 5 | FACT |
| DECISION-11 | Do not start broad feature work until build/CTest/product/projection proof is acceptable | Accepted | Post-CONVERGE planning | Feature expansion amplifies disorder while proof gaps remain | Domain/worldgen/render/etc. deferred | WORKSTREAM-06 | 5 | FACT |
| DECISION-12 | Use versions for release identity, capabilities/contracts for compatibility, GBN/BII for provenance | Accepted as strong refinement | Versioning discussion | Multi-dimensional compatibility cannot be encoded in one version string | Capability contract specs needed | WORKSTREAM-09 | 4 | FACT/INFERENCE |
| DECISION-13 | Use dev as integration branch, not source of truth | Accepted from AIDE Git plan | Multi-machine/agent work needs shareable integration branch | main remains accepted canonical truth | AIDE Git policy uses main/dev/task/release roles | WORKSTREAM-10 | 4 | FACT/INFERENCE |
| DECISION-14 | Structured commits and WorkUnit recovery should become AIDE policy | Accepted | Eureka/AIDE Git workflow discussion | Future automation needs task IDs, branch roles, evidence, trailers | Q27-Q35 plan | WORKSTREAM-10 | 4 | FACT/INFERENCE |
| DECISION-15 | External leak-derived projects are research inputs, not foundations | Accepted | Claude Code/Graphify/OMX discussions | Legal/supply-chain risk and vendor-specific semantics | Borrow patterns; do not transplant code | WORKSTREAM-11 | 5 | FACT/INFERENCE |
| DECISION-16 | Graphify-like tools are optional analysis backends, not canon | Accepted | Graphify discussion | Graph outputs are derived and may be noisy/stale | AIDE may benchmark/use as adapter later | WORKSTREAM-11 | 4 | FACT/INFERENCE |
| DECISION-17 | AIDE must support template, managed product, and release bundle adoption | Accepted | Bootstrap/release discussion | Different repos need different adoption modes | AIDE install/repair/upgrade/rollback plans required | WORKSTREAM-05 | 4 | FACT |
| DECISION-18 | Generated outputs are evidence unless promoted | Accepted | Dominium AGENTS/AIDE generated artifacts discussions | Prevents generated files from competing with canon | AIDE managed sections subordinate to source-of-truth | WORKSTREAM-04 | 5 | FACT |
| DECISION-19 | Use documentation/contract first before runtime/app/extension expansion | Accepted | Repeated throughout | Avoids overbuilding and premature abstraction | Q36-Q57 prior to Gateway/Hosts | WORKSTREAM-04 | 5 | FACT |
| DECISION-20 | This chat should be preserved as a high-fidelity handoff package | Accepted by current user request | User requested downloadable package | Creates persistent artifact for future aggregation | Package files become carry-forward artifacts | WORKSTREAM-12 | 5 | FACT |

## 19. Task Register

| ID | Task | Priority | Urgency | Owner | Dependencies | Inputs needed | Expected output | Next step | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TASK-01 | Run or finish Q35 GitHub Protection and CI Advisory in AIDE | P0 | U0 | AIDE repo/Codex | Q27-Q34 governance wave | Current AIDE repo | Advisory branch protection/CI files, no GitHub mutation | Then QCHECK-03 | WORKSTREAM-10 | FACT |
| TASK-02 | Run QCHECK-03 Governance/Git/Release Readiness Audit | P0 | U0 | AIDE repo/Codex | Q35 complete | AIDE Q27-Q35 artifacts | PASS/PASS_WITH_WARNINGS/FAIL decision | If pass, Q36; if fail, QFIX-GOV | WORKSTREAM-10 | FACT |
| TASK-03 | Implement Q36 Intent Compiler + WorkUnit Sizing v0 | P0 | U1 | AIDE repo | QCHECK-03 acceptable | AIDE policies/intake plan | Vague prompt -> bounded WorkUnit draft | Then Q37 | WORKSTREAM-04 | FACT |
| TASK-04 | Implement Q37 Repo Intelligence Index v0 | P0 | U1 | AIDE repo | Q36 | Repo files and policies | file/ownership/dependency/test/doc maps | Then Q38 | WORKSTREAM-04 | FACT |
| TASK-05 | Implement Q38 File Quality Ledger v0 | P1 | U1 | AIDE repo | Q37 | Repo intelligence maps | Quality ledger/report for files/modules/docs/tests | Then Q39 | WORKSTREAM-04 | FACT |
| TASK-06 | Implement Q39 Refactor Control Plane v0 | P0 | U1 | AIDE repo | Q38 | AIDE refactor requirements | refactor/migration schemas and dry-run validation | Then Q40 | WORKSTREAM-07 | FACT |
| TASK-07 | Implement Q40 Root Recycling Framework v0 | P0 | U1 | AIDE repo | Q39 | Root recycling plan | Root inventory/classification/plan schema and commands | Then Q41 | WORKSTREAM-07 | FACT |
| TASK-08 | Implement Q41 Existing Tool Absorption v0 | P0 | U1 | AIDE repo | Q40 | Tool absorption plan | Tool inventory and wrapper plan model | Then Q42 | WORKSTREAM-08 | FACT |
| TASK-09 | Implement Q42 move/salvage/path-alias model | P0 | U1 | AIDE repo | Q39-Q41 | Refactor schemas | Dry-run map mechanics, ledger format | Then install/upgrade phase | WORKSTREAM-07 | FACT |
| TASK-10 | Implement Q43-Q48 install/repair/upgrade/rollback/release bundle planning | P1 | U2 | AIDE repo | Q42 | AIDE pack model | Stable AIDE Lite release bundle and GitHub draft files | Then Dominium preflight | WORKSTREAM-05 | FACT |
| TASK-11 | Run Q49 Dominium Fresh Install Preflight | P0 | U2 | Dominium via AIDE | Stable AIDE pack exists | Dominium repo state | Preflight report before AIDE upgrade/install | Then Q50 | WORKSTREAM-06 | FACT |
| TASK-12 | Run Q50 Dominium Fresh Install/Upgrade from Stable Pack | P0 | U2 | Dominium via AIDE | Q49 pass/warnings classified | Stable pack and Dominium doctrine | AIDE installed/upgraded preserving Dominium truth | Then Q51 | WORKSTREAM-06 | FACT |
| TASK-13 | Run Q51 Dominium Existing Tool Absorption | P0 | U2 | Dominium via AIDE | Q50 | XStack/AuditX/RepoX/TestX/tools | Tool inventory and adapter map | Then Q52 | WORKSTREAM-08 | FACT |
| TASK-14 | Run Q52 Dominium Root Recycling Pilot | P0 | U2 | Dominium via AIDE | Q51 | Root recycling framework | Inventory/salvage plans for safer roots | Then Q53 | WORKSTREAM-07 | FACT |
| TASK-15 | Run Q53 Dominium Operating Baseline | P0 | U2 | Dominium via AIDE | Q49-Q52 | AIDE/Dominium reports | Dominium ready to use AIDE for structured work | Then root waves | WORKSTREAM-06 | FACT |
| TASK-16 | Remediate/classify invariant_units_present | P0 | U0 | Dominium main chat/Codex | POST-CONVERGE-10E | CTest output and unit registry | Clean or accepted blocker | Then inv_repox_rules | WORKSTREAM-06 | FACT |
| TASK-17 | Remediate/classify inv_repox_rules and remaining RepoX drift | P0 | U0 | Dominium main chat/Codex | TASK-16 or parallel if scoped | RepoX/CTest output | Clean or classified warning | Then POST-CONVERGE-11 decision | WORKSTREAM-06 | FACT |
| TASK-18 | Decide if POST-CONVERGE-11 can proceed with CTest-warning status | P0 | U1 | User/Dominium chat | TASK-16-17 evidence | Build/CTest blocker reports | Explicit proceed/block decision | Product boot proof or more remediation | WORKSTREAM-06 | FACT |
| TASK-19 | Fix/classify setup Python bridge, dist/bin/dom, server CLI forwarding blockers | P1 | U1 | Dominium/Codex | Build proof available | POST_CONVERGE_NEXT_STEPS and validators | Command surface proof improvements | Then product/projection proof | WORKSTREAM-06 | FACT |
| TASK-20 | Prove portable projection assembly path | P1 | U2 | Dominium/Codex | TASK-19; native binaries | Distribution contracts | Manifests and portable roots proof | Then release lane | WORKSTREAM-06 | FACT |
| TASK-21 | Create AIDE-STRUCTURE-00 in Dominium | P0 | U1 | Dominium/Codex | CTest blockers understood/classified | Root constitution plan | Repo Constitution and Refactorability Framework | Then tooling inventory | WORKSTREAM-07 | FACT |
| TASK-22 | Create AIDE-STRUCTURE-01 Existing Tool Recycling Inventory | P0 | U1 | Dominium/Codex | AIDE-STRUCTURE-00 | Existing tools dirs | Tool recycling inventory docs/json | Then wrap before rename | WORKSTREAM-08 | FACT |
| TASK-23 | Create AIDE-STRUCTURE-02 Wrap Before Rename | P0 | U1 | Dominium/Codex | AIDE-STRUCTURE-01 | Tool inventory | tools/aide/run_task wrappers to old tools | Then rename/migrate later | WORKSTREAM-08 | FACT |
| TASK-24 | Create AIDE-ROOT-00 Root Recycling Framework | P0 | U1 | Dominium/Codex | AIDE wrappers exist | Root recycling plan | Schemas/tools/ledgers/reports, no moves | Then root inventories | WORKSTREAM-07 | FACT |
| TASK-25 | Run AIDE-ROOT-01 safe root inventory | P1 | U2 | Dominium/Codex | AIDE-ROOT-00 | governance/meta/validation/performance/ide roots | Inventory and recycling plans | Then wrappers/tools inventory | WORKSTREAM-07 | FACT |
| TASK-26 | Run AIDE-ROOT-02 wrappers/tools inventory | P1 | U2 | Dominium/Codex | AIDE-ROOT-00 | root wrappers and obvious tools | Inventory/salvage plans | Then content roots | WORKSTREAM-07 | FACT |
| TASK-27 | Run AIDE-ROOT-03 content/package/profile inventory | P1 | U2 | Dominium/Codex | Manifest/path identity rules | data/packs/profiles/bundles/modding/models/templates | Inventory/salvage plans | Then contract/security roots | WORKSTREAM-07 | FACT |
| TASK-28 | Run AIDE-ROOT-04 contract/security/spec/update inventory | P1 | U2 | Dominium/Codex | AIDE-ROOT-00 | compat/locks/repo/safety/security/specs/updates | Inventory/salvage plans | Then high-risk roots | WORKSTREAM-07 | FACT |
| TASK-29 | Run AIDE-ROOT-05 core/control/net inventory | P1 | U3 | Dominium/Codex | Build/CTest stable enough | core/control/net | High-risk inventory/salvage plans | Then libs inventory | WORKSTREAM-07 | FACT |
| TASK-30 | Run AIDE-ROOT-06 lib/libs inventory | P1 | U3 | Dominium/Codex | Build/CTest stable enough | lib/libs | ABI/build-sensitive inventory | Then move waves | WORKSTREAM-07 | FACT |
| TASK-31 | Apply AIDE-MOVE-01..07 waves only after maps exist | P1 | U3 | Dominium/Codex | Root inventories/salvage maps | Move maps and validators | Root exceptions retired or narrowed | Then product/release proof | WORKSTREAM-07 | FACT |
| TASK-32 | Run POST-CONVERGE-11 product boot proof | P0 | U2 | Dominium/Codex | Build/test acceptable | Native binaries | Command/status/save/load/shutdown proof | Then projection proof | WORKSTREAM-06 | FACT |
| TASK-33 | Run POST-CONVERGE-12 portable projection proof | P0 | U2 | Dominium/Codex | Product boot proof | Release/distribution contracts | Portable projection manifests/root proof | Then RELEASE-00 | WORKSTREAM-06 | FACT |
| TASK-34 | Create RELEASE-00 first test release lane | P1 | U3 | Dominium/Codex | Product/projection proof | Binaries/manifests/release docs | Test release lane proof | Then feature work | WORKSTREAM-06 | FACT |
| TASK-35 | Preserve this package and feed future aggregation | P0 | U0 | User/future assistant | This generated zip | Files in package | Master spec book input | Use future bootstrap prompt | WORKSTREAM-12 | FACT |

## 20. Constraint Register

| ID | Constraint | Type | Hard/soft | Source / basis | Practical implication | Violation risk | Confidence | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CONSTRAINT-01 | Do not overwrite Dominium AGENTS/XStack authority with AIDE-generated guidance | authority | hard | Dominium AGENTS and repeated decision | AIDE must be subordinate in Dominium until bridge/profile migration | Competing governance canon | 5 | FACT |
| CONSTRAINT-02 | Do not delete old XStack/AuditX/RepoX/TestX checks before wrapping/classifying them | migration | hard | Latest synthesis | Existing validation value must be preserved | Loss of drift detection | 5 | FACT |
| CONSTRAINT-03 | No wholesale moves of mixed roots | repo-structure | hard | Root recycling doctrine | Inventory/classify per file before moving | Broken build/semantic demotion | 5 | FACT |
| CONSTRAINT-04 | No feature expansion before build/CTest/product/projection proof is acceptable | sequencing | hard | Post-CONVERGE planning | Worldgen/render/native/civilization work waits | Amplifies disorder | 5 | FACT |
| CONSTRAINT-05 | AIDE Runtime/Gateway/Hosts are deferred | scope | hard for now | AIDE plan | Focus on Profiles/Harness/Compatibility/Bridge and stable control plane | Scope creep | 5 | FACT |
| CONSTRAINT-06 | Generated outputs are not canon unless explicitly promoted | authority | hard | AIDE and Dominium decisions | Generated manifests/sections are evidence or projections | Silent authority inversion | 5 | FACT |
| CONSTRAINT-07 | AIDE updates are additive and compatibility-preserving by default | upgrade | hard | Q35-Q57 plan | Migration only mandatory/dry-run/evidenced/reversible/gated | Target data loss | 4 | FACT |
| CONSTRAINT-08 | Target repo truth wins over AIDE source pack defaults | install | hard | AIDE install plan | Preserve target memory/doctrine/tools | Pack overwrites local canon | 4 | FACT |
| CONSTRAINT-09 | Use repo state over chat memory | workflow | hard | Multiple decisions and user preference | Task recovery/checks read repo artifacts first | Redoing/duplicating stale work | 5 | FACT |
| CONSTRAINT-10 | Every root recycling move requires evidence, validators, rollback notes, and ledger entries | migration | hard | Root recycling plan | Moves are reversible and auditable | Irreversible cleanup errors | 5 | FACT |
| CONSTRAINT-11 | Capabilities/contracts determine compatibility; versions identify releases | compatibility | soft-to-hard after spec | Version/capability discussion | Avoid version-only compatibility assumptions | Misload plugins/packs/saves | 4 | INFERENCE |
| CONSTRAINT-12 | Use small issue-sized Codex tasks for implementation; large prompts only for audit/planning | workflow | soft/hard practice | Codex use discussion | Reduce overreach and prompt drift | Bad diffs/large rewrites | 4 | INFERENCE |
| CONSTRAINT-13 | No leak-derived code as foundation | legal/safety | hard | Leak discussions and resource guide | Use patterns only; avoid contamination | Legal/supply-chain risk | 5 | FACT |
| CONSTRAINT-14 | Expired uploads cannot be treated as fully re-inspected | evidence | hard | Current file_search notice | Use visible transcript and live repo checks; mark gaps | False precision | 5 | FACT |
| CONSTRAINT-15 | Future assistants must preserve uncertainty labels | reporting | hard | User preservation prompt | Avoid turning suggestions into decisions | Bad aggregation | 5 | FACT |

## 21. User Preference Register

| ID | Preference | Area | Explicit/inferred/uncertain | Strength | Practical implication | Risk if wrong | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| PREF-01 | Direct, source-grounded, audit-ready answers | communication | explicit | high | Use facts/inferences/uncertainty, cite when current or specific | Loss of trust | FACT |
| PREF-02 | Detailed knowledge-base summaries for long chats | artifact | explicit | high | Produce human-readable and machine-aggregatable packages | Lost context | FACT |
| PREF-03 | Do not ask for unnecessary confirmation; proceed with best effort | workflow | explicit from project/user style | high | Only ask when materially blocked | Stalling | FACT |
| PREF-04 | Prefer structured markdown and clear headings | format | explicit/inferred | high | Use sections, tables where helpful | Hard to reuse | FACT/INFERENCE |
| PREF-05 | Do not over-compress important decisions and rationale | summary | explicit | high | Preserve decisions, alternatives, rejected paths | Spec loss | FACT |
| PREF-06 | Correct framing when evidence disagrees | epistemic | explicit | high | Do not just validate user assumptions | Bad strategy | FACT |
| PREF-07 | Current facts should be verified when possible | factuality | explicit | high | Use GitHub/web/current docs for live repo/tool state | Stale claims | FACT |
| PREF-08 | Separate Dominium work from AIDE work | project management | explicit | high | Main chat handles Dominium; AIDE repo handles AIDE | Cross-contamination | FACT |
| PREF-09 | Preserve both human-readable and machine-readable artifacts | artifact | explicit | high | Create report, spec sheet, registers, aggregator packet | Poor future aggregation | FACT |
| PREF-10 | Bias toward anti-complexity and incremental proof | engineering | inferred/accepted | high | Avoid big-bang rewrites and speculative platformization | Project mess worsens | INFERENCE |

## 22. Open Questions Register

| ID | Question / issue | Why it matters | Known information | Unknown information | Resolution path | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QUESTION-01 | Will POST-CONVERGE-10F fully resolve invariant_units_present and inv_repox_rules? | Determines whether product boot proof can proceed | 10E classified blockers | Exact fix/acceptance not yet verified | Run targeted remediation and CTest | P0 | WORKSTREAM-06 | UNVERIFIED |
| QUESTION-02 | When should Dominium accept CTest-warning status for POST-CONVERGE-11? | Could unblock product boot proof without pretending clean CTest | CTest currently blocked by governance drift and wall-time | User/repo policy acceptance threshold | Formal review decision | P0 | WORKSTREAM-06 | UNCERTAIN |
| QUESTION-03 | What exact AIDE pack version should Dominium import? | Avoids importing unreviewed/local AIDE code | AIDE Q35-Q57 plan exists; live state may lag | Final release/tag/pack boundary | Use stable bundle after Q47/Q50 path | P0 | WORKSTREAM-05 | UNVERIFIED |
| QUESTION-04 | What is minimal stable .aide schema for v0? | Affects install/export compatibility | Current .aide profile exists; Q36-Q47 expand it | Exact final schema | AIDE Q36-Q48 | P0 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-05 | Which downstream generated targets are v0 mandatory? | Avoids overgeneration | AGENTS and .agents skills already managed in AIDE; Claude preview/deferred | Final v0 target list | AIDE Q35-Q48 decisions | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-06 | How strict should AIDE validation be in dev vs CI? | Controls adoption friction | Need warning/error/hard-gate classes | Severity model | QCHECK-03 and Q36-Q48 | P1 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-07 | Which root families should be moved first after inventory? | Prevents risky cleanup | Safe groups identified; moves still pending | Inventory findings | AIDE-ROOT-01..06 outputs | P1 | WORKSTREAM-07 | UNCERTAIN |
| QUESTION-08 | Which XStack tools should be adapted vs archived vs dropped? | Determines tool migration plan | Plan says inventory/classify all | File-level tool inventory | AIDE-STRUCTURE-01 | P0 | WORKSTREAM-08 | UNCERTAIN |
| QUESTION-09 | When does AIDE Runtime become necessary? | Avoids premature build of runtime | Current plan says later after QCHECK-04 | Whether Profiles/Harness solve enough | QCHECK-04 | P2 | WORKSTREAM-04 | UNCERTAIN |
| QUESTION-10 | What is final branch protection policy for public repos? | Git/GitHub governance | Plan says generate advisories only | Exact applied protection rules | Q35 + user approval | P1 | WORKSTREAM-10 | UNCERTAIN |
| QUESTION-11 | What compatibility guarantees will AIDE make? | Affects upgrade/migration trust | Additive default accepted | Concrete SemVer/capability/support policy | Q45/Q47 specs | P1 | WORKSTREAM-09 | UNCERTAIN |
| QUESTION-12 | Which Graphify/graph-memory features are worth adopting? | Potential context benefit | Graphify optional backend only | Measured usefulness | Bakeoff experiments | P3 | WORKSTREAM-11 | UNVERIFIED |
| QUESTION-13 | How much of expired uploaded file content should be reuploaded for complete audit? | Package completeness | Some uploads expired | Whether user wants exact raw re-analysis | User reupload if needed | P2 | WORKSTREAM-12 | UNCERTAIN |
| QUESTION-14 | How should Dominium content identity be made path-independent before moving packs/profiles/data? | Critical for content roots | Rule established: identity by manifest, not path | Exact validators/manifests | AIDE-ROOT-03 | P0 | WORKSTREAM-07 | UNCERTAIN |
| QUESTION-15 | What is the final test release lane definition? | Required before feature work | Release lane deferred until product/projection proof | Release criteria and assets | RELEASE-00 | P1 | WORKSTREAM-06 | UNCERTAIN |

## 23. Artifact Ledger

| ID | Artifact / file / prompt / output | Type | Purpose | Status | Origin | Carry forward? | Notes | Label |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ARTIFACT-01 | AIDE Spinout Pack v0.1 | canvas document | Initial AIDE split charter | created earlier in chat | assistant-generated | yes | Defined XStack as Dominium profile and AIDE as portable system | FACT |
| ARTIFACT-02 | XStack and AIDE Knowledge Base Snapshot 2026-04-06 | canvas document | Early consolidated KB | created earlier | assistant-generated | yes | Captured initial XStack/AIDE split before later changes | FACT |
| ARTIFACT-03 | Dominium Main Chat Handoff — XStack, AIDE, and Repo Authority | canvas document | Handoff to main development chat | created earlier | assistant-generated | yes | Aligned repo normalization, XStack narrowing, AIDE extraction | FACT |
| ARTIFACT-04 | AIDE and Dominium Ultimate Synthesis 2026-05-13 | canvas document | Latest synthesis before current package | updated in chat | assistant-generated | yes | Now includes POST-CONVERGE-10E and Q35-Q57 plan | FACT |
| ARTIFACT-05 | Pasted text.txt | uploaded file | Prompt requesting full preservation package | available now | user-uploaded | yes | Current package follows this prompt; earlier uploads expired | FACT |
| ARTIFACT-06 | The Grug Brained Developer.pdf | uploaded/expired | Anti-complexity design filter | expired now | user-uploaded | yes if reuploaded | Visible transcript discussed its lessons; exact raw file unavailable now | FACT/UNVERIFIED |
| ARTIFACT-07 | Claude_Code_Leak_Resource_Guide.pdf | uploaded/expired | Leak research map/safety warnings | expired now | user-uploaded | yes if reuploaded | Visible transcript discussed read-only/supply-chain caveats | FACT/UNVERIFIED |
| ARTIFACT-08 | Claude Code leak mirrors zips | uploaded/expired | Pattern research around agent harnesses | expired now | user-uploaded | maybe | Use only as pattern evidence; do not run | FACT/UNVERIFIED |
| ARTIFACT-09 | oh-my-codex-main.zip / claw-code-main.zip | uploaded/expired | Open source harness comparison | expired now | user-uploaded | maybe | OMX useful inspiration; claw-code research only | FACT/UNVERIFIED |
| ARTIFACT-10 | Live AIDE README.md | GitHub fetched file | Current AIDE repo state | verified in chat | GitHub connector | yes | Cited in final package | FACT |
| ARTIFACT-11 | Live AIDE .aide/profile.yaml | GitHub fetched file | AIDE profile/current focus | verified | GitHub connector | yes | Shows deferred runtime/hosts | FACT |
| ARTIFACT-12 | Live AIDE Harness files | GitHub fetched files | Harness command surface and AIDE Lite details | verified | GitHub connector | yes | scripts/aide, aide_harness.py, aide_lite.py | FACT |
| ARTIFACT-13 | Live Dominium README.md | GitHub fetched file | Dominium identity/governance overview | verified | GitHub connector | yes | Shows RepoX/TestX/AuditX/XStack governance | FACT |
| ARTIFACT-14 | Live Dominium AGENTS.md | GitHub fetched file | Canonical Dominium agent governance | verified | GitHub connector | yes | Authority and protected areas; AIDE must not override | FACT |
| ARTIFACT-15 | Live Dominium POST_CONVERGE_NEXT_STEPS.md | GitHub fetched file | Current post-CONVERGE priority state | verified | GitHub connector | yes | Shows 10E status and current priority order | FACT |
| ARTIFACT-16 | Dominium commit 0f842... | GitHub commit | POST-CONVERGE-10D build/UI bind proof | verified | GitHub connector | yes | Earlier state; superseded in part by 10E | FACT |
| ARTIFACT-17 | Dominium commit 06d383... | GitHub commit search result | POST-CONVERGE-10E CTest/AuditX remediation | verified via commit search | GitHub connector | yes | Latest relevant current state | FACT |
| ARTIFACT-18 | Generated package files | zip contents | This preservation package | created now | assistant-generated | yes | Downloadable ZIP in /mnt/data | FACT |
| ARTIFACT-19 | Future chat bootstrap prompt | markdown file | Resume in new chat | created now | assistant-generated | yes | Contains placeholder for context transfer packet | FACT |
| ARTIFACT-20 | Spec sheet YAML | yaml file | Machine-assisted aggregation | created now | assistant-generated | yes | Secondary to human report | FACT |

## 24. Rejected / Superseded Options Register

| ID | Option | Status | Reason | Final or tentative? | Reconsider conditions | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REJECTED-01 | Build AIDE as full coding agent first | deprioritized | Existing tools already provide runtimes; missing wedge is portable repo contract | tentative but strong | If current tools cannot be harnessed or profiles fail | WORKSTREAM-04 | FACT |
| REJECTED-02 | Make XStack universal public abstraction | rejected | XStack is Dominium-shaped and bloated for general public model | strong | If AIDE fails and XStack proves portable with minimal change | WORKSTREAM-03 | FACT |
| REJECTED-03 | Delete XStack/AuditX/RepoX/TestX outright | rejected | Checks are valuable; names/locations are problem | strong | Only after all logic migrated or proven obsolete | WORKSTREAM-08 | FACT |
| REJECTED-04 | Move bad roots wholesale | rejected | Roots are mixed strata; wholesale moves break semantics/build | strong | Only if root is proven pure by inventory | WORKSTREAM-07 | FACT |
| REJECTED-05 | Start Dominium feature systems now | deferred | Build/CTest/product/projection proof incomplete | strong temporary | After RELEASE-00/test release proof | WORKSTREAM-06 | FACT |
| REJECTED-06 | Use Graphify as canonical AIDE memory layer | rejected | Graph outputs are derived and tool is young/optional | strong | If graph backend becomes evaluated and provenance-aware | WORKSTREAM-11 | FACT/INFERENCE |
| REJECTED-07 | Adopt leak-derived code as base | rejected | Legal/supply-chain/IP contamination and maturity issues | strong | Do not reconsider without clean-room/legal review | WORKSTREAM-11 | FACT |
| REJECTED-08 | Use one version number for all compatibility | rejected | Compatibility is multi-dimensional | strong | None; versions still used for identity | WORKSTREAM-09 | FACT |
| REJECTED-09 | Use dev as second source of truth | rejected | dev should be integration only; main canonical | strong | None unless workflow changes radically | WORKSTREAM-10 | FACT |
| REJECTED-10 | Treat generated outputs as canon | rejected | Dominium/AIDE authority model forbids silent promotion | strong | Only explicit promotion by stronger source | WORKSTREAM-04 | FACT |
| REJECTED-11 | Ask agents to remember better instead of enforcing structure | rejected | Repo must be structurally self-enforcing | strong | None | WORKSTREAM-07 | FACT |
| REJECTED-12 | Do desktop/IDE/app surfaces before harness stability | deferred | Would distract from core product | strong temporary | After QCHECK-04 | WORKSTREAM-04 | FACT |
| REJECTED-13 | Import unreviewed AIDE Q19 into Dominium as canonical | rejected | Need reviewed/pushed/tagged pack boundary | strong | Quarantined branch only if urgent | WORKSTREAM-05 | FACT |
| REJECTED-14 | Put every test/eval at root in future monorepos | rejected in analogous archive advice | Creates ownership ambiguity | context-dependent | System-level tests only at root | WORKSTREAM-07 | INFERENCE |
| REJECTED-15 | Make memory/infinite context the system center | rejected | Tasks/evidence/contracts are center; memory supports them | strong | If memory tools demonstrably become control layer | WORKSTREAM-11 | INFERENCE |

## 25. Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Future assistant treats AIDE as full runtime now | Scope creep and wrong tasks | Medium | High | Repeat pre-product boundary and Q35-Q57 sequence | WORKSTREAM-04 | FACT |
| RISK-02 | Future assistant deletes old XStack checks too early | Loss of validation and drift detection | Medium | High | Wrap before rename; tool absorption inventory | WORKSTREAM-08 | FACT |
| RISK-03 | Root cleanup breaks build or semantics | Build failure / lost policy / content identity bugs | High | High | Inventory/salvage/move maps and validators before moves | WORKSTREAM-07 | FACT |
| RISK-04 | Generated AIDE artifacts compete with Dominium AGENTS canon | Authority conflict | Medium | High | Managed sections subordinate; target truth wins | WORKSTREAM-06 | FACT |
| RISK-05 | Expired uploads create false precision | Unsupported details in report | Medium | Medium | Mark limitations; request reupload for exact audit | WORKSTREAM-12 | FACT |
| RISK-06 | CTest warnings get accepted without explicit review | False green state | Medium | High | Formal blocker acceptance before POST-CONVERGE-11 | WORKSTREAM-06 | INFERENCE |
| RISK-07 | AIDE install overwrites target-specific memory/evidence | Data loss and contamination | Medium | High | Install/upgrade dry-run and ownership ledger | WORKSTREAM-05 | FACT |
| RISK-08 | Dev branch becomes dumping ground | Unstable integration and confusion | Medium | Medium | AIDE branch roles and promotion gates | WORKSTREAM-10 | INFERENCE |
| RISK-09 | Capability flags become string soup | Compatibility model unusable | Medium | Medium | Contract-family registry and schema | WORKSTREAM-09 | INFERENCE |
| RISK-10 | Graph/memory backend treated as canon | Wrong context and bad refactors | Low-Medium | Medium | Derived artifact policy and evaluation | WORKSTREAM-11 | INFERENCE |
| RISK-11 | Big prompts cause broad unintended changes | Messier repo and hard reviews | High | Medium | Intent compiler and WorkUnit sizing | WORKSTREAM-04 | FACT/INFERENCE |
| RISK-12 | Feature work resumes before product/projection proof | Amplifies technical debt | Medium | High | Gate feature work behind proof sequence | WORKSTREAM-06 | FACT |
| RISK-13 | Installer/upgrade logic lacks rollback | Hard-to-repair target repos | Medium | High | Q43-Q48 before wide adoption | WORKSTREAM-05 | FACT |
| RISK-14 | AIDE becomes product architecture rather than repo control plane | Boundary collapse | Medium | High | Keep AIDE under .aide/tools/aide; not engine/game/runtime | WORKSTREAM-04 | FACT |
| RISK-15 | Old chat decisions are merged with other chats without labels | Spec contamination | Medium | Medium | Use aggregator packet and FACT/INFERENCE labels | WORKSTREAM-12 | FACT |
| RISK-16 | Root inventories undercount references | Broken paths after moves | Medium | High | Reference rewrite plus check_no_raw_root_references | WORKSTREAM-07 | INFERENCE |
| RISK-17 | Q35-Q57 plan shifts in AIDE chat before implementation | Package becomes stale | Medium | Medium | Verify live AIDE docs before acting | WORKSTREAM-04 | UNVERIFIED |
| RISK-18 | Dominium content identity remains path-dependent during moves | Packs/profiles invalid or silent drift | Medium | High | Path-independent manifest validators before content moves | WORKSTREAM-07 | INFERENCE |
| RISK-19 | Release/version/capability policy remains prose only | Inconsistent builds and support claims | Medium | Medium | Create machine-readable compatibility schemas | WORKSTREAM-09 | INFERENCE |
| RISK-20 | Canvas docs not exported with future package | Loss of prior summaries | Low | Medium | Include in artifact ledger and package synthesis | WORKSTREAM-12 | FACT |

## 26. Verification Queue

| ID | Item requiring verification | Why verification is needed | Suggested source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Current AIDE Q35/QCHECK-03 implementation state | Planning may have advanced after visible transcript | GitHub AIDE repo files/commits | P0 | WORKSTREAM-04 | UNVERIFIED |
| VERIFY-02 | Current Dominium head after POST-CONVERGE-10E | Remote may have advanced | GitHub commits and POST_CONVERGE_NEXT_STEPS | P0 | WORKSTREAM-06 | FACT/UNVERIFIED |
| VERIFY-03 | Whether invariant_units_present has been fixed | Blocks product proof | CTest output/commit logs | P0 | WORKSTREAM-06 | UNVERIFIED |
| VERIFY-04 | Whether inv_repox_rules has been fixed or accepted | Blocks full CTest/FAST confidence | CTest/RepoX reports | P0 | WORKSTREAM-06 | UNVERIFIED |
| VERIFY-05 | Final AIDE v0 schema and install bundle contents | Needed before Dominium import | AIDE release bundle/Q47 outputs | P0 | WORKSTREAM-05 | UNVERIFIED |
| VERIFY-06 | Which AIDE generated targets are enabled by default | Avoid target overwrite | AIDE manifest/policies | P1 | WORKSTREAM-04 | UNVERIFIED |
| VERIFY-07 | Exact count/current status of Dominium root exceptions | Root cleanup planning | contracts/repo/layout_exceptions.toml and validators | P0 | WORKSTREAM-07 | UNVERIFIED |
| VERIFY-08 | Exact existing XStack/AuditX/RepoX/TestX tool inventory | Tool absorption | Repo scan | P0 | WORKSTREAM-08 | UNVERIFIED |
| VERIFY-09 | Whether expired uploads need reupload | Completeness of preservation | User reupload if desired | P2 | WORKSTREAM-12 | FACT |
| VERIFY-10 | Current official Codex/Claude/OpenHands/Continue project guidance | Tool adapters can change | Official docs/web | P2 | WORKSTREAM-11 | UNVERIFIED |
| VERIFY-11 | Graphify/claude-mem current maturity | Optional backend evaluation | Project repos/docs | P3 | WORKSTREAM-11 | UNVERIFIED |
| VERIFY-12 | GitHub branch protection availability/settings for repos | AIDE Git advisory | GitHub API/repo settings | P1 | WORKSTREAM-10 | UNVERIFIED |
| VERIFY-13 | Actual Dominium product boot command sequence after binaries | Product proof | Local run/CI logs | P0 | WORKSTREAM-06 | UNVERIFIED |
| VERIFY-14 | Portable projection assembly command and manifests | Release proof | Distribution validators/artifacts | P1 | WORKSTREAM-06 | UNVERIFIED |
| VERIFY-15 | Compatibility/capability schema status in Dominium/AIDE | Versioning model implementation | contracts/capabilities or AIDE policies | P2 | WORKSTREAM-09 | UNVERIFIED |

## 27. Chronological Timeline Register

| Sequence | Event / topic | What changed or was decided | Why it mattered | Current relevance | Confidence |
| --- | --- | --- | --- | --- | --- |
| 01 | User asked how to better use Codex Pro, ChatGPT, VS Code, apps, and API | Initial workflow problem framed | Started discussion from practical developer productivity | Background | 5 |
| 02 | We shifted from prompt optimization to harness engineering | Harness became main lens | Explained why environment/tools/evidence matter more than prompt relay | Still central | 5 |
| 03 | Multi-agent stack ideas explored | Repo topology, AGENTS.md, skills, MCP, Responses, hosted shell, evals, merge queues discussed | Led to bounded delegation/evidence/task graph ideas | Background | 5 |
| 04 | XStack metaharness proposals formed | HarnessX/TaskX/BridgeX/PermitX/ContextX etc. explored | Useful but too complex as public model | Superseded/refined | 5 |
| 05 | Simplified AIDE/XStack split emerged | XStack as Dominium profile; AIDE as portable system | Avoided overgeneralizing XStack | Current | 5 |
| 06 | AIDE narrowed from platform/app to portable repo harness/profile | Profiles+Harness+Compatibility+Dominium Bridge first | Avoided building another coding agent | Current | 5 |
| 07 | Open-source/leak projects assessed | Claude Code leak, OMX, claw-code, Graphify, claude-mem, OpenHands etc. | Informed patterns but not foundations | Ongoing reference | 4 |
| 08 | Versioning/capability model discussed | Versions vs capabilities vs provenance split | Provides future release/support architecture | Pending implementation | 4 |
| 09 | Dominium repo restructuring aligned with AIDE | Topology authority and canonical playable baseline emerged | AIDE becomes refactor control plane | Current | 5 |
| 10 | AIDE repo advanced through Q09/Q10 and beyond planning | AIDE Lite token pack and Harness v0 inspected live | Showed AIDE is usable as pack, not runtime | Current | 5 |
| 11 | Dominium CONVERGE/POST-CONVERGE state inspected | Build proof improved; CTest still blocked | Set immediate Dominium priorities | Current | 5 |
| 12 | Latest Q35-Q57 AIDE plan supplied | Stable control plane, install/repair/upgrade/root recycling flows defined | Authoritative for AIDE future | Current with verification caveat | 4 |
| 13 | This preservation package requested and generated | Chat content consolidated into files/zip | Creates persistent handoff and aggregation input | Current | 5 |

## 28. Spec Book Contribution Register

| Spec-book area | Contribution from this chat | Source IDs | Should become requirement/context/open issue? | Confidence | Notes |
| --- | --- | --- | --- | --- | --- |
| AIDE doctrine | Defines AIDE as repo-native operating layer, not agent clone | WORKSTREAM-04, DECISION-04..07 | requirement/context | 5 | Core future spec chapter |
| XStack migration | XStack as Dominium strict profile, wrapped and retired over time | WORKSTREAM-03,08 | requirement | 5 | Avoid deleting checks |
| Dominium root recycling | File-by-file fates, salvage/move maps, validators | WORKSTREAM-07 | requirement | 5 | Critical for repo cleanup |
| AIDE install/upgrade | Additive, target-truth-preserving install/repair/upgrade/rollback | WORKSTREAM-05 | requirement | 4 | Needs implementation |
| Git/workunit policy | main/dev/task branches, structured commits, workunit recovery | WORKSTREAM-10 | requirement | 4 | Cross-repo useful |
| Version/capabilities | Versions/release identity vs capability compatibility | WORKSTREAM-09 | requirement/open issue | 4 | Needs schemas |
| External research | Claude/OMX/Graphify/claude-mem pattern mining | WORKSTREAM-11 | background context | 4 | Do not merge as dependency |
