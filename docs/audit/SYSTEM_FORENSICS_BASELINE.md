Status: BASELINE
Last Reviewed: 2026-03-06
Version: 1.0.0
Scope: SYS-7 System Forensics & Explainability Capstone

# System Forensics Baseline

## Summary
SYS-7 establishes deterministic, bounded, epistemically-redacted system forensics for composed systems across micro and macro tiers.

Delivered capabilities:
- deterministic explain request/artifact schemas and normalization contracts,
- bounded cause-chain selection with stable severity/recency/event-id tie-break ordering,
- policy-driven redaction levels (`diegetic`, `inspector`, `admin`) without truth leakage by default,
- explain generation process (`process.system_generate_explain`) with deterministic cache keys and hash-chain integration,
- automatic explain generation hooks for reliability failures, forced expands, certificate revocations, and capsule error-bound conditions,
- proof/replay determinism verification tooling for explain artifact fingerprints.

## Explain Levels
- `L1` boundary-level explain:
  - boundary inputs/outputs, invariant context, and high-level primary cause.
- `L2` component-level explain:
  - subsystem contributors and safety/spec interactions.
- `L3` event-chain explain:
  - bounded sequence of canonical events and references suitable for deep audit.

## Bounded Selection Algorithm
Cause-chain construction is deterministic and bounded:
- candidate inputs are canonical rows (reliability, safety, certification, ledger residual, macro error-bound and domain fault streams),
- entries are sorted by:
  - higher `severity`,
  - then newer `tick`,
  - then stable `entry_id` tie-break,
- final chain is truncated to configured maximum (`system_forensics_max_cause_entries` with safe defaults),
- artifact fingerprints are canonicalized and hash chained.

## Redaction Rules
- `diegetic`:
  - coarse cause entries only, minimal references, no privileged thresholds/spec internals.
- `inspector`:
  - includes threshold/spec references and richer cause context.
- `admin`:
  - full bounded references to canonical event IDs/specs/remediation hints.

Redaction is applied at generation time by requester policy and enforced before cache persistence.

## Macro Capsule Forensics
Forensics remains available while systems are collapsed:
- consumes `system_macro_output_record_rows` and `system_macro_runtime_state_rows` as supporting evidence,
- links forced-expand explain outputs to canonical `system_forced_expand_event_rows`,
- keeps explain artifacts derived/compactable while preserving references to canonical truth rows.

## Proof and Replay
Tooling:
- `tools/system/tool_verify_explain_determinism.py`
- wrappers:
  - `tools/system/tool_verify_explain_determinism`
  - `tools/system/tool_verify_explain_determinism.cmd`

Proof surfaces:
- `system_explain_hash_chain`
- `system_explain_cache_hash_chain`
- referenced canonical event hash chains from SYS-5/SYS-6/SYS-2 integrations.

## Validation Snapshot (SYS-7)
- TestX SYS-7 required subset: PASS
  - `test_explain_artifact_deterministic`
  - `test_cause_chain_bounded`
  - `test_redaction_policy_applied`
  - `test_forced_expand_auto_explain`
  - `test_certificate_revocation_explain`
- AuditX STRICT: PASS (`promoted_blockers=0`).
- RepoX STRICT: PASS on clean committed worktree (warnings only).
- strict build (`py -3 tools/xstack/run.py strict --repo-root . --cache on`): REFUSAL due pre-existing repository-wide strict-lane blockers outside SYS-7 scope (CompatX/pack/session/bootstrap/full-lane TestX/packaging), no SYS-7-specific contract regression identified.
- topology map refresh: PASS (`docs/audit/TOPOLOGY_MAP.json`, `docs/audit/TOPOLOGY_MAP.md` regenerated).

## Readiness for SYS-8
SYS-7 is ready for SYS-8 stress/proof envelope work:
- deterministic explain generation and caching are established,
- system event explain coverage is integrated across reliability/certification/capsule pathways,
- epistemic redaction rules are enforced in-process and test-covered,
- replay determinism hooks exist for explain artifact verification.
