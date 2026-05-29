## 17. Content, Modding, Providers, and Data-Driven Extension

Content and modding belong behind pack, registry, capability, compatibility, and refusal law.

**Why this chapter matters.** Canon says packs are data-only and missing optional packs must degrade or refuse deterministically. Conversation material expands this into provider models, modules, open-source provider surfaces, and package composition, much of which is blocked.

> [!CURRENT_TRUTH] Current repo truth comes first in this chapter. Archive and conversation evidence is used to explain design intent, recurring concerns, and review candidates without promoting it.

### Integrated Evidence

The current repo-backed evidence emphasizes: Packs provide capabilities, data, and assets; executables do not embed content (EVC-00035). Foundation Lock does not mean full CTest is green, every compatibility corpus exists, every provider is implemented, every runtime trust rule is enforced, Workbench UI exists, or broad feature work is open (EVC-01460). The user also made a clear versioning decision. **FACT:** The user wanted **major.minor.patch semantic versioning** for all components/packages and for the complete game package. The user explicitly did **not** want build numbers or build dates in (EVC-00695).
The archive and conversation corpus add: The user also made a clear versioning decision. **FACT:** The user wanted **major.minor.patch semantic versioning** for all components/packages and for the complete game package. The user explicitly did **not** want build numbers or build dates in (EVC-00695). The final part of the conversation dealt with repo status and task queue. The user pasted status reports indicating that 'PRESENTATION-CONTRACT-01' completed with warnings, and then chose to generate six maintenance prompts before replanning (EVC-00835). This report is reliable for explaining what was discussed in the visible chat. It is not proof that the real repository has the recommended structure, not proof that the user formally accepted every recommendation, and not a substitute for verifying the (EVC-00498). Top tasks: verify repo baseline, draft framework ABI, add provider manifests, add forbidden include validator, implement null providers, implement raylib providers, create profiles, and define work-lease/CAD schemas (EVC-00382).

### Decisions Already Visible

- **Decision:** The user also made a clear versioning decision. **FACT:** The user wanted **major.minor.patch semantic versioning** for all components/packages and for the complete game package. The user explicitly did **not** want build numbers or build dates in... _Evidence:_ `EVC-00695` from `docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md`. _Status:_ conversation advisory evidence.
- **Decision:** The final part of the conversation dealt with repo status and task queue. The user pasted status reports indicating that 'PRESENTATION-CONTRACT-01' completed with warnings, and then chose to generate six maintenance prompts before replanning... _Evidence:_ `EVC-00835` from `docs/archive/conversations/_reader/by_chat/dominium_full_conversation.md`. _Status:_ conversation advisory evidence.
- **Decision:** This report is reliable for explaining what was discussed in the visible chat. It is not proof that the real repository has the recommended structure, not proof that the user formally accepted every recommendation, and not a substitute for verifying the... _Evidence:_ `EVC-00498` from `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__10_accompanying_detailed_summary_report.md`. _Status:_ conversation advisory evidence.

### Specifications and Requirements

- **Specification:** Packs provide capabilities, data, and assets; executables do not embed content. _Evidence:_ `EVC-00035` from `docs/README.md`. _Status:_ current repo source.
- **Specification:** Top tasks: verify repo baseline, draft framework ABI, add provider manifests, add forbidden include validator, implement null providers, implement raylib providers, create profiles, and define work-lease/CAD schemas. _Evidence:_ `EVC-00382` from `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__06_reader_brief.md`. _Status:_ conversation advisory evidence.
- **Specification:** Verify repository state, raylib/SDL2/Lua versions and platform support, licenses for reference projects, and any second-wave dependency licenses. _Evidence:_ `EVC-00385` from `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__06_reader_brief.md`. _Status:_ conversation advisory evidence.
- **Specification:** Ask next: "Draft DOMINO-FRAMEWORK-WEDGE-01," "Define the provider ABI header," "Verify repo C17/C++17 state," "Design the work-lease protocol," "Create raylib/SDL/Lua provider manifests," or "Turn this into a spec book chapter." _Evidence:_ `EVC-00392` from `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__09_in_chat_reader.md`. _Status:_ conversation advisory evidence.
- **Specification:** This package preserves the visible current chat about standards-informed assurance, portability, modularity, extensibility, replaceability, directory/API/schema/protocol design, and future-proof Domino/Dominium architecture. _Evidence:_ `EVC-00489` from `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__09_in_chat_reader.md`. _Status:_ conversation advisory evidence.
- **Specification:** The user was trying to prevent Dominium from becoming a brittle one-off project. The repeated concern was that the codebase, files, directories, APIs, schemas, renderers, GUIs, and data formats should remain portable, modular, extensible, replaceable... _Evidence:_ `EVC-00739` from `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md`. _Status:_ conversation advisory evidence.
- **Specification:** The exact first implementation branch, versions, and dependency pins are unresolved. The exact Domino Framework ABI is unresolved. The exact Lua version is unresolved. The current repository baseline must be verified. The formal policy for... _Evidence:_ `EVC-00885` from `docs/archive/conversations/_reader/by_chat/framework_open_source_provider.md`. _Status:_ conversation advisory evidence.
- **Specification:** The conclusion was that all products should boot through AppShell, use shared command registries, expose descriptors, validate packs/contracts before session start, and never have ad hoc boot paths. This matters for portability, setup/launcher... _Evidence:_ `EVC-00934` from `docs/archive/conversations/_reader/by_chat/omega_xi_pi_architecture_future.md`. _Status:_ conversation advisory evidence.

