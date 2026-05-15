# DOM-AIDE-02 Wrapper Selection

## Evidence Inspected

- `AGENTS.md`
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
- `docs/planning/AUTHORITY_ORDER.md`
- `docs/planning/MERGED_PROGRAM_STATE.md`
- `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`
- `docs/planning/GATES_AND_PROOFS.md`
- `docs/planning/POST_PI_EXECUTION_PLAN.md`
- `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`
- `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`
- `specs/reality/SPEC_*.md`
- `data/reality/*.json`
- `data/planning/final_prompt_inventory.json`
- `data/planning/dependency_graph_post_pi.json`
- `.aide/context/latest-task-packet.md`
- `.aide/context/latest-review-packet.md`
- `.aide/context/dominium-doctrine-refs.md`
- `.aide/queue/DOMINIUM-AIDE-FRESH-PREFLIGHT-01/evidence/q50-readiness.md`
- `.aide/queue/DOMINIUM-AIDE-STABLE-INSTALL-01/evidence/q51-readiness.md`
- `.aide/queue/DOMINIUM-AIDE-TOOL-ABSORPTION-01/evidence/q52-readiness.md`
- `.aide/queue/DOMINIUM-AIDE-ROOT-RECYCLING-01/evidence/q53-readiness.md`
- `.aide/queue/DOMINIUM-AIDE-OPERATING-BASELINE-01/evidence/baseline-summary.md`
- `.aide/queue/DOMINIUM-AIDE-OPERATING-BASELINE-01/evidence/warning-disposition.md`
- `.aide/queue/DOMINIUM-AIDE-BASELINE-REPAIR-01/evidence/xstack-integration.md`
- `.aide/queue/DCHECK-01-dominium-aide-operating-baseline-audit/audit-report.md`
- `.aide/queue/DCHECK-01-dominium-aide-operating-baseline-audit/readiness-and-next-plan.md`
- `.aide/reports/dominium-tool-preservation-plan.md`
- `.aide/reports/dominium-tool-capability-map.md`
- `.aide/tools/latest-tool-inventory.md`
- `.aide/tools/latest-tool-inventory.json`
- `.aide/tools/latest-tool-classification.md`
- `.aide/tools/latest-tool-classification.json`
- `.aide/tools/latest-tool-wrap-plan.md`
- `.aide/tools/latest-tool-wrap-plan.json`
- `.aide/tools/xstack-integration-contract.md`
- `.aide/tools/xstack-wrapper-registry.md`

## Existing Inventories And Wrapper Plans

Current AIDE tool inventory exists under `.aide/tools/latest-tool-inventory.*`
and records 3000 tool candidates, 206 validate-capability candidates, 858
unknown candidates, `execution_allowed: false`, `no_apply: true`, no deletion,
no rename, and no migration.

Current AIDE tool classification exists under
`.aide/tools/latest-tool-classification.*` and records 858 unknown candidates,
443 low-risk candidates, 1543 medium-risk candidates, 158 release-risk
candidates, 6 high-risk candidates, 5 destructive candidates, and 2
security-risk candidates.

Current AIDE wrap-plan evidence exists under
`.aide/tools/latest-tool-wrap-plan.*` and
`.aide/tools/latest-tool-adapter-map.*`. These are dry-run, no-apply,
execution-disabled plan surfaces.

Current XStack integration evidence exists under
`.aide/tools/xstack-integration-contract.*` and
`.aide/tools/xstack-wrapper-registry.*`. It models XStack, AuditX, RepoX,
TestX, BuildX-like surfaces, and FAST/STRICT/FULL validation profiles, but all
legacy execution remains disabled.

## Candidate Validator Families Considered

| Candidate | Disposition | Reason |
|---|---|---|
| `tools validate` family | selected | Lowest-risk current validator; checks AIDE tool inventory/wrap-plan evidence and enforcement flags without running discovered tools. |
| `repo validate` family | deferred | Safe enough to run as validation, but broader repo scope still reports 1669 unknown file classifications. |
| `roots validate` family | deferred | Safe no-apply validation, but root recycling remains high-risk/mixed and no root move is approved. |
| `quality validate` family | deferred | Useful, but tied to large quality ledgers and broader quality reports; not the smallest first wrapper. |
| `xstack validate` family | deferred | Supported and safe as AIDE-local validation, but underlying legacy families are authority/build-sensitive and should remain second-wave. |
| docs sanity validators | deferred | Potentially low-risk, but less clearly represented as current wrapper-plan evidence than the tools validator family. |
| broad XStack FAST/FULL, full CTest, build, package, release, full eval | rejected | Outside DOM-AIDE-02 scope, can write build/package/release/cache outputs, timeout, or execute broad legacy tools. |

## Selected Family

Selected family: `aide_tool_wrapper_plan_validator`

Current command contract: `py -3 .aide/scripts/aide_lite.py tools validate`

Supporting evidence refresh:

- `py -3 .aide/scripts/aide_lite.py tools classify`
- `py -3 .aide/scripts/aide_lite.py tools wrap-plan`

## Safety Reasoning

This family is safe to wrap first because it validates AIDE evidence and policy
shape instead of invoking legacy validators. It checks that all tool records and
wrapper plans keep execution disabled, apply disabled, and deletion/rename/
migration unapproved. It has no provider/model calls, no network calls, no build
outputs, no package/release outputs, and no product/runtime behavior impact.

## Blocker Reasoning

Execution remains disabled by default. Unknown and high-risk candidates are
evidence to preserve, not commands to execute. Before any executable wrapper is
enabled, a future task must prove command line, input/output roots, timeout,
side effects, failure behavior, and validation evidence, then receive human
promotion.

## Expected Next Implementation Step

The next implementation step is not code execution. It is review of this
contract, followed by a narrowly scoped future task that selects one concrete
legacy command and proves a report-only adapter contract before enabling
execution.
