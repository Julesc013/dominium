Status: TEMPLATE
Version: 1.0.0
Last Reviewed: 2026-02-15
Compatibility: Use with observer/renderer/truth separation, `schemas/ui_window.schema.json` v1.0.0, and profile-driven governance rules.

# Skill Template: client_ui

## Purpose
Implement or review client UI changes while preserving law/authority gating and non-authoritative presentation boundaries.

## Constraints
- UI must not mutate authoritative state directly.
- Do not bypass authority/law checks in UI command dispatch.
- Do not encode runtime mode branches in UI logic.
- Keep changes minimal and contract-aligned; avoid speculative UI framework overhauls.
- Window descriptors are pack data only; no executable pack code.
- UI bindings must target `perceived_model` selectors only.
- Unknown widget types and invalid selectors must refuse deterministically.

## Checklist
1. Identify UI surfaces touched (panels, overlays, commands, lenses).
2. Validate lens and entitlement requirements are explicit.
   - `required_entitlements[]`
   - optional `required_lenses[]`
   - law debug allowance gate for nondiegetic overlays
3. Verify command path goes through canonical command graph and refusal handling.
4. Verify observer/renderer/truth boundaries remain intact.
   - renderer/presentation code must not include `domino/truth_model_v1.h`
5. Verify missing entitlement/missing pack behavior is explicit refusal.
6. Update docs/contracts for changed surface semantics.
7. Run required tests/gates for UI and determinism safety.
   - `tools/xstack/run fast`
   - `tools/xstack/run strict`
   - inspect `tools/xstack/out/fast/latest/report.json`
   - inspect `tools/xstack/out/strict/latest/report.json`

8. Validate descriptor and registry contracts directly when relevant.
   - `tools/xstack/schema_validate ui_window <descriptor.json>`
   - `tools/xstack/registry_compile`
   - inspect `build/registries/ui.registry.json`

## Output Format
- UI contract impact summary.
- Entitlement/lens/authority changes.
- Refusal and fallback behavior.
- Validation summary.
- Descriptor/schema conformance summary.

## Example Invocation
```text
Use skill.client_ui to add a new navigation panel:
- lens-gated
- authority-aware command wiring
- no direct truth mutation
- update lens/session contracts
- validate descriptor schema + ui.registry determinism
```

## TODO
- Add reusable checklist for CLI/TUI/GUI parity verification.
- Add standard refusal UX message mapping by refusal code class.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/contracts/lens_contract.md`
- `docs/contracts/authority_context.md`
- `docs/architecture/truth_model.md`
- `docs/architecture/truth_perceived_render.md`
- `docs/architecture/ui_registry.md`
- `docs/architecture/RENDERER_RESPONSIBILITY.md`
