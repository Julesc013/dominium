# Token Savings Report

Method: chars / 4, rounded up. This is not exact provider tokenization and does
not claim exact billing savings.

Compact surfaces:

- task packet: `.aide/context/latest-task-packet.md`
  - chars: 4,347
  - approx tokens: 1,087
- context packet: `.aide/context/latest-context-packet.md`
  - chars: 1,866
  - approx tokens: 467
- review packet: `.aide/context/latest-review-packet.md`
  - chars: 5,125
  - approx tokens: 1,282
- verification report: `.aide/verification/latest-verification-report.md`
  - chars: 4,911
  - approx tokens: 1,228

Naive doctrine-heavy baseline:

- baseline name: `root_history_baseline`
- chars: 440,459
- approx tokens: 110,115
- baseline file list:
  - `README.md`
  - `DOMINIUM.md`
  - `GOVERNANCE.md`
  - `CLAUDE.md`
  - `AGENTS.md`
  - `docs/README.md`
  - `docs/ARCHITECTURE.md`
  - `docs/XSTACK.md`
  - `docs/STATUS_NOW.md`
  - `docs/canon/constitution_v1.md`
  - `docs/canon/glossary_v1.md`
  - `docs/planning/AUTHORITY_ORDER.md`
  - `docs/planning/SNAPSHOT_INTAKE_PROTOCOL.md`
  - `docs/planning/MERGED_PROGRAM_STATE.md`
  - `docs/planning/EXTEND_NOT_REPLACE_LEDGER.md`
  - `docs/planning/GATES_AND_PROOFS.md`
  - `docs/planning/POST_PI_EXECUTION_PLAN.md`
  - `docs/planning/SEMANTIC_OWNERSHIP_REVIEW.md`
  - `docs/planning/PLAYER_DESIRE_ACCEPTANCE_MAP.md`
  - `specs/reality/SPEC_DOMINIUM_UNIVERSAL_REALITY_FRAMEWORK.md`
  - `specs/reality/SPEC_DOMAIN_CONTRACT_TEMPLATE.md`
  - `specs/reality/SPEC_CAPABILITY_SURFACES.md`
  - `specs/reality/SPEC_REPRESENTATION_LADDERS.md`
  - `specs/reality/SPEC_SEMANTIC_ASCENT_DESCENT.md`
  - `specs/reality/SPEC_FORMALIZATION_CHAIN.md`
  - `specs/reality/SPEC_CROSS_DOMAIN_BRIDGES.md`
  - `docs/xstack/AIDE_PORTABLE_TASK_CONTRACT.md`
  - `docs/xstack/AIDE_EVIDENCE_AND_REVIEW_CONTRACT.md`
  - `docs/xstack/AIDE_POLICY_AND_PERMISSION_SHAPE.md`
  - `docs/xstack/AIDE_CAPABILITY_PROFILE_SHAPE.md`
  - `docs/xstack/AIDE_ADAPTER_CONTRACT.md`

Reduction:

- task packet versus baseline: 1,087 / 110,115 approx tokens
- estimated reduction: 99.0%

Other comparisons from AIDE ledger:

- latest context packet versus `repo_context_baseline`: 97.3% reduction
- latest review packet versus `review_baseline`: 81.0% reduction

Uncertainty and caveat:

- Exact tokenizer behavior, provider billing, hidden reasoning tokens, cached
  token discounts, and quality outcomes are not measured.
- The quality claim is limited to preserving enough refs and constraints for
  bounded next-task review, not to proving arbitrary implementation quality.
