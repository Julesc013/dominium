# AIDE Token Savings Summary

## Method

- approximation: chars / 4, rounded up
- exact_provider_billing: false
- exact_tokenizer: false
- raw_prompt_storage: false
- raw_response_storage: false

## Latest Compact Surfaces

- `.aide/context/latest-task-packet.md`: 4347 chars / 1087 approx tokens / within_budget
- `.aide/context/latest-context-packet.md`: 1866 chars / 467 approx tokens / within_budget
- `.aide/context/latest-review-packet.md`: 5125 chars / 1282 approx tokens / within_budget
- `.aide/verification/latest-verification-report.md`: 4911 chars / 1228 approx tokens / within_budget

## Named Baselines

- `root_history_baseline`: 440459 chars / 110115 approx tokens
- `review_baseline`: 26937 chars / 6735 approx tokens
- `repo_context_baseline`: 70053 chars / 17514 approx tokens

## Compact-To-Baseline Comparisons

- `.aide/context/latest-task-packet.md` vs `root_history_baseline`: 99.0% estimated reduction (1087 vs 110115 approx tokens)
- `.aide/context/latest-review-packet.md` vs `review_baseline`: 81.0% estimated reduction (1282 vs 6735 approx tokens)
- `.aide/context/latest-context-packet.md` vs `repo_context_baseline`: 97.3% estimated reduction (467 vs 17514 approx tokens)

## Largest Ledger Surfaces

- `AGENTS.md` (generated_adapter): 3658 approx tokens
- `.aide/cache/latest-cache-keys.json` (cache_report): 2008 approx tokens
- `.aide/prompts/codex-token-mode.md` (baseline_surface): 1593 approx tokens
- `.aide/context/latest-review-packet.md` (review_packet): 1282 approx tokens
- `.aide/verification/latest-verification-report.md` (verification_report): 1228 approx tokens
- `.aide/context/latest-task-packet.md` (task_packet): 1087 approx tokens
- `.aide/prompts/compact-task.md` (baseline_surface): 1000 approx tokens
- `.aide/prompts/evidence-review.md` (baseline_surface): 856 approx tokens
- `.aide/evals/runs/latest-golden-tasks.json` (eval_report): 813 approx tokens
- `.aide/cache/latest-cache-keys.md` (cache_report): 716 approx tokens

## Budget Warnings

- near budget: cache_report `.aide/cache/latest-cache-keys.json` 2008/2400

## Regression Warnings

- none

## Uncertainty

These are estimated metadata records only. They do not measure provider billing, exact tokenizer behavior, hidden reasoning tokens, cached-token discounts, or quality outcomes. Q15 golden tasks provide deterministic local quality gates, but they do not prove arbitrary coding-task quality.
