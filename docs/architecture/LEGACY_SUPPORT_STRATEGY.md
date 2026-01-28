# Legacy Support Strategy (REPOX)

Status: binding.
Scope: VC6/VC7.1/CodeWarrior and other legacy toolchains.

## Principles
- Legacy support is mechanical, not aspirational.
- Once a legacy tier is validated, it is frozen.
- Legacy projections are generated, not hand-edited.

## Toolchain maintenance
- VC6 (Win9x/NT4/2000) and VC7.1 (XP/Vista) are maintained in frozen environments.
- CodeWarrior Classic is maintained in a frozen Classic Mac OS environment.
- Xcode era builds are pinned to known SDKs and Xcode versions.

## Environment handling
- Use frozen VMs or sealed OS installs for legacy tiers.
- Document exact OS + toolchain + SDK versions used.
- Artifacts must include provenance metadata (toolchain tier, SDK pin, OS floor).

## Projection workflow
- Generate file lists and flags deterministically.
- Use templates + token substitution for legacy project files.
- Output goes under `/ide/**` only.

## Cross-references
- `docs/architecture/IDE_AND_TOOLCHAIN_POLICY.md`
- `docs/architecture/PROJECTION_LIFECYCLE.md`
