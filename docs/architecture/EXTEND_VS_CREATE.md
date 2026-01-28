# Extend vs Create (CONS-0)

Status: binding.
Scope: rule for introducing new systems.

## Rule
A new system may only be introduced if extending an existing system would
violate that system's semantic truth or invariants.

## Mandatory checklist
1) Which existing system was considered?
2) Why is extension insufficient?
3) Which invariant would be violated by extension?
4) How is removal handled?

## Correct extensions (examples)
- Mode policies expressed via law/capability.
- Recipes expressed as processes with explicit inputs and outputs.

## Incorrect new systems (examples)
- XP/level systems
- Debug flag systems
- Tech trees

## References
- `docs/arch/EXTENSION_RULES.md`
- `docs/arch/ARCH0_CONSTITUTION.md`
