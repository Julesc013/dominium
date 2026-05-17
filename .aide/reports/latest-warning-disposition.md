# Latest Warning Disposition

Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

## TEST-PERF-00

- Focused tuple RepoX still fails.
- Canonical `ctest --preset verify -N` discovered 0 tests before configure refresh, then 493 tests after `cmake --preset verify`.
- CTest smoke labels now discover 57 tests after `dom_add_testx` label repair and reconfigure.
- Full CTest, product boot proof, package proof, and portable projection proof remain not run by TEST-PERF-00.
- Full CTest remains a promotion gate rather than the normal post-change feedback path.

## POST-CONVERGE-10L

- Focused RepoX remains 51 failures / 5 warnings.
- The 12 distribution/product target failures are classified as missing portable projection wrapper/proof surfaces under `dist/bin`.
- Missing product/projection proof remains blocking and was not converted into a warning.

## POST-CONVERGE-10M

- Focused RepoX remains expected-failing but improved to 23 failures / 5 warnings.
- The safe retired-domain stale rule path family was fixed, not converted into warnings.
- Two source import blockers remain for MW-4 fixture evaluation through stale `embodiment.*` lazy imports.

## POST-CONVERGE-10N

- Focused RepoX remains expected-failing but improved to 20 failures / 5 warnings.
- `INV-IDENTITY-FINGERPRINT` and `INV-TOOL-VERSION-MISMATCH` hard failures were fixed by canonical evidence refresh, not converted into warnings.
- `INV-AUDITX-OUTPUT-STALE` remains a warning because broad AuditX output regeneration was out of scope.
- Four `WARN-GLOSSARY-TERM-CANON` warnings in generated/historical audit evidence remain warnings and were not rewritten.
- Product boot proof, package proof, release proof, portable projection proof, build, and full CTest were not run by scope.

## POST-CONVERGE-10O

- Focused RepoX remains expected-failing at 20 failures / 5 warnings.
- The remaining hard failures were not accepted as warnings.
- POST-CONVERGE-11 remains blocked because real non-proof governance/source-policy failures remain.
- The warning candidates are still `INV-AUDITX-OUTPUT-STALE` and four generated/historical glossary warnings.
- Product boot proof, package proof, release proof, portable projection proof, build, and full CTest were not run by scope.

## POST-CONVERGE-11

- Focused RepoX remains expected-failing at 20 failures / 5 warnings.
- The remaining hard failures were not accepted as warnings.
- Product binaries were not inspected or executed because the RepoX readiness gate failed.
- POST-CONVERGE-12 remains blocked because product boot proof did not run.
- Product boot proof, package proof, release proof, portable projection proof, build, and full CTest were not run by scope.

## POST-CONVERGE-12

- Product boot proof remains blocked and was not accepted as sufficient portable projection input.
- No projection root was generated and no projection validator was run.
- The remaining RepoX hard failures were not accepted as warnings.
- RELEASE-00 remains blocked until RepoX/product boot/projection gates are resolved or explicitly accepted.

## Closeout Remediation

- Focused RepoX now passes through both direct RepoX and canonical CTest focused `inv_repox_rules`.
- Tracked RepoX proof/profile evidence records zero warnings and zero failures.
- Native product command smoke passes for `setup`, `launcher`, `client`, `server`, and `tools` on `--help`, `--version`, `--status`, and `--smoke`.
- CTest smoke passes 57/57.
- Remaining warnings are operational, not semantic RepoX failures: full `cmake --build --preset verify` was not completed because the verification phase timed out, and portable projection proof has not yet been generated.

## Portable Projection Closeout

- Local ignored portable projection generation now completes under `.dominium.local/projections/post-converge-12/`.
- Portable projection validation reports `proof_status: proven` with no blockers.
- The projection tree includes the required portable roots/manifests and native `setup.exe`, `launcher.exe`, `client.exe`, `server.exe`, and `tools.exe` binaries.
- Remaining warnings are release-process scope: no public package, installer, tag, GitHub release, or full promotion CTest was run.

