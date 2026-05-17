# MOVE-BULK-01-APPLY Rollback

## Rollback Scope

Rollback only needs to reverse the 26 applied `git mv` operations. No reference rewrites, import rewrites, shims, exception updates, or generated metadata updates were applied.

## Reverse Moves

Move each target back to its source path:

```text
archive/audits/data/ultra_repo_audit_doc_code_mismatches.json -> data/audit/ultra_repo_audit_doc_code_mismatches.json
docs/planning/generated-data/checkpoints/checkpoint_c_phib1_y0.json -> data/planning/checkpoints/checkpoint_c_phib1_y0.json
docs/planning/generated-data/checkpoints/checkpoint_c_phib3_yb_safe_review.json -> data/planning/checkpoints/checkpoint_c_phib3_yb_safe_review.json
docs/planning/generated-data/checkpoints/checkpoint_c_sigma0_phia1.json -> data/planning/checkpoints/checkpoint_c_sigma0_phia1.json
docs/planning/generated-data/checkpoints/checkpoint_c_sigmaa1_phia2.json -> data/planning/checkpoints/checkpoint_c_sigmaa1_phia2.json
docs/planning/generated-data/cross_domain_bridge_template.json -> data/planning/cross_domain_bridge_template.json
docs/planning/generated-data/domain_constitution_execution_plan.json -> data/planning/domain_constitution_execution_plan.json
docs/planning/generated-data/next_execution_order_post_phib1.json -> data/planning/next_execution_order_post_phib1.json
docs/planning/generated-data/next_execution_order_post_phib3_yb.json -> data/planning/next_execution_order_post_phib3_yb.json
docs/planning/generated-data/next_execution_order_post_phib4.json -> data/planning/next_execution_order_post_phib4.json
docs/planning/generated-data/next_execution_order_post_ya.json -> data/planning/next_execution_order_post_ya.json
docs/planning/generated-data/next_execution_order_post_yc.json -> data/planning/next_execution_order_post_yc.json
docs/planning/generated-data/next_execution_order_post_yd.json -> data/planning/next_execution_order_post_yd.json
docs/planning/generated-data/next_execution_order_post_zb.json -> data/planning/next_execution_order_post_zb.json
docs/planning/generated-data/next_execution_order_post_zb3.json -> data/planning/next_execution_order_post_zb3.json
docs/planning/generated-data/player_desire_acceptance_matrix.json -> data/planning/player_desire_acceptance_matrix.json
docs/planning/generated-data/post_zeta_frontier_reconciliation_and_handoff.json -> data/planning/post_zeta_frontier_reconciliation_and_handoff.json
docs/planning/generated-data/semantic_ownership_registry.json -> data/planning/semantic_ownership_registry.json
docs/planning/generated-data/universal_domain_constitution_template.json -> data/planning/universal_domain_constitution_template.json
docs/planning/generated-data/universal_reality_framework_reconciliation.json -> data/planning/universal_reality_framework_reconciliation.json
docs/planning/generated-data/verification_and_equivalence_doctrine_reconciliation.json -> data/planning/verification_and_equivalence_doctrine_reconciliation.json
docs/repo/data/agent_mirror_registry.json -> data/agents/agent_mirror_registry.json
docs/repo/data/agent_safety_policy.json -> data/agents/agent_safety_policy.json
docs/repo/data/mcp_surface_registry.json -> data/agents/mcp_surface_registry.json
docs/repo/data/next_execution_order_post_repo_structure_review.json -> data/repo/next_execution_order_post_repo_structure_review.json
docs/repo/data/xstack_task_catalog.json -> data/agents/xstack_task_catalog.json
```

## Validation After Rollback

After rollback, rerun Tier 0 validation, exact old/new path scans, and git diff checks. No exception restoration is required because no exception changed.
