Status: DERIVED
Last Reviewed: 2026-03-13
Stability: provisional
Future Series: RELEASE
Replacement Target: regenerated convergence step summary for ipc_attach_smoke

# Convergence Step - IPC-UNIFY attach smoke

- step_no: `9`
- step_id: `ipc_attach_smoke`
- result: `complete`
- rule_id: `INV-IPC-REQUIRES-NEGOTIATION`
- source_fingerprint: `ef454e4a9dc155502c860442990834568b9b8d9c830b8e3be125963f7c7cf81d`
- observed_refusal_count: `0`
- observed_degrade_count: `0`

## Key Hashes

- client_ipc_hash: `d6f16799fa1bd25c631d5d8f93a34c631371673210d26493dc05e68bf595d0c7`
- client_negotiation_record_hash: `9b5d431786f32df95274fec1b4ab97008f2886229a1e82cebf6b405a0c5c7712`
- server_ipc_hash: `b3436bceb73b721eb7a5942eaea590fd5397ade39d5c0f704649b982dade31f0`
- server_negotiation_record_hash: `d835395666963dcfe0b71e548660c9ede5bb16ac4722d614f32063a61d8f8732`
- setup_ipc_hash: `81b23b7ff2bfdfbfbcc4090adbdf6a650f08a7e6f7ae20fef2b2e228fe6bee68`
- setup_negotiation_record_hash: `e79e3579f1aa1c5575ed646cdff97a73838a9478eb940f0700d7990b19401c28`

## Notes

- server compatibility_mode_id=compat.full missing_negotiation_refusal=refusal.connection.no_negotiation
- client compatibility_mode_id=compat.degraded missing_negotiation_refusal=refusal.connection.no_negotiation
- setup compatibility_mode_id=compat.refuse missing_negotiation_refusal=refusal.connection.no_negotiation

## Source Paths

- none

## Remediation

- module=`tools/appshell/tool_run_ipc_unify.py` rule=`INV-IPC-REQUIRES-NEGOTIATION` refusal=`none` command=`python tools/appshell/tool_run_ipc_unify.py --repo-root .`