## RELEASE-00

- Internal Pilot Release 0 local staging passes validation under `.dominium.local/releases/internal-pilot-0`.
- The staging root includes the projection tree, internal pilot manifest, provenance, checksums, proof reports, warning ledger, runbook, and rollback notes.
- The strict validator reports no blockers and verifies 4718 checksum entries.
- Remaining warnings are operational release scope: no public package, installer, tag, GitHub release, upload, or full promotion CTest was run.
- The generated release staging root is ignored/local and was not committed.

## MOVE-BULK-00-PLAN

- Batch A is the only gate-ready subset in the global bad-root migration plan.
- Batches B-G remain warning/deferred because they require ownership, identity, authority, import, runtime, ABI, or build gates.
- `libs/CMakeLists.txt` is explicitly blocked from direct movement until CMake/build target rewiring is approved.
- No full CTest, full eval, CMake configure/build, product binary execution, package/release generation, or projection regeneration was run by scope.
- Apply remains unauthorized until `MOVE-BULK-00-GATE`.

## MOVE-BULK-00-GATE

- Batch A is authorized with mandatory safe-subset apply behavior.
- Batches B-G remain deferred for ownership, identity, authority, import, runtime, ABI, or build gates.
- Batch H remains blocked until prior apply/proof completion.
- Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, and projection regeneration remain out of scope for the gate.
- Feature work remains blocked.

## BASELINE-00

- RELEASE-00 is frozen as the structural regression baseline at HEAD `0b631fc5f09f3d927a54e8312976b926d111a72e`.
- Full promotion CTest and full eval remain not run.
- No public package, installer, tag, GitHub release, upload, or release publication was created.
- Generated release, projection, build, and local AIDE outputs remain ignored proof evidence and must not be committed.
- Release staging manifest provenance records stager-time commits earlier than the BASELINE-00 freeze HEAD because the generated release tree was not regenerated by this baseline task.
- DOE-00 and feature work remain deferred until MOVE-FAMILY cleanup and post-restructure proof pass.

## MOVE-FAMILY-00-PLAN

- Family apply readiness is blocked, not warning-only: no remaining target-family file is safe enough to include in an apply-ready plan without active-module ownership and consumer migration work.
- `governance/`, `meta/`, `performance/`, and `validation/` are active Python/tooling import surfaces.
- `ide/manifests/**` is machine-readable IDE projection metadata with CMake, script, docs, and registry consumers.
- Full CTest, full eval, CMake configure/build, product binary execution, package generation, and release generation remain not run by scope.
- No files were moved, deleted, renamed, or rewritten.

## MOVE-FAMILY-00-REFINE

- Ownership refinement is warning-only for this task but remains blocking for direct apply.
- `ide/manifests/**` has a clear future owner under `contracts/projections`, but still needs a contract/validator/reference plan before movement.
- `validation/**`, `meta/identity/**`, `meta/stability/**`, and `governance/**` require temporary shim/import planning.
- semantic/runtime `meta/**` and product/runtime `performance/**` remain preserve-current.
- No files were moved, deleted, renamed, or rewritten.

## MOVE-FAMILY-00B-PLAN

- The IDE manifest plan is gate-ready but warning-bearing because `contracts/projections/ide/**` is planned, not existing.
- The plan includes 3 moves and no file-level blockers.
- Apply remains unauthorized until `MOVE-FAMILY-00B-GATE`.
- Generated `ide/manifests/*.projection.json` references are warning-only if they remain classified as generated-output references, not tracked source authority.
- Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, portable projection regeneration, and internal pilot release regeneration remain not run by scope.
- No files were moved, deleted, renamed, or rewritten.

## MOVE-FAMILY-00B-GATE

