# AIDE Token Savings Summary

## Method

- approximation: chars / 4, rounded up
- exact_provider_billing: false
- exact_tokenizer: false
- raw_prompt_storage: false
- raw_response_storage: false

## Latest Compact Surfaces

- `.aide/context/latest-task-packet.md`: 4902 chars / 1226 approx tokens / within_budget
- `.aide/context/latest-context-packet.md`: 1849 chars / 463 approx tokens / within_budget
- `.aide/context/latest-review-packet.md`: 6008 chars / 1502 approx tokens / within_budget
- `.aide/verification/latest-verification-report.md`: 4911 chars / 1228 approx tokens / within_budget

## Named Baselines

- `root_history_baseline`: 442547 chars / 110637 approx tokens
- `review_baseline`: 27829 chars / 6958 approx tokens
- `repo_context_baseline`: 72141 chars / 18036 approx tokens

## Compact-To-Baseline Comparisons

- `.aide/context/latest-task-packet.md` vs `root_history_baseline`: 98.9% estimated reduction (1226 vs 110637 approx tokens)
- `.aide/context/latest-review-packet.md` vs `review_baseline`: 78.4% estimated reduction (1502 vs 6958 approx tokens)
- `.aide/context/latest-context-packet.md` vs `repo_context_baseline`: 97.4% estimated reduction (463 vs 18036 approx tokens)

## Largest Ledger Surfaces

- `.aide/evals/runs/latest-golden-tasks.json` (eval_report): 15648 approx tokens
- `.aide/evals/runs/latest-golden-tasks.md` (eval_report): 10715 approx tokens
- `AGENTS.md` (generated_adapter): 3742 approx tokens
- `.aide/cache/latest-cache-keys.json` (cache_report): 2008 approx tokens
- `.aide/prompts/codex-token-mode.md` (baseline_surface): 1593 approx tokens
- `.aide/context/latest-review-packet.md` (review_packet): 1502 approx tokens
- `.aide/verification/latest-verification-report.md` (verification_report): 1228 approx tokens
- `.aide/context/latest-task-packet.md` (task_packet): 1226 approx tokens
- `.aide/prompts/compact-task.md` (baseline_surface): 1000 approx tokens
- `.aide/prompts/evidence-review.md` (baseline_surface): 856 approx tokens

## Budget Warnings

- over budget: eval_report `.aide/evals/runs/latest-golden-tasks.json` 15648/4800
- over budget: eval_report `.aide/evals/runs/latest-golden-tasks.md` 10715/4800

## Budget Watchlist

- near budget: cache_report `.aide/cache/latest-cache-keys.json` 2008/2400

## Regression Warnings

- none

## Uncertainty

These are estimated metadata records only. They do not measure provider billing, exact tokenizer behavior, hidden reasoning tokens, cached-token discounts, or quality outcomes. Q15 golden tasks provide deterministic local quality gates, but they do not prove arbitrary coding-task quality.
