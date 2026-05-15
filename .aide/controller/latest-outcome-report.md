# AIDE Outcome Report

## RESULT

- result: PASS
- mode: advisory_only
- applies_automatically: false

## SIGNALS

- adapter_guidance: PASS / unknown / info
- context_artifacts: PASS / unknown / info
- golden_tasks: PASS / unknown / info
- review_packet: PASS / unknown / info
- token_ledger: PASS / unknown / info
- verifier: PASS / unknown / info

## FAILURE_CLASSES

- none

## NEXT_ACTION

- top_recommendation: REC-PROCEED-Q17-WITH-GATES: Proceed to Q17 Router Profile v0 as an advisory profile only; do not call providers or implement Gateway.
- recommendations: `.aide/controller/latest-recommendations.md`
- outcome_ledger: `.aide/controller/outcome-ledger.jsonl`

## SAFETY

- provider_or_model_calls: none
- network_calls: none
- automatic_mutation: false
- raw_prompt_storage: false
- raw_response_storage: false
- controller_policy: `.aide/policies/controller.yaml`