- Gate result is PASS_WITH_WARNINGS, not BLOCKED.
- The absent `contracts/projections/ide/**` target directory is warning-only because the reviewed plan creates it during apply and no target collision exists.
- Historical/audit `ide/manifests/**` references remain warning-only and should not be rewritten by the apply task.
- Generated-output `ide/manifests/*.projection.json` references remain warning-only if the apply task preserves them as generated/local output references.
- Strict validators emitted known TOML fallback-parser warnings while passing.
- Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, portable projection regeneration, and internal pilot release regeneration remain not run by gate scope.
- No files were moved, deleted, renamed, or rewritten.

## MOVE-FAMILY-00B-APPLY

- Apply result is PASS_WITH_WARNINGS, not BLOCKED.
- Strict validators emitted known TOML fallback-parser warnings while passing.
- Generated-output references to `ide/manifests/*.projection.json` remain warning-only when they point at ignored/local projection output, not tracked source authority.
- Historical/audit/planning references to old `ide/manifests/**` paths remain warning-only by design.
- Focused RepoX initially failed on three touched planning docs missing the full four-line status header; metadata-only header repairs were applied and the rerun passed.
- Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, portable projection regeneration, and internal pilot release regeneration remain not run by apply scope.

## MOVE-FAMILY-00B-PROOF

- Proof result is PASS_WITH_WARNINGS, not BLOCKED.
- Historical/audit/planning/root-recycling/AIDE references to old `ide/manifests/**` paths remain warning-only by design.
- Generated-output references to `ide/manifests/*.projection.json` remain warning-only because they describe ignored local projection output, not tracked source authority.
- Strict validators emitted known TOML fallback-parser warnings while passing.
- Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, portable projection regeneration, and internal pilot release regeneration remain not run by proof scope.
- No files were moved, deleted, renamed, or rewritten by the proof task.

## MOVE-FAMILY-00C-PLAN

- Result is BLOCKED by design, not an unexpected validator failure.
- No active-tool batch is gate-ready because current public imports reach `validation`, `meta.identity`, `meta.stability`, and `governance` from release, runtime, AppShell, tools, AuditX, RepoX, TestX, and tests.
- `performance/**` remains preserve-current because product/client/game/runtime consumers import it directly.
- semantic/runtime `meta/**` remains preserve-current until a separate runtime/domain ownership plan exists.
- Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, portable projection regeneration, and internal pilot release regeneration remain not run by planning scope.
- No files were moved, deleted, renamed, import-rewritten, reference-rewritten, or shimmed by the plan.

## MOVE-FAMILY-00C-A-PLAN

- Result is PASS_WITH_WARNINGS, not BLOCKED.
- Future apply remains high risk because it will move active Python implementations and create temporary shims.
- Temporary old-import callers remain warning-only when they are exactly the allowlisted runtime, compatibility, release/security/lib, or deferred governance consumers.
- New old-import usage after apply must be blocking once the planned static check exists.
- `validation` and `meta` exceptions cannot retire after the first shim apply because shim files and broader `meta/**` material remain.
- The prompt-specified `aide(move)` commit subject is not accepted by local AIDE commit policy. Because amend/rebase/reset are forbidden, the policy mismatch is handled by a follow-up `audit(...)` evidence commit.
- Commit-policy correction commits use the local `audit(...)` type and `Changed:` changelog category required by AIDE policy.
- Full CTest, full eval, CMake configure/build, product binary execution, package/release generation, portable projection regeneration, and internal pilot release regeneration remain not run by planning scope.
- No files were moved, deleted, renamed, import-rewritten, reference-rewritten, or shimmed by the plan.

## MOVE-BULK-01-APPLY

- Batch A was partially applied by safe subset.
- 283 planned files were skipped because exact active/current references remain.
- Skipped references were not accepted as stale; skipped files remain at their old paths.
- The first apply commit included the required trailer text, but AIDE commit check parsed only the final trailer because the trailers were separated by blank `git commit -m` paragraphs. A follow-up evidence commit records the disposition because amend is forbidden.
- No reference rewrites, import rewrites, shims, exception retirements, full CTest, full eval, CMake build, package/release generation, projection generation, or product binaries were run by scope.
