Status: DERIVED
Version: 1.0.0
Last Reviewed: 2026-02-15
Scope: Prompt 20 Phase 6 institutional failure catalog
Compatibility: Bound to `docs/canon/constitution_v1.md`, `docs/canon/glossary_v1.md`, and `AGENTS.md`.

# Failure Mode Catalog

## Catalog

| Failure Class | Representative Refusal Code(s) | Detection Mechanism | Remediation Path |
|---|---|---|---|
| Mechanical failures (missing tool / stale cache) | `REFUSE_INTERNAL`, `REFUSE_CACHE_KEY_MISMATCH` | XStack run step failure, TestX smoke, packaging verify | Rebuild cache, re-run strict profile, repair tool path, regenerate derived artifacts |
| Determinism violations | `REFUSE_DIST_NONDETERMINISTIC`, `REFUSE_LAB_COMPOSITE_HASH_MISMATCH` | TestX determinism suites, packaging validation, SRZ hash replay tests | Re-run with identical envelope, inspect canonical serialization order, fix nondeterministic ordering |
| Authority violations | `ENTITLEMENT_MISSING`, `PRIVILEGE_INSUFFICIENT`, `refusal.server_authority_violation` | Runtime refusal contract, server/session tests, RepoX policy checks | Correct AuthorityContext entitlements/privilege, align law profile allowances |
| Contract violations | `PROCESS_FORBIDDEN`, `refusal.contract_violation` | Process execution refusals, domain contract tests, RepoX invariants | Bind allowed process/lens/solver contracts; update registry declarations |
| Registry drift | `REFUSE_REGISTRY_HASH_MISMATCH`, `REFUSE_LOCKFILE_REGISTRY_MISMATCH` | lockfile validation, AuditX freshness analyzer, xstack strict | Recompile registries deterministically, refresh lockfile, verify hash map |
| Pack incompatibility | `PACK_INCOMPATIBLE`, `REFUSE_DEPENDENCY_MISSING`, `REFUSE_DEPENDENCY_CYCLE` | pack loader/contrib checks, lockfile build, launcher enforcement | Repair manifest compatibility/dependencies and regenerate lockfile |
| Schema mismatch | `REFUSE_SCHEMA_VERSION_MISMATCH`, `REFUSE_INSTANCE_INVALID` | `schema_validate`, CompatX checks, FAST/STRICT schema tests | Apply CompatX migration or explicit refusal path; update schema-bound docs |
| Domain binding mismatch | `refusal.domain_missing`, `refusal.contract_missing`, `refusal.solver_unbound` | `tools/domain/tool_domain_validate.py`, RepoX domain invariants, TestX | Correct domain/contract IDs and solver bindings in registries |
| Session pipeline misuse | `refusal.stage_invalid_transition`, `refusal.server_stage_mismatch`, `INV-NO-STAGE-SKIP` | session pipeline runtime checks, server tests, RepoX invariant checks | Resume through canonical stages; do not stage-jump; verify session registries |
| Streaming hint misuse | `REFUSE_POLICY_INVALID` (policy-level), deterministic cap/degrade refusal paths | PerformX reports, ROI/fidelity strict tests, AuditX drift | Constrain hints to policy registries; keep hints non-semantic and deterministic |

## Notes

1. Refusal codes are stable contract surface and must not be silently renamed.
2. Runtime refusals and governance findings are complementary:
   - Runtime enforces immediate safety.
   - RepoX/TestX/AuditX enforce pre-merge discipline.
3. Deterministic formatting and ordering are required for all refusal payloads.

## Cross-References

- `docs/contracts/refusal_contract.md`
- `docs/architecture/session_lifecycle.md`
- `docs/architecture/registry_compile.md`
- `docs/architecture/hash_anchors.md`
- `docs/testing/xstack_profiles.md`
