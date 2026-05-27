# Verification and Audit — Dominium Domino Codex Planning

## 1. Audit of the Original Context Transfer Packet

| Issue | Severity | Correction applied | Residual risk |
|---|---|---|---|
| Prior transfer packet did not create downloadable files. | High | This response creates seven files plus a ZIP. | Download/storage still depends on user saving files. |
| Repo-specific claims from questionnaire answer were not sufficiently verifiable. | High | All such claims are labelled UNCERTAIN / UNVERIFIED and added to verification queue. | Future assistant may still skip verification. |
| Generated Codex prompts were summarized, not reproduced verbatim. | Medium | Prompt objectives, files, APIs, constraints, risks, and sequencing are preserved. | Exact wording may require original chat if needed. |
| Assistant recommendations risk being treated as decisions. | High | Decision register separates FACT, INFERENCE, and recommendation status. | Aggregator must respect labels. |
| Startup prompt linker risk was not part of original prompt text. | High | Added as explicit risk/task/question. | Implementation still requires design revision. |
| C89/C++98 pitfalls needed stronger highlighting. | High | Added risks for long long/q48_16 and std::snprintf/C++98 issues. | Repo policy may already solve this, requiring verification. |
| Native-endian TLV conflict with cross-platform compatibility was under-emphasized. | High | Added task/question/risk to define endian-stable TLV IO. | Could remain acceptable as temporary if user chooses. |
| Missing pack-system prompt could be lost. | High | Added as workstream, task, artifact, open question, and carry-forward item. | Needs generation in future chat. |
| The packet did not provide normalized stable IDs for every item. | High | This package assigns WORKSTREAM/DECISION/TASK/CONSTRAINT/QUESTION/ARTIFACT/RISK/REJECTED/VERIFY IDs. | IDs are new and should be preserved. |
| Possible project-context vs chat-local boundary ambiguity. | Medium | Report metadata and labels clarify source scope. | Some master prompt content is user-visible and project-level simultaneously. |

## 2. Final Reliability Assessment

- Completeness rating: 4/5.
- Reliability rating: 4/5 for visible-chat facts; 2/5 for repo-specific questionnaire facts until verified.
- Aggregation readiness rating: 4/5.
- Main remaining uncertainty sources:
  - Whether generated Codex prompts were executed.
  - Current contents of `dominium.zip` / active repo.
  - Whether prior assistant actually inspected the repo.
  - Exact current CMake targets and backend implementation status.
  - User confirmation of some assistant recommendations.

## 3. Manual Verification Checklist

- Confirm the generated ZIP opens and contains all seven files.
- Verify `dominium.zip` or current repo before using repo-specific claims.
- Search repo for all prompt-generated files.
- Run CMake configure/build and target help.
- Run available tests, especially `domino_numeric_test` and game headless checksum if present.
- Review startup dispatcher implementation plan for link safety.
- Review numeric core for C89 compliance.
- Review TLV/data format endian policy.
- Confirm if user wants the missing pack-system prompt next.
- Confirm if startup env/config overrides should remain deferred.

## 4. Residual Risk Register

| ID | Residual risk | Consequence | Mitigation | Label |
|---|---|---|---|---|
| RISK-01 | Unverified repo-state claims are treated as verified facts. | Future prompts/code may target wrong files/platforms/APIs. | Inspect dominium.zip/current repo and label facts with file evidence. | UNCERTAIN / UNVERIFIED |
| RISK-02 | Generated prompts are mistaken for implemented code. | Duplicate work, conflicts, or missed implementation gaps. | Check repo for generated files before continuing. | INFERENCE |
| RISK-03 | Startup dispatcher in domino_core references all product C++ wrappers and causes unresolved symbols. | Build/link failure for tests or individual product targets. | Use callback-table/generic dispatcher or product-local dispatcher instead. | INFERENCE |
| RISK-04 | Strict C89 and C++98 are violated by generated snippets. | Build portability failure and policy violation. | Audit for long long, std::snprintf, declarations, and modern constructs. | INFERENCE |
| RISK-05 | q48_16/u64/i64 implementation relies on non-C89 compiler extensions without clear fallback. | Retro/compiler portability failure. | Define portability policy or emulation for strict C89 targets. | INFERENCE |
| RISK-06 | Native-endian TLV save/load conflicts with cross-platform compatibility. | Old/cross-platform saves may not load deterministically. | Introduce endian-stable TLV helpers early. | INFERENCE |
| RISK-07 | Minimal JSON manifest parser is brittle. | Manifest parsing fails on valid but differently formatted JSON or edge cases. | Constrain manifest subset or replace with robust deterministic parser/TLV manifest. | INFERENCE |
| RISK-08 | Layering violations introduced by Codex. | Product code may call OS APIs or render APIs directly, undermining portability. | Each prompt must explicitly restate dsys/dgfx boundaries and reviews must enforce them. | INFERENCE |
| RISK-09 | Broad GUI/TUI/dgfx prompts overreach existing API maturity. | Large inconsistent changes and build failures. | Split prompts after repo inspection. | INFERENCE |
| RISK-10 | GUI/TUI product logic diverges from CLI behavior. | Bugs and incompatible product workflows. | Use shared state machines and product action models. | INFERENCE |
| RISK-11 | GUI directly depends on raster/theme packs and breaks vector-only fallback. | Products fail without optional assets. | Ensure built-in vector style/icon pack remains mandatory. | INFERENCE |
| RISK-12 | IME/input event timing contaminates deterministic sim. | Sim results differ by platform/UI mode. | Input event streams are deterministic per frame; sim RNG isolated from UI systems. | INFERENCE |
| RISK-13 | Backend detection or GUI timing uses nondeterministic environment values for sim-affecting choices. | Different render backend may alter sim behavior. | Keep render/UI backend separate from sim; fixed tick and deterministic input stream. | INFERENCE |
| RISK-14 | Pack-system prompt becomes too broad and under-specified. | Asset loading, shader packs, audio packs, and streaming become inconsistent. | Split pack prompt or define pack manifest and deterministic load order first. | INFERENCE |
| RISK-15 | Windows/macOS packaging realities break one-binary startup assumptions. | Double-click vs terminal detection may not behave as intended. | Decide Windows subsystem and macOS bundle strategy after repo/build inspection. | INFERENCE |
| RISK-16 | Questionnaire answer carries stale/external software-version claims. | Platform/render/API plan may rely on outdated build facts. | Re-verify current docs/toolchains before using. | UNCERTAIN / UNVERIFIED |
| RISK-17 | This final report package over-compresses generated prompts. | Future assistant may need original chat to recover exact prompt text. | Report preserves prompt objectives, files, constraints, APIs, and risks; original chat remains ideal source for exact wording. | INFERENCE |
| RISK-18 | Future aggregator merges recommendations as decisions. | Spec Book may incorrectly formalize tentative suggestions. | Use labels/status fields and preserve uncertainty. | FACT |

## 5. Recommended Re-Extraction Triggers

- A newer chat changes the project language policy.
- A newer chat confirms or rejects platform tier priorities.
- Codex applies any of the generated prompts and changes actual repo state.
- The user uploads a newer repo zip.
- The startup dispatcher design is implemented or superseded.
- The missing pack-system prompt is generated.
- The questionnaire is re-answered from verified files.
