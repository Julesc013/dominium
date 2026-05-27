# Verification and Audit — Dominium README Ports Determinism

## 1. Audit of the Original Context Transfer Packet

| Issue | Severity | Correction applied | Residual risk |
| --- | --- | --- | --- |
| Original packet lacked stable IDs for every register item. | medium | Normalized all workstreams, decisions, tasks, constraints, questions, artifacts, risks, rejected options, and verification items. | Low. |
| Original packet identified /ports ambiguity but did not package it as an ID-linked open question. | high | Created QUESTION-02, TASK-03, RISK-03, VERIFY-04. | Still needs user confirmation. |
| Original packet included extensive context but not downloadable files. | medium | Created Markdown/YAML files and ZIP package. | None if downloads persist. |
| OS/2 contradiction was found in prior packet but not in earlier assistant review. | high | Added QUESTION-01, TASK-02, RISK-02, VERIFY-05. | Needs README patch or user decision. |
| Repository state was unverified. | high | Marked README/spec files as UNCERTAIN / UNVERIFIED and created VERIFY-01/02/03. | Requires actual repo inspection. |
| Prompt artifacts were preserved but not normalized. | medium | Added ARTIFACT IDs and artifact ledger. | Exact prompt texts and final README snapshot are included in the full chat report appendix. |
| Spec future work was inferred, not explicitly requested in all cases. | medium | Labelled spec workstream and related tasks as INFERENCE where appropriate. | Future assistant must not treat inferred tasks as accepted user decisions. |
| Final README snapshot is very long. | low | Represented as active artifact and summarized; noted need to verify actual file. | Full original chat contains full text; repo verification is better source. |

## 2. Final Reliability Assessment

* Completeness rating: 4/5.
* Reliability rating: 4/5.
* Aggregation readiness rating: 4/5.
* Main remaining uncertainty sources:
  * Actual repository files were not inspected.
  * Metadata-only `/ports` may not fully satisfy the user's wording.
  * OS/2 platform status is unresolved.
  * Referenced spec files were not inspected.
  * Exact implementation algorithms for RNG/hash/TLV/content hashes were not established.

## 3. Manual Verification Checklist

| ID | Item requiring verification | Why verification is needed | Suggested verification source/type | Priority | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- |
| VERIFY-01 | Actual repository README.md matches final pasted README. | Final pasted text may not be committed or may have changed. | Repository file/diff. | high | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |
| VERIFY-02 | /docs/spec/DIRECTORY_CONTRACT.md exists and matches README source-tree rules. | README says it is authoritative; contents not inspected. | Repository file. | high | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-03 | /docs/spec/MILESTONES.md exists and matches status claims. | README references it for concrete implementation status. | Repository file. | medium | WORKSTREAM-05 | UNCERTAIN / UNVERIFIED |
| VERIFY-04 | User accepts metadata-only /ports rather than no /ports directory. | User's wording may reject any separate ports directory. | User confirmation. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-05 | OS/2 platform status. | Intro and Section 9 conflict. | User decision or platform target list. | high | WORKSTREAM-01 | FACT |
| VERIFY-06 | No engine/runtime source files live under /ports if retained. | Needed to enforce metadata-only semantics. | Repository tree/CI. | high | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| VERIFY-07 | Capability descriptors are declarative and cannot alter canonical behavior. | Prevents degradation flowing upstream. | Spec/build review. | medium-high | WORKSTREAM-02 | INFERENCE |
| VERIFY-08 | Build numbers/timestamps cannot enter engine-controlled formats or simulation state. | README demands diagnostic-only metadata. | Build scripts/generated file review. | medium | WORKSTREAM-03 | UNCERTAIN / UNVERIFIED |
| VERIFY-09 | Tools/renderers cannot feed float-derived values into engine state/formats. | Section 2.1 boundary requires enforcement. | Code review/dataflow/spec. | medium-high | WORKSTREAM-03 | INFERENCE |
| VERIFY-10 | RNG streams are inaccessible to debug/UI/render layers outside deterministic phases. | Prevent desyncs. | API/spec review. | medium-high | WORKSTREAM-03 | INFERENCE |
| VERIFY-11 | Data format specs avoid compiler packing dependence. | README bans platform-specific packing pragmas. | Format spec and C implementation review. | medium | WORKSTREAM-04 | INFERENCE |
| VERIFY-12 | content.lock exact-match and reconciliation behavior are specified. | Avoid ad hoc user-friendly bypasses. | Content/loader spec. | medium | WORKSTREAM-04 | INFERENCE |
| VERIFY-13 | Future Codex output contains no duplicate sections and preserves unified-ports semantics. | Codex previously introduced duplicate block. | Manual diff/review. | ongoing | WORKSTREAM-06 | FACT |

