## 20. Specifications and Requirements Still Needing Promotion

Some source claims look like requirements but are not current specs until promoted through the right target docs or contracts.

**Why this chapter matters.** Current authority already contains many requirements; generated evidence can only propose candidates. Archive and conversation materials are strongest when they clarify intent already aligned with current docs.

> [!CURRENT_TRUTH] Current repo truth comes first in this chapter. Archive and conversation evidence is used to explain design intent, recurring concerns, and review candidates without promoting it.

### Integrated Evidence

The current repo-backed evidence emphasizes: Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions (EVC-01433). Normative contracts live under 'docs/architecture/' only. All other docs are guidance, reference, or historical context (EVC-00032). Packs provide capabilities, data, and assets; executables do not embed content (EVC-00035). Archived documents are kept for provenance only. Canonical contracts are in 'docs/architecture/' (EVC-00040).
The archive and conversation corpus add: What disposition should be chosen for this unresolved claim: This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still foll...? (EVC-00686). 'DECISION-0009': What disposition should be chosen for this unresolved claim: This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still foll...? (EVC-00693). [INFERENCE] The conclusion was not a finalized implementation but a working architecture: each simulation domain should be deterministic, fixed-point, content-driven, versioned, replayable, and integrated through clear read/write boundaries (EVC-00694). The user also made a clear versioning decision. **FACT:** The user wanted **major.minor.patch semantic versioning** for all components/packages and for the complete game package. The user explicitly did **not** want build numbers or build dates in (EVC-00695).
The downstream implication is that: Future Series: DOC-CONVERGENCE Replacement Target: canon-aligned documentation set for convergence and release preparation (EVC-00055). 'docs/release/roadmap/' goals and coverage tests only (EVC-00037). Use this prompt block for future work so tasks remain short and stable: (EVC-01442). It does not promote archive claims (EVC-01424).

### Decisions Already Visible

- **Decision:** Rendering is presentational only and MUST NOT mutate truth or enforce authority decisions. _Evidence:_ `EVC-01433` from `docs/canon/constitution_v1.md`. _Status:_ current repo source.
- **Decision:** What disposition should be chosen for this unresolved claim: This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still foll...? _Evidence:_ `EVC-00686` from `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md`. _Status:_ conversation advisory evidence.
- **Decision:** 'DECISION-0009': What disposition should be chosen for this unresolved claim: This chat was about preserving and re-grounding Dominium's architecture around a very old constitutional contract, then checking whether the current GitHub repository still foll...? _Evidence:_ `EVC-00693` from `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md`. _Status:_ conversation advisory evidence.
- **Decision:** [INFERENCE] The conclusion was not a finalized implementation but a working architecture: each simulation domain should be deterministic, fixed-point, content-driven, versioned, replayable, and integrated through clear read/write boundaries. _Evidence:_ `EVC-00694` from `docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md`. _Status:_ conversation advisory evidence.
- **Decision:** The user also made a clear versioning decision. **FACT:** The user wanted **major.minor.patch semantic versioning** for all components/packages and for the complete game package. The user explicitly did **not** want build numbers or build dates in... _Evidence:_ `EVC-00695` from `docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md`. _Status:_ conversation advisory evidence.
- **Decision:** The user pasted the final README after those cleanup changes. At that point, the README had the current active form: deterministic constraints clarified, ports unified under one source hierarchy, '/ports' metadata-only if retained, Section 9 normative... _Evidence:_ `EVC-00703` from `docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md`. _Status:_ conversation advisory evidence.
- **Decision:** What disposition should be chosen for this unresolved claim: The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The...? _Evidence:_ `EVC-00682` from `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md`. _Status:_ conversation advisory evidence.
- **Decision:** 'DECISION-0001': What disposition should be chosen for this unresolved claim: The user then asked whether arbitrary placement was possible or whether the system was stuck to grids. The answer established that the engine should be grid-agnostic. [FACT] The...? _Evidence:_ `EVC-00689` from `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md`. _Status:_ conversation advisory evidence.

### Specifications and Requirements

