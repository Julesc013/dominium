# 29. Context Transfer Packet for a Future Chat — Dominium Modularity, AIDE Refactorability, and Future-Proof Architecture

## 29.1 Ultra-Condensed Bootstrap Brief

This retired-chat handoff covers a Dominium architecture discussion about making the project portable, modular, extensible, reusable, and refactorable. The user wants Dominium built like a serious long-lived game/engine platform, not a one-off indie repository. The conversation moved from directory cleanup to a broader doctrine: stable root constitution, logical-root projection for distribution/install/package/media/bundles, AIDE as the refactor control plane, product-line reuse boundaries, versioned contracts and manifests, stable API/ABI seams, deterministic data, and mechanical future refactors.

The most important user correction was rejecting XStack/AuditX/RepoX/TestX-style architecture naming. The user wants AIDE adopted quickly and wants existing code/docs/tests recycled, not ignored. Therefore, old tooling should be inventoried, wrapped behind AIDE, classified as keep/adapt/extract/convert/archive/drop, then renamed or retired only after value is preserved.

The recommended stable source roots are `.aide/`, `.github/`, `apps/`, `engine/`, `game/`, `runtime/`, `contracts/`, `content/`, `docs/`, `tests/`, `tools/`, `scripts/`, `cmake/`, `external/`, `release/`, `archive/`, with `dist/` as generated/strictly governed output. New roots are refused by default. Paths are not identity; contracts and manifests define identity. Apps are thin. Runtime owns host adaptation. Engine owns deterministic substrate. Game owns Dominium-specific rules. Tools and AIDE own validation/refactor machinery.

The best next action is to verify live repo state, then implement AIDE-STRUCTURE-00 and AIDE-ARCH-00 as non-invasive scaffolding: root constitution, ownership slots, dependency layers, AIDE policies, move/salvage map schemas, inventory tooling, stability levels, C89 ABI rules, modularity docs, and report-only boundary validators. Do not treat pasted repo-status claims as verified. Do not treat all assistant recommendations as accepted user decisions.

## 29.2 Source Hierarchy

1. Direct user statements in this chat.
2. Explicit decisions accepted by the user, especially AIDE transition and recycling existing material.
3. Current task register.
4. Constraint register.
5. Artifact ledger.
6. Inferences from user goals and assistant responses.
7. Assistant suggestions not explicitly accepted.
8. General software engineering knowledge.

## 29.3 Operating Rules for Future Assistants

Preserve FACT / INFERENCE / UNCERTAIN / PROJECT-CONTEXT labels. Do not assume access to the old chat or live repo. Do not re-ask answered questions. Verify stale facts before relying on them. Do not invent missing details. Do not treat tentative items as final. Do not repeat rejected options, especially XStack-style durable naming or visual folder dragging. Preserve artifacts and registers. Use structured outputs when continuing.

## 29.4 Active Workstreams

Active workstreams are WORKSTREAM-01 through WORKSTREAM-09 from the register: repo constitution, distribution projection, AIDE control plane, old-tool recycling, reusable product-line architecture, contracts/API/ABI discipline, naming/matrix cleanup, determinism/testing/proof, and spec-book aggregation.

## 29.5 Current Priorities

Top priorities: verify repo state; implement AIDE-STRUCTURE-00; inventory/wrap old tooling; implement AIDE-ARCH-00; define logical-root projection contracts; add report-only boundary validators; create portability/determinism checks.

## 29.6 Current Open Questions

The main unresolved issues are: current live repo status; which old tools are useful; exact boundary between domino-engine reusable code and Dominium-specific game code; which APIs become stable; which generated artifacts are intentional; and which recommendations become formal spec requirements.

## 29.7 Recommended First Action

Run a live repo baseline verification, then execute AIDE-STRUCTURE-00 as a non-invasive commit that adds root constitution, AIDE refactor framework, move/salvage schema placeholders, and inventory tooling without moving runtime code.
