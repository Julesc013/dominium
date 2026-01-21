# Future Proofing (FUTURE0)

Status: binding.
Scope: long-term evolution rules and architectural guardrails.

FUTURE0 defines how the project survives decades of change without refactor
or drift. It preserves the canonical model and enforces safe extension paths.

## Allowed without architectural change
The following evolutions are allowed if they preserve invariants and follow
the change protocol:
- New gameplay systems built on Work IR, law/capability, domains, and refinement.
- New kernel backends (SIMD/GPU/cluster) that preserve deterministic contracts.
- New ECS storage backends that preserve schema semantics.
- New domain authoring formats that compile to canonical runtime forms.
- New economic models encoded as data + contracts.
- New life/civ content and policies expressed through schemas and contracts.

## Requires architectural review (CANON)
The following changes require explicit architectural review and canon update:
- Changes to invariants or determinism guarantees.
- Changes to ACT semantics or scheduling model.
- Changes to existence states, archival, or refinement guarantees.
- Any bypass of law, audit, or refusal semantics.
- Changes to engine/game separation or dependency rules.

## Forbidden (non-negotiable)
- Global simulation loops or per-tick world scans.
- Implicit existence or implicit resource creation.
- Hidden admin bypasses or unaudited authority.
- Teleportation without an explicit travel edge.
- Nondeterministic authoritative logic.

## Integration points
- Canon and invariants: `docs/arch/INVARIANTS.md`
- Change protocol: `docs/arch/CHANGE_PROTOCOL.md`
- Extension rules: `docs/arch/EXTENSION_RULES.md`
- Scale guarantees: `docs/arch/SCALE_AND_COMPLEXITY.md`
