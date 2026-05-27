Status: DERIVED
Last Reviewed: 2026-05-28
Supersedes: none
Superseded By: none
Stability: provisional
Result: reader_page_generated
Binding Sources: `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, `AGENTS.md`, `docs/planning/AUTHORITY_ORDER.md`, `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
Authority Class: advisory_only
Source Class: conversation_handoff_export
Source Folder: `docs/archive/conversations/Portability_Assurance_Future_Proof/`
Promotion Status: not_reviewed

# Domino/Dominium Portability, Assurance, and Future-Proof Architecture - Conversation Reader

This reader page is derived from archived conversation material. It cannot override canon, contracts, schema law, current queue state, live repo structure, or validated repo artifacts.

## What This Conversation Was About

This chat was mainly about turning Domino/Dominium from a one-off game project into a durable, reusable engine/product platform. It began with a question about whether standards from high-assurance domains-especially DO-178B/C and adjacent secure-development, supply-chain, and metadata standards-could be used for Domino and Dominium. The proposed answer was that the project should use standards as design inputs, not as compliance targets. The useful parts are traceability, requirements-based tests, tool-impact classification, independent review, secure development, release provenance, SBOM/license metadata, and risk-based assurance. The wrong move would be claiming or pursuing avionics-style certification for a game/engine project.

The user then widened the topic. They explicitly said that portability, modularity, extensibility, reuse, refactorability, and future-proofing are very important. They want code reusable for another game on Domino, and possibly for different engine or game projects. They also want files and directories replaceable during rewrites or major refactors. The desired quality bar is closer to a proper game platform or OS-style system than a throwaway indie project.

The central proposed answer was that Domino should be a contract-governed engine platform, while Dominium should be one product built on it. The assistant's core doctrine was "stable outside, replaceable inside." Public contracts-headers, save formats, pack formats, replay formats, schemas, protocols, command/result APIs, capability IDs, and migration rules-should be explicit, versioned, tested, and hard to break casually. Private internals, algorithms, backend modules, and directory-internal helper files should remain replaceable.

## Why It Mattered

This conversation matters as historical context for the topics tagged here: architecture, content, contracts_schema, determinism, governance, release, setup_launcher, simulation, timekeeping, tooling, ui, worldgen. Its value is explanatory and evidentiary, not authoritative. Any claim must be checked against current repo artifacts before promotion.

## What Was Discussed

The package appears to be a `conversation_handoff_package` with `15` source files. The primary extracted source is `docs/archive/conversations/Portability_Assurance_Future_Proof/Domino_Dominium_Portability_Assurance_Future_Proof_Architecture__01_human_readable_report.md`.

## What Was Decided

- The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved.
- Status: Assistant recommendation; not separately accepted after answer.
- Rationale: Replacement must be objectively testable.
- Status: Decision in this package.
- Rationale: Preservation must be honest about source scope.
- The user explicitly required human-readable preservation, uncertainty labels, no invented facts, no silent inference, and no treating assistant recommendations as user decisions. The user explicitly values portability, modularity, extensibility, reuse, replaceability, future-proofing, and proper long-lived engineering.
- Known: Assistant recommended DDAP; user has not explicitly accepted it.
- Unknown: User's final acceptance and desired strictness.
- This chat contributes architecture doctrine, assurance framing, API/ABI policy candidates, data-compatibility doctrine, conformance testing requirements, determinism/replay principles, and setup/launcher/tool/UI boundary principles. It should feed future spec-book chapters but should not be merged as final canon without checking recommendation status and actual repo state.
- Modularity must be proven by conformance tests, not just folders.
- 4. Should DDAP/DIL be accepted, revised, or rejected?

## What Was Not Decided

- The chat proposed using standards such as DO-178C, NIST SSDF, OWASP ASVS, SLSA, and SPDX as design inputs only. The proposed internal version is DDAP v0 with DIL levels. Uncertainty: user has not explicitly ratified DDAP.
- The actual repo was not inspected. The exact accepted directory structure, API policy, DDAP profile, compatibility promises, and first pilot module remain unresolved.
- Caveat: carry forward as `INFERENCE / assistant recommendation`.
- Caveat: carry forward as `FACT goal + INFERENCE architecture`.
- Caveat: carry forward as `assistant recommendation`.
- Implications: Safe for aggregation only with caveats.
- Caveat: carry forward as `FACT / UNCERTAIN scope`.
- 10. Feed this package into the master Project Spec Book with caveats.
- The user explicitly required human-readable preservation, uncertainty labels, no invented facts, no silent inference, and no treating assistant recommendations as user decisions. The user explicitly values portability, modularity, extensibility, reuse, replaceability, future-proofing, and proper long-lived engineering.
- Resolution path: Verify against official/current sources before normative text.
- The uploaded prompt requested this preservation package. The main caveat is that the package preserves visible chat context and the uploaded prompt, not a guaranteed hidden full transcript or inspected repository. The best next action is to inspect the actual repo and turn the strongest recommendations into a small set of enforceable policies and one conformance-test pilot.

