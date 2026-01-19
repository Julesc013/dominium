# Setup Extension Policy

## What is an extension
- New TLV fields or containers.
- New job kinds or job graph edges.
- New SPLAT providers or capability flags.
- New registration intents.

## What is not an extension
- UI text and layout.
- Documentation and examples.
- Test coverage additions.

## Rules
- New TLV fields must be optional and skip-unknown safe.
- Kernel ignores unknown fields deterministically.
- Every extension requires:
  - schema update
  - validation update
  - audit visibility
  - tests

## Versioning
- Major version bump for incompatible TLV changes.
- Minor version bump for additive changes.
- Refuse incompatible major versions deterministically.
