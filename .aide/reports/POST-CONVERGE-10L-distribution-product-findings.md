# POST-CONVERGE-10L Distribution/Product Findings

Status: DERIVED
Last Reviewed: 2026-05-16

## Summary

Checked 12 focused RepoX failures in the distribution/product-proof family:

- `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR`: 7 failures
- `INV-NO-ADHOC-MAIN`: 5 failures

All 12 target failures are real missing `dist/bin` wrapper/projection surfaces. They were not safe to fix by adding dummy files, removing product aliases, or changing registry product names.

## Findings

| Path | Rule | Classification | Action |
| --- | --- | --- | --- |
| `dist/bin/client` | `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | `portable_projection_proof_missing` | defer to POST-CONVERGE-12 |
| `dist/bin/engine` | `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | `portable_projection_proof_missing` | defer to POST-CONVERGE-12 |
| `dist/bin/game` | `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | `portable_projection_proof_missing` | defer to POST-CONVERGE-12 |
| `dist/bin/launcher` | `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | `portable_projection_proof_missing` | defer to POST-CONVERGE-12 |
| `dist/bin/server` | `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | `portable_projection_proof_missing` | defer to POST-CONVERGE-12 |
| `dist/bin/setup` | `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | `portable_projection_proof_missing` | defer to POST-CONVERGE-12 |
| `dist/bin/tool_attach_console_stub` | `INV-ALL-PRODUCTS-EMIT-DESCRIPTOR` | `portable_projection_proof_missing` | defer to POST-CONVERGE-12 |
| `dist/bin/engine` | `INV-NO-ADHOC-MAIN` | `portable_projection_proof_missing` | defer to POST-CONVERGE-12 |
| `dist/bin/game` | `INV-NO-ADHOC-MAIN` | `portable_projection_proof_missing` | defer to POST-CONVERGE-12 |
| `dist/bin/launcher` | `INV-NO-ADHOC-MAIN` | `portable_projection_proof_missing` | defer to POST-CONVERGE-12 |
| `dist/bin/setup` | `INV-NO-ADHOC-MAIN` | `portable_projection_proof_missing` | defer to POST-CONVERGE-12 |
| `dist/bin/tool_attach_console_stub` | `INV-NO-ADHOC-MAIN` | `portable_projection_proof_missing` | defer to POST-CONVERGE-12 |

## Safe Fix

One non-target hygiene failure was safe to fix: `docs/repo/audits/POST_CONVERGE_10K_CONTRACT_REGISTRY_ACCEPTANCE.md` was missing a status header. It is a derived audit report, so POST-CONVERGE-10L added the same minimal DERIVED status metadata used by adjacent audit evidence.

## Decision

No product proof was generated. No portable projection proof was generated. No package or release artifacts were generated. The remaining distribution/product family should be handled by POST-CONVERGE-11 for native boot proof and POST-CONVERGE-12 or a targeted dist wrapper task for tracked projection wrapper surfaces.
