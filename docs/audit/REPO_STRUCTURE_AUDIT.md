Status: DERIVED
Last Reviewed: 2026-02-09
Supersedes: none
Superseded By: none
Purpose: Repository structure audit and consolidation report
Authority: NON-CANONICAL

# Repository Structure Audit

- Date: 2026-02-09
- Tracked files audited: 5918
- Root directories audited: 29
- Root files audited: 22

## Top-Level Directory Audit

| Directory | Tracked | Listed In REPO_INTENT | Status | Recommendation |
|---|---|---|---|---|
| `.github` | yes | yes | Evolving | keep |
| `.vs` | no | yes | Evolving | local_generated_ok |
| `.vscode` | yes | yes | Evolving | keep |
| `app` | yes | yes | Evolving | keep |
| `build` | no | yes | Quarantined | local_generated_ok |
| `ci` | no | yes | Evolving | local_generated_ok |
| `client` | yes | yes | Evolving | keep |
| `cmake` | yes | yes | Evolving | keep |
| `data` | yes | yes | Frozen (pack formats), Evolving (content) | keep |
| `dist` | no | yes | Evolving | local_generated_ok |
| `docs` | yes | yes | Frozen/Evolving per taxonomy | keep |
| `engine` | yes | yes | Frozen (public contracts), Evolving (internals) | keep |
| `game` | yes | yes | Frozen (public contracts), Evolving (internals) | keep |
| `ide` | yes | yes | Evolving | keep |
| `labs` | yes | yes | Quarantined | keep |
| `launcher` | yes | yes | Evolving | keep |
| `legacy` | yes | yes | Archived | keep |
| `libs` | yes | yes | Frozen (contracts), Evolving (impl) | keep |
| `out` | no | yes | Quarantined | local_generated_ok |
| `repo` | yes | yes | Quarantined | keep |
| `schema` | yes | yes | Frozen/Evolving per `SCHEMA_STABILITY.md` | keep |
| `scripts` | yes | yes | Evolving | keep |
| `sdk` | no | yes | Evolving | local_generated_ok |
| `server` | yes | yes | Frozen (public contracts), Evolving (internals) | keep |
| `setup` | yes | yes | Evolving | keep |
| `tests` | yes | yes | Evolving | keep |
| `tmp` | no | yes | Quarantined | local_generated_ok |
| `tools` | yes | yes | Evolving | keep |
| `updates` | yes | yes | Evolving | keep |

## Root File Audit

| File | Tracked | Kind | Recommendation |
|---|---|---|---|
| `.dominium_build_number` | no | generated_build_counter | remove_from_root_or_keep_ignored |
| `.gitattributes` | yes | build_governance_contract | keep_root_canonical |
| `.gitignore` | yes | build_governance_contract | keep_root_canonical |
| `CHANGELOG.md` | yes | root_entry_document | keep_but_link_to_canonical_docs_only |
| `CMakeLists.txt` | yes | build_governance_contract | keep_root_canonical |
| `CMakePresets.json` | yes | build_governance_contract | keep_root_canonical |
| `CODE_CHANGE_JUSTIFICATION.md` | yes | root_entry_document | keep_but_link_to_canonical_docs_only |
| `CONTRIBUTING.md` | yes | root_entry_document | keep_but_link_to_canonical_docs_only |
| `DOMINIUM.md` | yes | root_entry_document | keep_but_link_to_canonical_docs_only |
| `GOVERNANCE.md` | yes | root_entry_document | keep_but_link_to_canonical_docs_only |
| `LICENSE.md` | yes | root_entry_document | keep_but_link_to_canonical_docs_only |
| `MODDING.md` | yes | root_entry_document | keep_but_link_to_canonical_docs_only |
| `README.md` | yes | root_entry_document | keep_but_link_to_canonical_docs_only |
| `SECURITY.md` | yes | root_entry_document | keep_but_link_to_canonical_docs_only |
| `VERSION_CLIENT` | yes | version_contract | keep_root_canonical |
| `VERSION_ENGINE` | yes | version_contract | keep_root_canonical |
| `VERSION_GAME` | yes | version_contract | keep_root_canonical |
| `VERSION_LAUNCHER` | yes | version_contract | keep_root_canonical |
| `VERSION_SERVER` | yes | version_contract | keep_root_canonical |
| `VERSION_SETUP` | yes | version_contract | keep_root_canonical |
| `VERSION_SUITE` | yes | version_contract | keep_root_canonical |
| `VERSION_TOOLS` | yes | version_contract | keep_root_canonical |

## Findings

- Root shim candidates: 0
- Missing root-doc references: 0
- Forbidden legacy gating tokens outside docs: 0

## Consolidation Decisions

- Root source module shims are forbidden and blocked by RepoX (`INV-ROOT-MODULE-SHIM`).
- Runtime source lives under product/library roots only (`engine`, `game`, `client`, `server`, `launcher`, `setup`, `libs`, `tools`, `app`).
- Root generated folders (`build`, `out`, `dist`, `tmp`, `.vs`, `ci`, `sdk`) remain local and untracked.
- Root documentation must point to existing canonical docs; broken links are remediation items.

## Inventory Artifact

- Full per-file inventory is written to `docs/audit/REPO_STRUCTURE_AUDIT.json`.
