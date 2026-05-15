# Latest Golden Tasks

- result: PASS
- task_count: 1
- pass_count: 1
- warn_count: 0
- fail_count: 0
- provider_or_model_calls: none
- network_calls: none
- raw_prompt_storage: false
- raw_response_storage: false
- token_quality_statement: Token reduction remains valid only if golden tasks pass.

## Tasks

### intent_compile_install_prompt_golden

- result: PASS
- checks_run: 6
- passed_checks: 6
- approx_tokens_if_applicable: n/a
- related_paths: .aide/policies/export-import.yaml, .aide/policies/intent.yaml, .aide/policies/prompt-normalization.yaml
- notes: Checks target install prompts become preflight/preservation WorkUnits.

## Limitations

- Deterministic local checks only.
- No model/provider/network calls.
- No external benchmark or arbitrary code semantic proof.
