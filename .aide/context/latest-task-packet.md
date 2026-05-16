
# AIDE Latest Task Packet

## PHASE

POST-CONVERGE-10K - Contract Registry Acceptance Backlog Remediation

## GOAL

Reduce the focused RepoX contract registry acceptance backlog without changing contract/schema semantics or product/runtime behavior.

## WHY

POST-CONVERGE-10J left focused RepoX at 60 failures / 5 warnings, with contract registry acceptance as the next safe family. Current synced local reproduction started at 59 failures / 5 warnings because the transient locklist-frozen failure was gone.

## CURRENT RESULT

PARTIAL. `INV-NEW-CONTRACT-REQUIRES-ENTRY` is reduced from 9 to 0. Focused tuple RepoX is now 51 failures / 5 warnings and remains blocking.

## CONTEXT_REFS

- `.aide/reports/POST-CONVERGE-10K-status.md`
- `.aide/reports/POST-CONVERGE-10K-contract-registry-findings.json`
- `.aide/reports/POST-CONVERGE-10K-repox-before-after.json`
- `docs/repo/audits/POST_CONVERGE_10K_CONTRACT_REGISTRY_ACCEPTANCE.md`
- `data/registries/semantic_contract_registry.json`

## ALLOWED_PATHS

- contract/registry acceptance metadata directly implicated by focused RepoX
- `.aide/reports/**`
- `.aide/context/**`
- `.aide/ledgers/migration_ledger.jsonl`
- post-converge status docs

## FORBIDDEN_PATHS

- product/runtime/source behavior changes
- root moves, deletes, renames, aliases, move maps, salvage maps, or exception retirement
- product boot proof, package proof, release proof, portable projection proof, full eval, or full CTest

## VALIDATION

AIDE doctor/validate/test/selftest/tools/roots/repo passed; strict repo/root/distribution/component validators passed; docs/build/UI/ABI checks passed; registry JSON and semantic registry validation passed; focused tuple RepoX remains failing by known remaining families.

## NEXT

Recommended next task: `POST-CONVERGE-10L - Distribution Descriptor and Product Proof Blocker Classification`.
