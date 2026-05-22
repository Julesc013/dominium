# AIDE Latest Task Packet

## PHASE

Post-workflow-law AIDE schema hardening.

## GOAL

`AIDE-WORKUNIT-SCHEMA-01` - define explicit WorkUnit, task attempt, blocker,
evidence packet, checkpoint, and promotion-report schemas that implement
`AIDE-WORKFLOW-LAW-01`.

## WHY

`AIDE-WORKFLOW-LAW-01` now defines the operating law: development is
non-blocking, while promotion is evidence-blocked. The next gap is structured
schema support so AIDE can record WorkUnits, attempts, blockers, evidence,
repair/resume paths, checkpoints, and promotion decisions without relying on
free-form prose.

## CONTEXT_REFS

- `AGENTS.md`
- `.aide/queue/current.toml`
- `contracts/aide/aide_workflow_law.v1.json`
- `.aide/policy/workflow_law.md`
- `.aide/policy/task_lifecycle.md`
- `.aide/policy/blocker_taxonomy.md`
- `.aide/policy/evidence_requirements.md`
- `docs/development/aide/AIDE_WORKFLOW_LAW_01.md`
- `docs/repo/audits/AIDE_WORKFLOW_LAW_01.md`
- `.aide/policies/work-units.yaml`
- `.aide/policies/recovery.yaml`
- `.aide/policies/branch-roles.yaml`
- `.aide/policies/promotion-rules.yaml`

## ALLOWED_PATHS

- `contracts/aide/**`
- `.aide/intake/**` only for narrow schema alignment if required
- `.aide/repair/**` only for narrow schema alignment if required
- `.aide/verification/**` only for evidence packet schema alignment if required
- `.aide/queue/**`
- `.aide/context/**`
- `.aide/reports/AIDE-WORKUNIT-SCHEMA-01-*`
- `docs/development/aide/**`
- `docs/repo/audits/AIDE_WORKUNIT_SCHEMA_01.md`
- `contracts/public_surface/**` only for provisional surface registration

## FORBIDDEN_PATHS

- no product/runtime implementation
- no package runtime
- no replay runtime
- no provider runtime
- no runtime module loader
- no Workbench shell
- no renderer/native GUI
- no gameplay/domain implementation
- no release publication
- no branch automation, force-push automation, or direct main-promotion automation

## IMPLEMENTATION

- Define schemas before automation.
- Reuse existing AIDE intake, recovery, verification, policy, and workflow-law
  vocabulary.
- Keep support claims provisional.
- Do not implement queue scheduler, merger, checkpoint runner, GitHub mutation,
  provider calls, or live branch promotion.

## VALIDATION

- JSON parse checks for touched schemas/contracts
- AIDE doctor/validate
- workflow law validator when relevant
- docs sanity
- public surface strict if public surfaces change
- dependency-direction strict if governance surfaces change substantially
- fast strict only when explicitly required by the task

## EVIDENCE

- changed files
- schemas added or updated
- validators run
- known warnings and non-goals

## NON_GOALS

- No branch execution automation.
- No remote mutation.
- No product/runtime feature work.
- No live provider/model/network calls.
- No broad Workbench UI.
- No runtime module loader.
- No package/provider/replay runtime.
- No gameplay, renderer, native GUI, or release publication.

## ACCEPTANCE

- WorkUnit, attempt, blocker, evidence, checkpoint, and promotion report shapes
  are explicit or explicitly deferred with reason.
- Schema fields align with `AIDE-WORKFLOW-LAW-01`.
- Existing AIDE fragments are extended, not replaced.
- Broad feature blockers remain visible.

## NEXT_AFTER

Expected follow-up: `AIDE-DEV-MAIN-POLICY-01`.

## OUTPUT_SCHEMA

Return compact closeout with `STATUS`, `SUMMARY`, `COMMITS`,
`CHANGED_FILES`, `VALIDATION`, `WARNINGS`, `RISKS`, and `NEXT`.

## TOKEN_ESTIMATE

- method: chars / 4, rounded up
- approx_tokens: 900
- budget_status: PASS
