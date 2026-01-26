# Mod Ecosystem Rules (MOD0)

Status: binding.
Scope: mod participation, save safety, compatibility modes, and deprecation.

## Mod participation rules
- Mods are packs; they are data and capability declarations.
- No executable logic inside packs.
- All identifiers are namespaced and stable.
- Mods MUST declare provided and required capabilities.

## Save safety guarantees
- Saves include mod chunks keyed by mod_id.
- Unknown mod chunks are preserved and round-trippable.
- Missing required mod chunks at load => frozen/inspect-only mode.
- No mod may mutate authoritative state without capability and law.

## Compatibility sandbox modes
```mod-compat-modes
# mode, allows_mutation, description
active, yes, full mod participation
degraded, limited, missing optional capabilities
frozen, no, missing required capabilities or data
inspect_only, no, read-only inspection of saves/replays
```

## Deprecation policy
- Deprecations MUST be explicit and versioned.
- A deprecation MUST include a migration path or refusal plan.
- Deprecated identifiers are never reused.

## See also
- `docs/arch/CONTENT_AND_STORAGE_MODEL.md`
- `docs/arch/SAVE_PIPELINE.md`
- `schema/mod_extension_policy.md`
