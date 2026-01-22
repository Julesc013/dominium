# IDE Projections (/ide)

Status: binding.
Scope: IDE project projections and projection manifests.

This directory is the only permitted location for IDE project outputs.
Everything under `/ide` is disposable and regenerated, except:
- `/ide/README.md`
- `/ide/manifests/**` (schema + examples)

Generated layout (created by scripts, not edited by hand):
- `/ide/win/` (vc6/vc71/vs2015/vs2026 projections)
- `/ide/mac/` (CodeWarrior + Xcode era projections)
- `/ide/linux/` (gcc/clang projections)
- `/ide/manifests/` (projection manifests)

Rules:
- Do not add or edit IDE project files outside `/ide`.
- Do not edit generated projects inside `/ide`; regenerate instead.
- Use `scripts/ide_gen.bat` or `scripts/ide_gen.sh` to regenerate.
- Projection manifests are required for every projection output.