### Constraints, Prohibitions, and Prerequisites

- **Constraint:** Foundation Lock does not mean full CTest is green, every compatibility corpus exists, every provider is implemented, every runtime trust rule is enforced, Workbench UI exists, or broad feature work is open. _Evidence:_ `EVC-01460` from `docs/repo/FOUNDATION_LOCK.md`. _Status:_ current repo source; future queue review.
- **Constraint:** 1. '00_manifest.md' - file list and package status. 2. '01_human_readable_report.md' - sections 0-16. 3. '02_context_transfer_packet.md' - future-chat handoff. 4. '03_spec_sheet.yaml' - machine-readable aggregation sheet. 5. '04_registers.md' -... _Evidence:_ `EVC-00440` from `docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__09_in_chat_reader.md`. _Status:_ conversation advisory evidence.
- **Constraint:** Near the end, the chat shifted into preservation mode. The user asked for a maximum-fidelity context transfer packet, then for a downloadable report package, then for an in-chat reader version of that package. Those outputs preserved the decisions... _Evidence:_ `EVC-00845` from `docs/archive/conversations/_reader/by_chat/dominium_setup.md`. _Status:_ conversation advisory evidence.
- **Constraint:** The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved. _Evidence:_ `EVC-00477` from `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__01_human_readable_report.md`. _Status:_ conversation advisory evidence.
- **Constraint:** The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved. _Evidence:_ `EVC-00963` from `docs/archive/conversations/_reader/by_chat/portability_assurance_future_proof.md`. _Status:_ conversation advisory evidence.

### Contradictions, Risks, and Open Ends

- **Risk:** '00_manifest.md' - package map and caveats. _Evidence:_ `EVC-00490` from `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__09_in_chat_reader.md`. _Status:_ conversation advisory evidence.

### Implications for Next Work

Promotion should separate pack documentation from provider/package runtime work.

Any later task that wants to move a claim from this chapter into live authority needs source IDs, target paths, authority compatibility, queue compatibility, and validation evidence. This chapter is therefore a review map, not a permission slip.

### Source Trail

- `docs/README.md`
- `docs/repo/FOUNDATION_LOCK.md`
- `docs/archive/conversations/_promotion/PROMOTION_WAVE_1_CANDIDATES_v0.md`
- `docs/archive/conversations/_reader/by_chat/dominium_full_conversation.md`
- `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__10_accompanying_detailed_summary_report.md`
- `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__06_reader_brief.md`
- `docs/archive/conversations/Framework_Open_Source_Provider/Domino_Framework_Open_Source_Provider_Architecture__09_in_chat_reader.md`
- `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__09_in_chat_reader.md`
- `docs/archive/conversations/_reader/by_chat/architecture_ui_providers.md`
- `docs/archive/conversations/_reader/by_chat/framework_open_source_provider.md`
- `docs/archive/conversations/_reader/by_chat/omega_xi_pi_architecture_future.md`
- `docs/archive/conversations/Modularity_AIDE_Refactorability/Dominium_Modularity_AIDE_Refactorability_Architecture__09_in_chat_reader.md`
- `docs/archive/conversations/_reader/by_chat/dominium_setup.md`
- `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__01_human_readable_report.md`
- `docs/archive/conversations/_reader/by_chat/portability_assurance_future_proof.md`
- `docs/archive/audit/FORKING_PROVIDES_BASELINE.md`
- `docs/archive/audit/NEGOTIATION_HANDSHAKE_BASELINE.md`
- `docs/archive/refactor/QUARANTINE_duplicate.sig.054184f12728a825.md`
