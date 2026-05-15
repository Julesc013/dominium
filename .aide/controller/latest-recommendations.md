# AIDE Recommendations

## MODE

- advisory_only: true
- applies_automatically: false
- automatic_prompt_mutation: false
- automatic_policy_mutation: false
- automatic_route_mutation: false

## RECOMMENDATIONS

- ID: REC-PROCEED-Q17-WITH-GATES
  - failure_class: unknown
  - evidence_source: `.aide/controller/latest-outcome-report.md`
  - expected_benefit: Begin advisory Router Profile design after token, verifier, review, and golden-task foundations are locally healthy.
  - risk_level: low
  - next_action: Proceed to Q17 Router Profile v0 as an advisory profile only; do not call providers or implement Gateway.
  - rollback_condition: If any controller signal regresses, pause Q17 and repair the failing local gate first.
  - applies_automatically: false

## SAFETY

- provider_or_model_calls: none
- network_calls: none
- raw_prompt_storage: false
- raw_response_storage: false
