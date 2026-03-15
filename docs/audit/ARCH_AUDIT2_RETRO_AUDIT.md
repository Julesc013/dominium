Status: DERIVED
Last Reviewed: 2026-03-14
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: Final release/distribution audit baseline governed by ARCH-AUDIT-2

# ARCH Audit 2 Retro Audit

## Existing Coverage

- `tools/audit/tool_run_arch_audit.py` and `tools/audit/arch_audit_common.py` already enforce truth purity, renderer/truth separation, duplicate semantic engines, determinism hazards, stability markers, contract pinning, and pack compatibility.
- RepoX already has dedicated invariants for component graph, install profiles, update model, trust model, target matrix, distribution assembly, distribution verification, and release manifest discipline.
- AuditX already covers many release and distribution smells, but the cross-layer coupling between these newer surfaces was not aggregated in one architecture report.

## Missing Cross-Layer Checks Before ARCH-AUDIT-2

- No single ARCH-AUDIT report check ensured dist assembly derived bundle composition from `component graph + install profile` rather than residual hardcoded bundle sets.
- No ARCH-AUDIT check explicitly confirmed update flows were release-index-driven and component-graph-resolved.
- No ARCH-AUDIT check explicitly searched for trust-verification bypass shortcuts in distribution and update flows.
- No ARCH-AUDIT check explicitly tied release-index downloadability to target-tier policy.
- No ARCH-AUDIT check explicitly scanned governed dist/update/release archive tooling for timestamp-bearing archive generation paths.

## Integration Targets

- Component graph and install profiles:
  - `src/release/component_graph_resolver.py`
  - `tools/release/component_graph_common.py`
  - `tools/release/install_profile_common.py`
- Update model:
  - `src/release/update_resolver.py`
  - `tools/release/update_model_common.py`
  - `tools/setup/setup_cli.py`
- Trust model:
  - `src/security/trust/trust_verifier.py`
  - `src/appshell/pack_verifier_adapter.py`
  - `tools/release/tool_verify_release_manifest.py`
  - `tools/dist/dist_verify_common.py`
- Target matrix:
  - `data/registries/target_matrix_registry.json`
  - `tools/release/arch_matrix_common.py`
  - `src/compat/capability_negotiation.py`
- Dist assembly and verification:
  - `tools/dist/dist_tree_common.py`
  - `tools/dist/tool_assemble_dist_tree.py`
  - `tools/dist/dist_verify_common.py`

## Audit-2 Scope

- Add five new ARCH-AUDIT families:
  - dist bundle composition purity
  - update model purity
  - trust bypass scan
  - target matrix compliance
  - archive determinism scan
- Keep the ARCH-AUDIT entrypoint single and deterministic.
- Emit dedicated ARCH-AUDIT-2 markdown and JSON outputs without creating a competing audit runtime.
