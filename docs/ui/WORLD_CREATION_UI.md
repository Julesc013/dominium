Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# World Creation UI

The world creation UI is a thin shell over the template registry.
It does not infer or mutate the generated WorldDefinition.

Core steps:
1) Enumerate templates from the built-in registry (zero packs required).
2) Select a template.
3) Edit parameters declared by the template:
   - seed(s)
   - policy sets (movement/authority/mode/debug)
   - template-specific toggles/sizes (if declared)
4) Generate a WorldDefinition.
5) Write the WorldDefinition into a save file.

Constraints:
- No content packs are required to create a world.
- No hardcoded topology, bodies, or spawn locations.
- No implicit defaults beyond what the template declares.
- Policy layers are explicit and recorded in the WorldDefinition.
- Template provenance is preserved (template_id, version, generator source, seed).

Built-in templates (MVP, zero-asset):
- Empty Universe
- Minimal System
- Realistic Test Universe (labels only; no asset assumptions)

Outputs:
- Save file contains full WorldDefinition and summary metadata.
- Any unknown fields in the WorldDefinition are preserved on round-trip.