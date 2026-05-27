# Verification and Audit — Dominium GUI/Binary + CONTENT0 Handoff

## 1. Audit of the Original Context Transfer Packet

| Issue | Severity | Correction applied | Residual risk |
|---|---|---|---|
| Previous packet was strong but not normalized into stable IDs for all package files. | medium | Added WORKSTREAM/DECISION/TASK/CONSTRAINT/QUESTION/ARTIFACT/RISK/VERIFY/REJECTED IDs. | IDs may need reconciliation with future packages. |
| Previous packet mixed visible chat preferences with user profile context. | medium | Marked outside-profile preference as PROJECT-CONTEXT. | Future assistant may still treat project-context as chat fact. |
| External platform facts were previously cited as current. | medium-high | Marked platform facts as requiring verification before future use. | Future implementation may skip verification. |
| Linux and Android sections were necessarily vague. | medium | Kept them open and created explicit questions/tasks. | Spec aggregator may want firmer conclusions; should not invent them. |
| Assistant suggestions risk being promoted to decisions. | high | Labelled C ABI, profiles, static packaging as INFERENCE/candidates. | Human readers may overlook labels. |
| No actual repo/files inspected. | high | Added VERIFY-01 and repeated caveat in metadata/risks. | Implementation planning from package alone could be wrong. |
| Original CONTENT0 exact prompt is long and not fully repeated in every file. | low-medium | Artifact ledger points to it and full report summarizes constraints; previous packet included verbatim. | If this package is separated from previous transcript, exact wording may require original packet or chat. |
| Potential contradiction: user said AppKit 64-bit Intel only but SwiftUI Intel/ARM; assistant suggested AppKit can be ARM too. | medium | Recorded as open question rather than decision. | Future matrix may assume one or the other. |

## 2. Final Reliability Assessment

| Metric | Rating | Notes |
|---|---:|---|
| Completeness | 4 / 5 | Covers visible chat and previous packet; no repo/files inspected. |
| Reliability | 4 / 5 | Strong for user-stated decisions; medium for assistant technical corrections and stale platform facts. |
| Aggregation readiness | 4 / 5 | Stable IDs, registers, manifest, and YAML spec sheet created. |

Main remaining uncertainty sources:

- Actual repository/file state.
- Current platform/toolchain documentation.
- Whether macOS 10.9 and .NET 4.0 are hard support requirements.
- Linux and Android strategy choices.
- Backend/UI contract shape.
- TUI parity expectations.

## 3. Manual Verification Checklist

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
|---|---|---|---|---|---|---|
| VERIFY-01 | Confirm actual repository/file availability and structure. | Prior assistant references to repo/files are unverified here. | File upload/repo inspection | critical before implementation | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | Confirm project name convention: Dominium vs Domino. | Both names appear in prompt context. | User or repo metadata | medium | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | Verify current Windows App SDK / WinUI 3 system requirements and Windows 10 1809 floor. | Toolchain facts are time-sensitive. | Official Microsoft docs | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | Verify WinForms/.NET Framework targeting support and Visual Studio versions. | Old .NET support requires real lanes. | Official Microsoft docs and installed toolchains | high | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | Confirm exact .NET Framework target floors desired. | User named .NET 4.0 but support cost may be high. | User decision | high | WORKSTREAM-08 | FACT |
| VERIFY-06 | Verify current Xcode deployment targets and old SDK feasibility. | macOS 10.9 support is toolchain-sensitive. | Official Apple docs and actual Xcode/SDK availability | high | WORKSTREAM-09 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Confirm whether macOS 10.9 is hard requirement. | Legacy macOS lane may be expensive. | User decision | high | WORKSTREAM-09 | FACT |
| VERIFY-08 | Verify .NET MAUI supported platforms if considered. | MAUI support changes over time and Linux desktop is not established here. | Official Microsoft docs | medium | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Compare Linux GUI stack current support: Qt, GTK, Avalonia, custom renderer host. | Linux stack is undecided and current package support matters. | Official docs and distro/package docs | high | WORKSTREAM-10 | UNCERTAIN / UNVERIFIED |
| VERIFY-10 | Confirm Android target role and API floor. | Android is in scope but undefined. | User decision and Android docs | high | WORKSTREAM-11 | FACT |
| VERIFY-11 | Verify Native AOT suitability for any .NET shells. | AOT limitations may conflict with plugins/reflection/dynamic loading. | Official Microsoft docs and prototype | medium | WORKSTREAM-12 | UNCERTAIN / UNVERIFIED |
| VERIFY-12 | Confirm TUI parity expectations. | 'Expected to work with TUI' is not detailed. | User decision | high | WORKSTREAM-15 | FACT |
| VERIFY-13 | Confirm whether stable C ABI is acceptable. | Candidate only; impacts all frontend integration. | User/project architecture review | critical | WORKSTREAM-07 | INFERENCE |
| VERIFY-14 | Resolve CONTENT0 schema semantic boundaries. | Descriptive schemas can accidentally imply behavior. | Schema review and user decision | medium | WORKSTREAM-01 | INFERENCE |
| VERIFY-15 | Define deterministic seed hierarchy for content. | CONTENT0 requires seeds but not seed namespace rules. | Content architecture decision | medium | WORKSTREAM-03 | FACT |
| VERIFY-16 | Define importance criteria for Milky Way celestial sites. | Default datapack selection depends on this. | Design decision and astronomical data-source review | medium | WORKSTREAM-04 | FACT |
| VERIFY-17 | Confirm current facts before final Project Spec Book aggregation. | This package includes stale-prone external references. | Official docs/current source pass | high | WORKSTREAM-16 | FACT |