## 4. Residual Risk Register

| ID | Risk / failure mode | Consequence | Likelihood | Severity | Mitigation | Related workstream | Label |
| --- | --- | --- | --- | --- | --- | --- | --- |
| RISK-01 | Codex may introduce duplicated sections or broad rewrites again. | Loss of coherence and hidden contradictions. | medium | medium | Prompts must explicitly forbid duplication and out-of-scope edits. | WORKSTREAM-06 | FACT |
| RISK-02 | OS/2 intro mention conflicts with normative Section 9 matrix omission. | Platform support ambiguity. | high | medium | Patch README or confirm OS/2 status. | WORKSTREAM-01 | FACT |
| RISK-03 | Metadata-only /ports may not satisfy user's 'no separate directory' intent. | Future directory contract may encode wrong structure. | medium | high | Confirm with user before directory spec work. | WORKSTREAM-02 | UNCERTAIN / UNVERIFIED |
| RISK-04 | Future contributor interprets /ports as source-code location. | Port forks could reappear. | medium | high | Directory contract and CI should forbid source/behavior under /ports. | WORKSTREAM-02 | INFERENCE |
| RISK-05 | Capability degradation could become behavior by proxy if descriptors are too powerful. | Platform limitations may flow upstream indirectly. | medium | high | Keep descriptors declarative and non-semantic; define strict schema. | WORKSTREAM-02 | INFERENCE |
| RISK-06 | Future assistant overcompresses determinism to 'no floats anywhere'. | Unnecessary constraints on renderers/tools. | medium | medium | Preserve Section 2.1 boundary exactly. | WORKSTREAM-03 | INFERENCE |
| RISK-07 | Future assistant treats README as normative over specs. | Spec drift and false authority. | medium | medium | Preserve README descriptive/spec normative hierarchy. | WORKSTREAM-01 | FACT |
| RISK-08 | Build metadata accidentally leaks into engine-controlled files or hashes. | Breaks reproducibility. | low-medium | high | Audit build system and generated files. | WORKSTREAM-03 | INFERENCE |
| RISK-09 | Debug/UI/rendering accidentally advance RNG streams. | Invisible desyncs. | medium | high | Restrict engine RNG API to deterministic tick phases. | WORKSTREAM-03 | INFERENCE |
| RISK-10 | Packed C struct wording may lead to compiler-packing reliance. | Cross-platform disk layout bugs. | medium | medium | Clarify canonical layout independent of compiler pragmas. | WORKSTREAM-04 | INFERENCE |
| RISK-11 | content.lock reconciliation process undefined. | Users may be blocked without recovery path or implement ad hoc bypasses. | medium | medium | Define reconciliation tooling and policy. | WORKSTREAM-04 | INFERENCE |
| RISK-12 | README-level decisions not transferred into normative specs. | Future code may implement inconsistent behavior. | medium | high | Create/update specs after README stabilizes. | WORKSTREAM-05 | INFERENCE |
| RISK-13 | Future Codex prompt may reintroduce rejected options due to missing context. | Repeated work and architecture regression. | medium | medium | Use this package as bootstrap and include rejected options in prompts. | WORKSTREAM-06 | INFERENCE |
| RISK-14 | State-transfer report may be treated as proof of repository state. | New assistant may assume changes were committed. | medium | medium | Verify actual files before editing or relying on repo state. | WORKSTREAM-01 | UNCERTAIN / UNVERIFIED |

## 5. Recommended Re-Extraction Triggers

Re-extract or manually review this chat if:
- actual `README.md` differs materially from the final pasted README;
- the user clarifies `/ports` should not exist at all;
- OS/2 support is resolved elsewhere;
- normative specs already exist and conflict with this README;
- future chats reverse or refine the ports architecture;
- Codex output later changes determinism, platform, or data-format semantics.