## Ideas Rejected, Superseded, Or Deprioritised

- The chat began with the user pasting a standards-focused answer originally framed around Eureka and asking whether similar ideas could be used for Domino and Dominium. The answer developed into a recommendation: borrow assurance patterns, but do not claim or pursue DO-178C or similar compliance.
- Status: Rejected by assistant recommendation.
- Status: Rejected/deprioritised by assistant recommendation.
- Status: Rejected implicitly.
- 4. Should DDAP/DIL be accepted, revised, or rejected?

## What Future Work Came From It

- Limitations: this package preserves visible current-chat context and the uploaded preservation prompt. It does not prove that hidden transcript segments, other conversations, repository files, or older generated artifacts were accessible. Broader project context is not treated as current-chat fact unless labelled.
- The user then clarified that the real concern was broader: all code should be portable, modular, extensible, reusable, replaceable, and future-proof. This shifted the conversation from standards to the whole structure of the engine/product ecosystem.
- The user then uploaded a maximum-fidelity preservation prompt. The task became preserving this chat into a package suitable for human reading and future aggregation. This response is that package.
- A target tree was proposed: include/, contracts/, source/domino/, source/dominium/, tests/conformance/, tests/migration/, tests/fuzz/, tools/validators/, docs/architecture/, docs/assurance/. This is a candidate, not a repo-verified plan.
- Conformance tests prove replaceability. High-trust paths need valid, invalid, malformed, old-version, future-version, migration, roundtrip, determinism, and negative-permission tests.
- The uploaded prompt required this preservation report, registers, spec sheet, aggregator packet, audit, files, and ZIP.
- The user wanted to know whether standards can be used wisely for Domino/Dominium. The user also explicitly wanted portability, modularity, extensibility, reuse, replaceability, proper-game/OS-grade structure, better directories, better names, better APIs, better schemas, and future-proof/backward-compatible design. The uploaded prompt explicitly requested a maximum-fidelity preservation package.
- The user likely wants these outputs to feed a future master Project Spec Book and prevent long-chat context loss.
- Basis: Visible context and uploaded prompt are available; hidden transcript/repo are not guaranteed.
- The user explicitly required human-readable preservation, uncertainty labels, no invented facts, no silent inference, and no treating assistant recommendations as user decisions. The user explicitly values portability, modularity, extensibility, reuse, replaceability, future-proofing, and proper long-lived engineering.
- Why it matters: Compatibility guarantees define future burden and user trust.
- This chat contributes architecture doctrine, assurance framing, API/ABI policy candidates, data-compatibility doctrine, conformance testing requirements, determinism/replay principles, and setup/launcher/tool/UI boundary principles. It should feed future spec-book chapters but should not be merged as final canon without checking recommendation status and actual repo state.

## Important Artifacts

- `handoff`: `1`
- `manifest`: `2`
- `markdown`: `2`
- `primary_report`: `1`
- `prompt`: `1`
- `reader_brief`: `2`
- `registers`: `1`
- `source_input`: `1`
- `spec_sheet`: `1`
- `verification`: `2`
- `zip`: `1`

## Verification Needed

- Verify every implementation, platform, tooling, release, and queue claim against current repo artifacts.
- Treat external platform or SDK claims as stale until independently checked.
- Treat old language-baseline claims as historical unless they match current `README.md` and current contracts.
- Do not infer current authority from the existence of this archive package.

## Candidate Promotions

Candidate promotions, if any, are recorded in `_promotion/PROMOTION_QUEUE.md`. This page does not promote claims.

## Do Not Assume

- Do not assume this conversation established current repo truth.
- Do not assume generated package reports are canonical.
- Do not assume old prompts were executed.
- Do not assume unresolved items are safe to implement.
- Do not use this package to open blocked work without stronger current authority.