## 4. Residual Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
|---|---|---|---|---|---|---|---|
| RISK-01 | GUI family drift | Different frontends implement different behavior. | medium | high | Define shared backend contract and test CLI/TUI/GUI against same capabilities. | WORKSTREAM-07 | INFERENCE |
| RISK-02 | Framework capture | WinForms/SwiftUI/etc. becomes product architecture instead of shell. | medium | high | Keep product logic backend-owned and shells thin. | WORKSTREAM-06 | INFERENCE |
| RISK-03 | Compatibility fraud | Claimed support for old hosts cannot be built or tested. | high | high | Require toolchain/build/test lane for every support claim. | WORKSTREAM-13 | INFERENCE |
| RISK-04 | Matrix explosion | Too many OS/arch/framework/era/style combinations to maintain. | medium-high | high | Use compatibility lanes and small visual profile set. | WORKSTREAM-14 | INFERENCE |
| RISK-05 | Premature prompt/code generation | Locks in unresolved assumptions. | medium | medium-high | Begin new chat with doctrine and matrices, not code. | WORKSTREAM-16 | FACT |
| RISK-06 | Schema behavior smuggling in CONTENT0 | Data schemas imply runtime mechanics contrary to scope. | medium | high | Limit schemas to shape, units, references, required fields; no behavior/default logic. | WORKSTREAM-01 | INFERENCE |
| RISK-07 | Fake precision in universe/content data | Content appears authoritative but is fabricated or too precise. | medium | medium-high | Use provenance, confidence, macro resolution, and sources. | WORKSTREAM-03 | INFERENCE |
| RISK-08 | Linux fragmentation | GUI/package fails across distros or display stacks. | medium | medium | Choose distro baselines and packaging formats explicitly. | WORKSTREAM-10 | INFERENCE |
| RISK-09 | macOS legacy trap | macOS 10.9 consumes disproportionate tooling effort. | medium | medium-high | Confirm whether 10.9 is hard requirement before committing. | WORKSTREAM-09 | INFERENCE |
| RISK-10 | Old .NET target trap | Supporting .NET 4.0 requires unsupported/old build tooling. | medium | medium-high | Define exact .NET floor and maintain frozen VS lane if needed. | WORKSTREAM-08 | UNCERTAIN / UNVERIFIED |
| RISK-11 | Android scope creep | Mobile project expands into full parity without clear need. | medium | medium | Define Android role first. | WORKSTREAM-11 | INFERENCE |
| RISK-12 | Over-reliance on this package without repo inspection | Future plan may not match actual files. | medium | high | Inspect repo/files before implementation. | WORKSTREAM-06 | UNCERTAIN / UNVERIFIED |
| RISK-13 | Stale platform/toolchain facts | Build matrix uses outdated support data. | medium | high | Re-verify official docs before acting. | WORKSTREAM-13 | FACT |
| RISK-14 | Treating assistant suggestions as user decisions | Spec book gains false requirements. | medium | high | Preserve labels and source hierarchy. | WORKSTREAM-16 | FACT |
| RISK-15 | Bad aggregation with other chat reports | Contradictions or duplicates are silently merged. | medium | high | Use IDs, labels, provenance, and conflict register. | WORKSTREAM-16 | FACT |

## 5. Recommended Re-Extraction Triggers

Re-extract or manually review this chat if:

- A future chat contradicts the GUI rebuild decision.
- New files/repo contents become available and differ from assumptions.
- The user clarifies Linux, Android, TUI, backend contract, macOS 10.9, or .NET floor.
- Platform/toolchain docs change materially.
- A future Project Spec Book promotes assistant suggestions to formal requirements.
- The original CONTENT0 prompt exact wording is needed and cannot be located.
