# DOM-AIDE-02 Blockers

## Blocking Issues

No blocking issue prevents creation of the provisional wrapper contract.

Executable wrapper enablement remains blocked until a future reviewed task
proves the command line, inputs, outputs, side effects, timeout, and failure
handling for a concrete underlying validator.

## Non-Blocking Warnings

- `repo validate` reports 1669 unknown file classifications.
- The current tool classification reports 858 unknown tool candidates.
- The current tool classification reports 171 destructive, high, release, or
  security-risk candidates.
- Full `eval run` is timeout-prone and remains deferred.
- No refactor move, salvage, or active path-alias map is approved or applied.
- `.aide/reports/file-quality-ledger.json` is large and remains a tracked
  advisory warning.
- GitHub/release outputs remain advisory only.
- Latest review-packet/controller references can warn during AIDE validation and
  remain non-blocking under the current baseline.
- `review-pack` still marks refreshed `.aide/tools/**` outputs as unknown in
  generated review evidence even though DOM-AIDE-02 allows them; this is a
  diff-scope recognition warning, not a product/source scope change.

## Deferred Risks

- Broad XStack FAST/FULL, full CTest, build, package, release, and full eval
  validation remain outside this task.
- XStack/AuditX/RepoX/TestX are preserved as evidence assets, but direct legacy
  execution remains disabled.
- Future wrapper implementation could accidentally promote legacy commands too
  early unless it preserves the no-apply review gate.
- Tool inventory/classification counts may shift after future tracked `.aide/**`
  wrapper contracts are committed and inventoried.

## Unknown Classifications

Unknown file and tool classifications are review inputs, not cleanup
authorization. Unknowns must be inventoried and classified before any execution,
rename, move, retirement, or migration plan is considered.

## Tool Execution Blockers

- `execution_allowed` remains false.
- `apply_allowed` remains false.
- `unknown_tools_allowed` remains false.
- Network, provider/model calls, build outputs, package outputs, release outputs,
  and product/runtime mutation are not allowed.
- No executable wrapper code was created under `tools/**`, `scripts/**`, CMake,
  CI, or product/source roots.

## Why Unknown Tools Are Preserved But Not Executed

Unknown tools may encode useful validation knowledge, project history, or
operator intent. Deleting or renaming them before wrappers exist would lose
evidence and break auditability. Executing them before side effects are known
could write caches, generated reports, build outputs, release artifacts, or
product/runtime state. DOM-AIDE-02 therefore preserves unknown tools as evidence
while blocking execution.

## What Must Be True Before Execution Wrappers Can Be Enabled

- A concrete underlying command is selected from classified evidence.
- The command has a stable AIDE contract.
- Inputs, output roots, side effects, timeout, environment requirements, and
  failure handling are documented.
- The command is proven report-only or read-only in a scoped validation run.
- Allowed output paths are limited to reviewed `.aide/**` evidence or explicitly
  approved roots.
- Human review promotes `execution_allowed` for that specific wrapper.

## What Must Be True Before Old Tool Renaming Can Begin

- Useful checks are available behind AIDE adapters.
- Reference inventory and migration evidence exist.
- No product/source/doctrine/tool root behavior is changed silently.
- Compatibility and historical names remain traceable.
- A reviewed migration/retirement task explicitly approves any rename, move, or
  reference update.
