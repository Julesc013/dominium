Status: DERIVED
Last Reviewed: 2026-05-17
Supersedes: none
Superseded By: none

# MOVE-FAMILY-00C-PLAN Blockers

## Blocking Issues

MOVE-FAMILY-00C is not ready for an apply gate.

| Group | Blocker |
| --- | --- |
| `validation/**` | Runtime AppShell and compatibility shims import `validation`; a direct move into `tools/validators` could create or preserve a runtime-to-tools dependency without explicit shim policy. |
| `meta/identity/**` | Release, security, lib validators, tools, validation, and TestX import identity helpers. Identity semantics are release/security sensitive. |
| `meta/stability/**` | Validation, governance, AuditX, RepoX, release, security, review, and TestX import the stability API. |
| `governance/**` | Release/update, setup, dist, governance tools, release tools, and TestX import `governance` directly. |
| semantic/runtime `meta/**` | Compile, compute, explain, instrumentation, numeric, profile, provenance, reference, and observability modules are active domain/runtime support. |
| `performance/**` | Product/client, game material, and session runtime code import these helpers. |

## Non-Blocking Warnings

- Ignored `__pycache__/` directories exist under target roots and remain untracked.
- Path-reference counts are high because AIDE/generated/audit/planning evidence preserves historical paths.
- MOVE-FAMILY-00B retired `ide/`; this task does not reopen IDE cleanup.

## Authorization

- Move apply authorized: false.
- Shim creation authorized: false.
- Import/reference rewrites authorized: false.
- Exception updates authorized: false.

## Recommended Remediation

```text
MOVE-FAMILY-00C-A-PLAN - Validation, Identity, and Stability Shim Contract Plan
```
