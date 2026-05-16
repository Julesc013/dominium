Status: DERIVED
Last Reviewed: 2026-05-16
Supersedes: none
Superseded By: none

# Package Smoke Proof

## Status

- Phase: POST-CONVERGE-09
- Status: partial

## Package / Projection Surfaces

| Surface | Command/Tool | Result | Evidence | Notes |
| --- | --- | --- | --- | --- |
| portable projection | `apps/setup/packages/scripts/packaging/pipeline.py assemble` then `portable` | blocked | help surfaces exist | requires build output and artifact root |
| `.dompkg` package artifact | `tools/distribution/tool_pkg_pack.py` | partial | temporary docs package wrote `smoke_docs.dompkg` | temp output removed; not a release artifact |
| `.dompkg` package verify | `tools/distribution/tool_pkg_verify.py --pkg <temp>/smoke_docs.dompkg` | partial | verification returned `result: ok` | unsigned smoke package only |
| package index | `tools/distribution/tool_pkg_index.py` | not run | help surface exists | requires package directory from real package output |
| install manifest | packaging pipeline / setup model | blocked | no generated portable root | no manifest was generated in this task |
| semantic contract registry | source registry and release helpers | blocked | source registry exists under `data/registries/` | no portable root copy was generated |
| package export roots | distribution contract and docs | partial | `package_export` projection exists | no full package set was exported |
| `dist/sys` projection | CMake/package targets | blocked | CMake targets exist | build output is missing |
| `dist/pkg` artifact | `pkg_pack_all`, `pkg_verify_all`, `pkg_index_all` | blocked | CMake targets and tools exist | depends on build output |
| symbols/provenance | `build_manifest.py`, docs | blocked | help surface exists | requires package index and build metadata |
| cache/staging | docs/contract | partial | layout docs exist | no cache/staging run was executed |
| bundle/diagnostic layout | docs/contract | partial | layout docs exist | no bundle artifact was generated |

## Artifact Policy

- No generated package bytes are committed.
- The POST-CONVERGE-09 `.dompkg` smoke output was created under `%TEMP%`, verified, listed, and removed.
- Any future generated projection or package output must remain local/generated unless a release task explicitly promotes it.
- Package support status follows `docs/release/PACKAGING_MATRIX.md` and `contracts/release/component_matrix.contract.toml`.

## Readiness For Universal Reality Enforcement

CONTRACT-00 should not proceed yet as a clean successor to post-CONVERGE proof. Build, product boot, and portable projection proof remain partial or blocked. The next step should be targeted build/package/projection remediation, then a rerun of POST-CONVERGE-08 and POST-CONVERGE-09.
