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
- source_fingerprint: `488ccf49df29f122d277ae863ca868db4e83f972be49332371222a89b0fd52ca`
- observed_refusal_count: `0`
- observed_degrade_count: `0`

## Key Hashes

- client_ipc_hash: `1ebbcf0e24aeac247f930092dddc40dda9312f0ef160b9c4a035b422604822d2`
- client_negotiation_record_hash: `f66e5a107da3e992b51d346a02a07605edee9bc63ab4f67c08283249a7c95389`
- server_ipc_hash: `0e2901767954abdad507085405d6705e26102d8348d51d56689dc48c50e30839`
- server_negotiation_record_hash: `58057b9000af55acbcd5f79b211ca3ec42e073463efe9feec34236cca5a297c6`
- setup_ipc_hash: `edcbca436bea388c1334af684c416382e32c6171b72eb52053707c939dc72785`
- setup_negotiation_record_hash: `7d4884f40623a75402d1b4ab37149486b24d4ec97dfb6d003132ff3215cddb74`

## Notes

- server compatibility_mode_id=compat.full missing_negotiation_refusal=refusal.connection.no_negotiation
- client compatibility_mode_id=compat.degraded missing_negotiation_refusal=refusal.connection.no_negotiation
- setup compatibility_mode_id=compat.refuse missing_negotiation_refusal=refusal.connection.no_negotiation

## Source Paths

- none

## Remediation

- module=`tools/appshell/tool_run_ipc_unify.py` rule=`INV-IPC-REQUIRES-NEGOTIATION` refusal=`none` command=`python tools/appshell/tool_run_ipc_unify.py --repo-root .`
