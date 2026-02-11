Status: DERIVED
Last Reviewed: 2026-02-11
Supersedes: none
Superseded By: none

# Threat Model

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
