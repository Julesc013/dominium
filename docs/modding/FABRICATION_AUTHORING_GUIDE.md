# Fabrication Authoring Guide (FAB0)

Status: binding.
Scope: data-only authoring for materials, processes, assemblies, standards, and instruments.

## Quick rules
- Use namespaced identifiers (reverse-DNS, lowercase ASCII).
- Never reuse an ID with new meaning.
- Keep schemas extension-preserving and add `extensions` maps.
- Declare units for every numeric value.
- Do not encode real-world semantics or gameplay rules.

## Add a new material family
1. Create a new material record in your pack using `schema/material.schema`.
2. Choose a stable `material_id` under your namespace.
3. Populate `traits`, `manufacturability`, and `failure_params` with declarative values.
4. Populate `unit_annotations` for any numeric entries inside those maps.
5. Keep `provenance` and `extensions` present.

## Add a new process family
1. Create a record under `schema/process_family.schema`.
2. Choose a stable `process_family_id`.
3. Fill `inputs`, `outputs`, `wastes`, and `parameter_space` with declarative IO.
4. Add `required_instruments` and `required_standards` if relevant.
5. Ensure all numeric entries are annotated in `unit_annotations`.

## Define a machine or building via assemblies
1. Create parts using `schema/part.schema`.
2. Create interfaces using `schema/interface.schema`.
3. Reference parts and interfaces in `schema/assembly.schema`:
   - `nodes` define parts/subassemblies.
   - `edges` connect interfaces.
   - `subsystems` name important subgraphs.
4. Use `hosted_processes` to reference process families only.

## Add standards and instruments
1. Define standards in `schema/standard.schema` with `scope` and tolerances.
2. Define instruments in `schema/instrument.schema` and reference standards.
3. Keep all numeric values unit-annotated and extension-preserving.

## Extend schemas safely
1. Add new fields only inside `extensions`.
2. Never remove or rename existing fields.
3. If semantics must change, mint new IDs and new versions.
4. Keep unknown fields during round-trip serialization.

## Common mistakes and refusal reasons
- Using non-namespaced IDs → refusal for namespace violation.
- Reusing an ID with new meaning → refusal for semantic reuse.
- Missing `extensions` or dropping unknown fields → schema contract violation.
- Missing unit annotations for numeric values → unit policy refusal.
- Encoding behavior or gameplay rules in schema → CODE_KNOWLEDGE_BOUNDARY violation.

## References
- `docs/arch/FABRICATION_MODEL.md`
- `docs/arch/ID_AND_NAMESPACE_RULES.md`
- `docs/arch/UNIT_SYSTEM_POLICY.md`
- `docs/arch/CODE_KNOWLEDGE_BOUNDARY.md`
