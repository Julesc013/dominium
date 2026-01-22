# IDE Contribution Rules (REPOX)

Status: binding.
Scope: IDE projections and contribution hygiene.

## Core rules
- IDE project files MUST NOT be committed outside `/ide/**` or documented packaging inputs.
- Generated IDE outputs are disposable; regenerate instead of editing.
- Core logic is not edited through legacy IDE projects.
- UI shell work stays within UI shell directories and stable C ABI boundaries.

## Projection workflow
- Use `scripts/ide_gen.bat` or `scripts/ide_gen.sh`.
- Commit templates and deterministic file lists only.
- Never commit generated outputs under `/ide/**` unless explicitly required and documented.

## Forbidden patterns
- `.sln`, `.vcxproj`, `.vcproj`, `.dsp`, `.dsw`, `.xcodeproj`, `.pbxproj`, `.mcp` outside `/ide/**`.
- IDE state directories (e.g., `.vs`, `.xcuserdata`) inside source trees.
- Silent IDE toolchain upgrades.

## Exceptions
Grandfathered packaging inputs must be listed in:
- `docs/arch/REPO_OWNERSHIP_AND_PROJECTIONS.md`

## Cross-references
- `docs/arch/REPO_OWNERSHIP_AND_PROJECTIONS.md`
- `docs/arch/GENERATED_CODE_POLICY.md`
