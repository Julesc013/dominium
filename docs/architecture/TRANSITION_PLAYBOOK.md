# Transition Playbook (LANG1)

Status: binding.
Scope: language transition and split-component strategy.

## Steps
1) Preserve C ABI spine and public headers (C89/C++98).
2) Isolate new language features to private translation units.
3) Provide a C ABI adapter when introducing new language modules.
4) Add baseline capability for each new requirement.
5) Maintain multi-SKU builds in parallel until deprecation is approved.

## Compatibility guarantees
- Old binaries may load new saves in frozen/inspect mode.
- Refusal required when capabilities are missing.
- No silent migration or behavior drift.

## See also
- `docs/architecture/LANGUAGE_STRATEGY.md`
- `docs/architecture/CAPABILITY_BASELINES.md`
