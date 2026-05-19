Status: DERIVED
Last Reviewed: 2026-03-14
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: OBSERVABILITY/DIAG
Replacement Target: release-pinned observability policies and repro-bundle minimum-set governance

# Observability Baseline

- result: `complete`
- guaranteed_category_count: `8`
- message_key_count: `57`
- deterministic_fingerprint: `25df6294a2d906482c77e6a1efa745abb14ffd58d5bcbb7c120c69136c35892d`

## Guaranteed Categories

- `compat`: minimum_fields=`event_id,message_key,product_id,severity` redaction_policy_id=`redaction.compat`
- `diag`: minimum_fields=`event_id,message_key,product_id,severity` redaction_policy_id=`redaction.diag`
- `lib`: minimum_fields=`event_id,message_key,product_id,severity` redaction_policy_id=`redaction.lib`
- `packs`: minimum_fields=`event_id,message_key,product_id,severity` redaction_policy_id=`redaction.packs`
- `refusal`: minimum_fields=`event_id,message_key,params.reason,params.refusal_code,params.remediation_hint,product_id,severity` redaction_policy_id=`redaction.refusal`
- `server`: minimum_fields=`event_id,message_key,params.source,product_id,severity` redaction_policy_id=`redaction.server`
- `supervisor`: minimum_fields=`event_id,message_key,product_id,severity` redaction_policy_id=`redaction.supervisor`
- `update`: minimum_fields=`event_id,message_key,product_id,severity` redaction_policy_id=`redaction.update`

## Minimum Fields

- `compat` -> `event_id,message_key,product_id,severity`
- `diag` -> `event_id,message_key,product_id,severity`
- `lib` -> `event_id,message_key,product_id,severity`
- `packs` -> `event_id,message_key,product_id,severity`
- `refusal` -> `event_id,message_key,params.reason,params.refusal_code,params.remediation_hint,product_id,severity`
- `server` -> `event_id,message_key,params.source,product_id,severity`
- `supervisor` -> `event_id,message_key,product_id,severity`
- `update` -> `event_id,message_key,product_id,severity`

## DIAG Bundle Mapping

- `events/canonical_events.json`
- `events/negotiation_records.json`
- `logs/log_events.jsonl`
- `packs/pack_verification_report.json`
- `plans/install_plan.json`
- `plans/update_plan.json`
- `proofs/proof_anchors.json`

## Readiness

- STORE-GC-0: `ready`
- DIST-7 final packaging: `ready`
