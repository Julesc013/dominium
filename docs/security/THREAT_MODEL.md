Status: DERIVED
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: patched document aligned to current canon ownership and release scope

# Threat Model

## Patch Notes

- Current status: partially aligned to the Constitutional Architecture and release-freeze documentation set.
- Required updates: documentation surface exists, but current canon ownership is not explicit
- Cross-check with: `docs/audit/CANON_MAP.md` and `docs/audit/DOC_DRIFT_MATRIX.md`.


## Prompt-Level Threats

- Untrusted prompt text may attempt to bypass gate policy, disable invariants, or force direct tool calls.
- Mitigation: ControlX prompt sanitization plus RepoX direct-gate-call invariants.

## Pack-Level Threats

- Tampered or unsigned packs may attempt schema drift, privilege escalation, or hidden dependencies.
- Mitigation: pack signatures, lockfile hash pinning, trust-policy checks, and deterministic refusal codes.

## Multiplayer Trust Threats

- Client-side attempts to mutate authoritative state or read restricted server fields.
- Mitigation: server-side authority validation and client/server boundary checks.

## Toolchain Integrity Threats

- Tool binary mismatch or non-reproducible outputs can poison derived artifacts.
- Mitigation: integrity manifests, reproducible-build verification, and derived artifact contract enforcement.

## Insider Error Threats

- Accidental hardcoded mode flags, entitlement bypasses, or unsafe file I/O.
- Mitigation: RepoX/TestX/AuditX security rules and regression tests.
