Status: TEMPLATE
Version: 1.0.0
Last Reviewed: 2026-02-14
Compatibility: Use with pack contracts and canon v1.0.0.

# Skill Template: pack_contrib

## Purpose
Contribute or modify packs while preserving pack-driven integration and deterministic load behavior.

## Constraints
- Packs are data-only; no executable code.
- No hidden dependencies or absolute path assumptions.
- Keep pack IDs/versioning namespaced and explicit.
- Avoid over-designing optional abstractions outside immediate pack contract scope.

## Checklist
1. Confirm target pack identity (`pack_id`, version, format version).
2. Validate manifest required fields and dependency declarations.
   - `tools/xstack/pack_list`
   - `tools/xstack/bundle_validate bundles/bundle.base.lab/bundle.json`
3. Confirm provided capabilities are registry-consistent.
   - `tools/xstack/registry_compile`
   - `tools/xstack/lockfile_validate build/lockfile.json`
   - For lens/law contributions, verify required observation-gating fields are present.
4. Confirm optional/missing-pack behavior is deterministic refusal/degradation.
5. Update pack-related docs/contracts if behavior meaning changes.
6. Validate lock/hash impact and replay-safety implications.
7. Run required gate profile for impacted scope.

## Output Format
- Pack changes summary.
- Compatibility impact statement.
- Determinism and refusal behavior statement.
- Validation status and TODOs.

## Example Invocation
```text
Use skill.pack_contrib to add pack.lab.galaxy.navigation:
- manifest only
- no runtime code
- declare capabilities and dependencies
- document refusal on missing optional dependency
Verify with:
- tools/xstack/run fast
- tools/xstack/out/fast/latest/report.json
```

## TODO
- Add template for deterministic provider tie-break documentation.
- Add pack lock-hash validation checklist details.

## Cross-References
- `docs/canon/constitution_v1.md`
- `docs/architecture/pack_system.md`
- `docs/contracts/session_spec.md`
- `docs/architecture/PACK_FORMAT.md`
