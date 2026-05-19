Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Handshake Compatibility Matrix

| case_id | expected_result | expected_reason_code | actual_result | actual_reason_code | match |
|---|---|---|---|---|---|
| private.refuse_schema_version | refused | refusal.net.handshake_schema_version_mismatch | refused | refusal.net.handshake_schema_version_mismatch | yes |
| ranked.accept_signed | complete |  | complete |  | yes |
| ranked.refuse_observer_law | refused | refusal.net.handshake_policy_not_allowed | refused | refusal.net.handshake_policy_not_allowed | yes |
| ranked.refuse_unsigned | refused | refusal.net.handshake_securex_denied | refused | refusal.net.handshake_securex_denied | yes |

matrix_hash: `1926e51d42b7bca86246ca523439c0674245e19f9f141662021d54394f366fb6`
