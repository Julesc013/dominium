Status: TEMPLATE
Version: 1.0.0
Last Reviewed: 2026-02-14
Compatibility: Use with `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

# Skill Template: repo_audit

## Purpose
Run a targeted repository audit for canon drift, invariant breaks, and contract/test obligations.

## Constraints
- Prioritize invariant violations and regressions over style comments.
- Do not propose architecture changes not required by discovered violations.
- Avoid broad refactors unless they are required to satisfy canon.
- Keep findings evidence-based with file/path references.

## Checklist
1. Load canon and glossary terms.
2. Identify changed paths and impacted contracts/invariants.
3. Run profile baseline:
   - `tools/xstack/run fast`
   - inspect `tools/xstack/out/fast/latest/report.json`
4. Check for forbidden patterns:
   - mode flags
   - non-process mutation
   - observer/renderer/truth boundary violations
   - nondeterministic authoritative behavior
   - renderer imports of TruthModel headers (`repox.renderer_truth_import`)
5. Check schema/compat obligations where contracts changed.
6. Check TestX/RepoX evidence expectations for changed invariants.
7. Emit findings ordered by severity.
8. Emit unresolved risks and TODO follow-ups.

## Output Format
- Findings (severity, file, invariant, impact, suggested fix).
- Assumptions/open questions.
- Residual risk and test gap list.

## Example Invocation
```text
Use skill.repo_audit on these changed files:
- docs/contracts/*
- docs/architecture/*
Audit for constitution/glossary drift and missing determinism obligations.
Run: tools/xstack/run strict
Inspect: tools/xstack/out/strict/latest/report.json
```

## TODO
- Add automated invariant-ID extraction from changed files.
- Add machine-readable output schema for audit findings.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/canon/glossary_v1.md`
- `AGENTS.md`
- `docs/architecture/truth_perceived_render.md`
