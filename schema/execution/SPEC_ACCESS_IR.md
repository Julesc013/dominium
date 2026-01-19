# SPEC_ACCESS_IR (EXEC0)

Status: binding.
Scope: canonical Access IR for declared reads, writes, and reductions.
Non-goals: runtime data access enforcement.

## Purpose
Access IR declares all data access for a TaskNode. Undeclared access is
forbidden. Access declarations are used for determinism, scheduling, and audit.

## Core Types

### AccessSet
Fields:
- access_id: stable, deterministic identifier.
- reads: ordered list of AccessRef entries.
- writes: ordered list of AccessRef entries.
- reduces: ordered list of ReduceRef entries.
- commutative: true | false

Rules:
- Every TaskNode MUST reference exactly one AccessSet.
- Reads and writes MUST be fully declared; undeclared access is forbidden.
- Writes imply exclusivity unless proven commutative and non-overlapping.
- Reductions MUST declare a deterministic reduction_op.
- Access lists MUST be emitted in deterministic order.

### AccessRef
Fields:
- component_id: stable component identifier.
- field_id: stable field identifier.
- range: RangeRef

Rules:
- component_id and field_id MUST resolve to schema-defined entities.
- range MUST be explicit and deterministic.

### ReduceRef
Fields:
- component_id: stable component identifier.
- field_id: stable field identifier.
- range: RangeRef
- reduction_op: stable identifier for a deterministic reduction operator.

Rules:
- reduction_op MUST be deterministic and defined in a binding spec.
- Floating-point reductions in AUTHORITATIVE tasks are forbidden.

### RangeRef
RangeRef is a declarative, bounded reference that identifies the target set of
entities or component instances without hidden iteration.

Allowed forms (examples):
- ENTITY_SET:<set_id>
- COMPONENT_SET:<set_id>
- INTEREST_SET:<set_id>
- INDEX_RANGE:<start_id>..<end_id> (inclusive, bounded)
- SINGLE:<entity_id>

Rules:
- RangeRef MUST be deterministic, bounded, and auditable.
- RangeRef MUST NOT imply implicit global scans.

## Commutativity
If commutative is true, the scheduler may reorder tasks only if:
- all writes/reductions are proven commutative, and
- all ranges are disjoint or resolved by deterministic reduction operators.

If commutative is false, the scheduler MUST enforce exclusive or ordered access.

## Forbidden Patterns
- Hidden access through opaque pointers or callbacks.
- Inferring access from names, directories, or dynamic reflection.
- Mutating state without a declared write.