- **Specification:** Normative contracts live under 'docs/architecture/' only. All other docs are guidance, reference, or historical context. _Evidence:_ `EVC-00032` from `docs/README.md`. _Status:_ current repo source.
- **Specification:** Packs provide capabilities, data, and assets; executables do not embed content. _Evidence:_ `EVC-00035` from `docs/README.md`. _Status:_ current repo source.
- **Specification:** Archived documents are kept for provenance only. Canonical contracts are in 'docs/architecture/'. _Evidence:_ `EVC-00040` from `docs/README.md`. _Status:_ current repo source.
- **Specification:** Scope: index of frozen and evolving constitutional surfaces. _Evidence:_ `EVC-00056` from `docs/architecture/CONTRACTS_INDEX.md`. _Status:_ current repo source.
- **Specification:** This index is the navigation hub for stability surfaces. "FROZEN" means the _Evidence:_ `EVC-00057` from `docs/architecture/CONTRACTS_INDEX.md`. _Status:_ current repo source.
- **Specification:** document defines a contract that must not change lightly. "EVOLVING" means the _Evidence:_ `EVC-00058` from `docs/architecture/CONTRACTS_INDEX.md`. _Status:_ current repo source.
- **Specification:** Schemas are the authoritative data-shape contracts. Start here: _Evidence:_ `EVC-00060` from `docs/architecture/CONTRACTS_INDEX.md`. _Status:_ current repo source.
- **Specification:** 'tests/apps/' (legacy and adjacent contract checks) _Evidence:_ `EVC-00061` from `docs/architecture/CONTRACTS_INDEX.md`. _Status:_ current repo source.

### Constraints, Prohibitions, and Prerequisites

