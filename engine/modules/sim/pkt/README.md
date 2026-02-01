# SIM/PKT (Packets)

TLV-versioned packet families used by deterministic simulation and lockstep.

## Responsibilities
- Define packet families and TLV framing rules.
- Require stable IDs and canonical ordering for serialization and hashing.
- Provide forward/backward compatibility via versioned TLVs.

## Non-responsibilities / prohibited
- No platform/network transport code (wire transport lives elsewhere).
- No gameplay semantics; packets are generic carriers.

## Spec
See `docs/specs/SPEC_PACKETS.md` and `docs/specs/SPEC_DETERMINISM.md`.

