# Language Strategy (LANG0)

Status: binding.
Scope: language evolution, ABI stability, and multi-SKU coexistence.

## Core rules
- Engine C ABI spine is permanent.
- Public headers remain C89/C++98-parseable.
- Modern features are isolated to translation units.
- Launcher/client/tools may upgrade earlier than engine core.
- Multiple SKUs coexist without behavior drift.

## Enforcement
- Public headers must compile under legacy toolchains.
- Forbidden include detection in public headers.
- Capability list printed by every binary.

## See also
- `docs/architecture/TRANSITION_PLAYBOOK.md`
- `docs/architecture/SKU_MATRIX.md`