- **Constraint:** Foundation Lock does not mean full CTest is green, every compatibility corpus exists, every provider is implemented, every runtime trust rule is enforced, Workbench UI exists, or broad feature work is open. _Evidence:_ `EVC-01460` from `docs/repo/FOUNDATION_LOCK.md`. _Status:_ current repo source; future queue review.
- **Prohibition:** Client and renderer project data and issue intents; they do not author authoritative outcomes. _Evidence:_ `EVC-01434` from `docs/canon/constitution_v1.md`. _Status:_ current repo source.
- **Prerequisite:** Delegated execution requires deterministic proof artifacts before commit. _Evidence:_ `EVC-01436` from `docs/canon/constitution_v1.md`. _Status:_ current repo source.
- **Constraint:** 'platform' (39 conversations): runtime shell, platform adapter, renderer boundary, operating-system support, and portability. Sources: [Dominium Advanced Simulation and Infrastructure... _Evidence:_ `EVC-01081` from `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md`. _Status:_ conversation advisory evidence.
- **Constraint:** 'platform' (39 conversations): runtime shell, platform adapter, renderer boundary, operating-system support, and portability. Sources: [Dominium Advanced Simulation and Infrastructure... _Evidence:_ `EVC-01097` from `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md`. _Status:_ conversation advisory evidence.
- **Prohibition:** Do not promote archive claims without a later reviewed task. _Evidence:_ `EVC-01103` from `docs/archive/conversations/_synthesis/READ_THIS_FIRST_v0.md`. _Status:_ conversation advisory evidence.
- **Prerequisite:** Any Wave 1 candidate before source text and target docs are inspected together. _Evidence:_ `EVC-01072` from `docs/archive/conversations/_synthesis/CURRENT_PROJECT_ATLAS_v0.md`. _Status:_ conversation advisory evidence.
- **Constraint:** The most important specific calendar is the user-defined Perfect Earth Calendar (HPC-E): 13 months of 28 days, weekdays Monday-Sunday, year begins in March, month order March through February with Undecember as the 11th month, and all intercalary days... _Evidence:_ `EVC-00133` from `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md`. _Status:_ conversation advisory evidence.
- **Constraint:** Mass moves or broad rewrites can break build, tests, imports, packaging, and compatibility. Use small gated migrations. _Evidence:_ `EVC-00210` from `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md`. _Status:_ conversation advisory evidence.
- **Constraint:** 1. Is the official scope one star system, multiple star systems, or a true galaxy-scale universe? 2. What exact scientific constraints define realistic planet generation? 3. How does reverse planet generation work? 4. What is the field-layer and... _Evidence:_ `EVC-00279` from `docs/archive/conversations/Dominium_Complete_Conversation/existing_companion_report_package/Dominium_Complete_Conversation_Companion_Report__human_readable_detailed_summary.md`. _Status:_ conversation advisory evidence.

### Contradictions, Risks, and Open Ends

- **Contradiction:** Constitutional conflicts are resolved by this document, not by prompt convenience. _Evidence:_ `EVC-01441` from `docs/canon/constitution_v1.md`. _Status:_ current repo source.
- **Risk:** Continue documentation and evidence updates that keep remaining warnings and full-gate debt visible. _Evidence:_ `EVC-01466` from `docs/repo/FOUNDATION_LOCK.md`. _Status:_ current repo source.
- **Change Of Direction:** 'docs/archive/' historical and superseded docs only _Evidence:_ `EVC-00039` from `docs/README.md`. _Status:_ current repo source.
- **Contradiction:** The current repo should not be overstated as a complete runtime implementation of all v1 goals. _Evidence:_ `EVC-00178` from `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Canon_Portability_Audit__01_human_readable_report.md`. _Status:_ conversation advisory evidence.
- **Contradiction:** Use negative architecture rules to prevent drift. _Evidence:_ `EVC-00206` from `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md`. _Status:_ conversation advisory evidence.
- **Contradiction:** Verify standards, repo structure, toolchain targets, persistent formats, and cross-chat conflicts. _Evidence:_ `EVC-00488` from `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__06_reader_brief.md`. _Status:_ conversation advisory evidence.
- **Contradiction:** The conversation began with the user presenting a long assessment of whether Eureka should borrow from DO-178B/C and related standards. The pasted assessment argued that the right approach is not full DO-178C compliance, but a DO-178C-inspired assurance... _Evidence:_ `EVC-00499` from `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__10_accompanying_detailed_summary_report.md`. _Status:_ conversation advisory evidence.
- **Contradiction:** Resolve DSYS vs 'domino_sys_*' if conflict appears. _Evidence:_ `EVC-01371` from `docs/archive/conversations/platform_renderer_api_plan/dominium_codex_platform_renderer_api_plan__05_reader_brief.md`. _Status:_ conversation advisory evidence.
- **Contradiction:** A future assistant may merge this with other chats without preserving conflicts. Mitigation: use the aggregator packet and conflict warnings. _Evidence:_ `EVC-00109` from `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`. _Status:_ conversation advisory evidence.
- **Contradiction:** Risk 6 - Cross-chat aggregation drift _Evidence:_ `EVC-00129` from `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__10_accompanying_human_readable_detailed_summary_report.md`. _Status:_ conversation advisory evidence.

### Second- and Third-Order Effects

- **Third Order Effect:** Future Series: DOC-CONVERGENCE Replacement Target: canon-aligned documentation set for convergence and release preparation _Evidence:_ `EVC-00055` from `docs/architecture/CONTRACTS_INDEX.md`. _Status:_ current repo source.
- **Third Order Effect:** 'docs/release/roadmap/' goals and coverage tests only _Evidence:_ `EVC-00037` from `docs/README.md`. _Status:_ current repo source.
- **Design Goal:** Use this prompt block for future work so tasks remain short and stable: _Evidence:_ `EVC-01442` from `docs/canon/constitution_v1.md`. _Status:_ current repo source.
- **Design Goal:** It does not promote archive claims. _Evidence:_ `EVC-01424` from `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md`. _Status:_ archive historical evidence.
- **Second Order Effect:** A preservation package was then generated. This current task adds an accompanying detailed report and bundles it with the earlier preservation files, the uploaded preservation prompt, a new manifest, and a ZIP package. Some previously uploaded files were... _Evidence:_ `EVC-00204` from `docs/archive/conversations/Dominium_Complete_Conversation/Accompanying_Report/Dominium_Entire_Conversation_Accompanying_Report__10_accompanying_detailed_summary_report.md`. _Status:_ conversation advisory evidence.
- **Second Order Effect:** This report does **not** claim to capture every older Dominium conversation. The accessible material shows that this is part of a broader Dominium project, but the complete historical project transcript is not visible here. Some previously uploaded files... _Evidence:_ `EVC-00614` from `docs/archive/conversations/UE6_Domino_Deterministic_Universe/Dominium_UE6_Domino_Deterministic_Universe__10_accompanying_human_readable_detailed_summary_and_report.md`. _Status:_ conversation advisory evidence.
- **Third Order Effect:** Later, the user expanded the horizon: Dominium should start with simple early graphics and audio, but eventually support AAA-quality graphics, spatial audio, environmental acoustics, proximity chat, AI, navigation, terrain, vehicles, economy, combat... _Evidence:_ `EVC-00950` from `docs/archive/conversations/_reader/by_chat/platform_renderer_api_plan.md`. _Status:_ conversation advisory evidence.
- **Third Order Effect:** If merged into a future master spec book, this chat should inform chapters on architecture doctrine, repository governance, XStack, versioning and release, agent governance, runtime componentization, live operations roadmap, and long-term future-proofing. _Evidence:_ `EVC-01364` from `docs/archive/conversations/omega_xi_pi_architecture_future/dominium_omega_xi_pi_architecture_future_proofing_planning__10_accompanying_human_readable_detailed_summary_and_report.md`. _Status:_ conversation advisory evidence.
- **Third Order Effect:** 4. **Conceptual artifacts produced in chat.** These include proposed architectures, matrices, lane plans, Workbench modules, Interface Operating Layer, boot-to-replay MVP, and structured roadmaps. _Evidence:_ `EVC-00943` from `docs/archive/conversations/_reader/by_chat/os_interface_repo_architecture.md`. _Status:_ conversation advisory evidence.
- **Third Order Effect:** Native widgets were a recurring theme. **FACT:** The user wanted true OS controls, not merely native-looking custom rendering. This means real Win32 controls on Windows, and eventually platform-native controls on other systems where possible. _Evidence:_ `EVC-01028` from `docs/archive/conversations/_reader/by_chat/ui_editor_tool_editor_planning.md`. _Status:_ conversation advisory evidence.

### Implications for Next Work

Promotion candidates should be converted into bounded microtasks with source IDs and validation.

Any later task that wants to move a claim from this chapter into live authority needs source IDs, target paths, authority compatibility, queue compatibility, and validation evidence. This chapter is therefore a review map, not a permission slip.

### Source Trail

- `docs/canon/constitution_v1.md`
- `docs/README.md`
- `docs/architecture/CONTRACTS_INDEX.md`
- `docs/architecture/INVARIANTS.md`
- `docs/architecture/WHAT_THIS_IS.md`
- `docs/architecture/WHAT_THIS_IS_NOT.md`
- `docs/canon/glossary_v1.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/archive/conversations/_decision/DECISION_SUMMARY_v0.md`
- `docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md`
- `docs/archive/conversations/_synthesis/CURRENT_PROJECT_ATLAS_v0.md`
- `docs/archive/docs_corpus/_archive/DOCS_CONVERSATION_CORPUS_INTEGRATION_v0.md`
- `docs/archive/conversations/_synthesis/FULL_PROJECT_PICTURE_v0.md`
- `docs/archive/conversations/_synthesis/PROJECT_SYNTHESIS_BOOK_v0.md`
- `docs/archive/conversations/_synthesis/READ_THIS_FIRST_v0.md`
- `docs/archive/docs_corpus/_reconciliation/DOCS_CURRENT_PROJECT_PICTURE_v0.md`
- `docs/archive/conversations/Build_and_Future_Proofing/Dominium_Build_and_Future_Proofing_Architecture__01_human_readable_report.md`
- `docs/archive/conversations/Chronology_Celestial_Systems/Dominium_Chronology_Celestial_Systems__05_reader_brief.md`
