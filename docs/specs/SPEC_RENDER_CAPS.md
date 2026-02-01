Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# RenderCaps Specification (REND0)

RenderCaps is the canonical capability contract. It is versioned and enforced.
RenderCaps is the only basis for backend selection and tiering.

## RenderCaps Schema (Versioned)

RenderCaps MUST declare:

- `caps_version` (semantic version)
- `backend_identity` (stable id string; renderer identity)
- `backend_family` (enum; see SPEC_RENDERING_CANON)
- `pipeline_model` (Explicit | Implicit | ProgrammableLegacy | FixedFunction)
- `limits` (binding limits, buffer sizes, counts)
- `formats` (required format support sets)
- `features` (capability bits)
- `timing` (gpu timestamp support, determinism flags)

All fields are required unless explicitly marked optional.

## Required Fields (RenderCaps v1)

### Identity
- `caps_version` (major.minor.patch)
- `backend_identity` (string)
- `backend_family` (enum)
- `pipeline_model` (enum)

### Limits
- `max_bind_groups`
- `max_bindings_per_stage`
- `max_uniform_bytes`
- `max_storage_bytes`
- `max_textures`
- `max_samplers`
- `max_render_targets`
- `max_push_constants`
- `max_vertex_attrs`
- `max_instances`
- `max_draw_indirect`

### Formats
- `color_formats` (required set)
- `depth_formats` (required set)
- `compute_formats` (required set)
- `sRGB_support` (boolean)

### Features
- `supports_compute`
- `supports_multisample`
- `supports_timestamp`
- `supports_bindless` (if present, must specify limits)
- `supports_sparse` (if present, must specify constraints)
- `supports_multiview`

### Determinism
- `deterministic_formats` (boolean)
- `deterministic_barriers` (boolean)
- `deterministic_shaders` (boolean)

## Tier Derivation (Deterministic)

Tiers are derived from RenderCaps ONLY, never from API names.

Example tier mapping (authoritative):
- Tier 0 (FixedFunction): pipeline_model == FixedFunction
- Tier 1 (ProgrammableLegacy): pipeline_model == ProgrammableLegacy
- Tier 2 (Implicit): pipeline_model == Implicit and supports_compute == true
- Tier 3 (Explicit): pipeline_model == Explicit and supports_timestamp == true

Tier derivation MUST be deterministic and documented in code.

## Capability Negotiation

- Selection MUST use RenderCaps and requested tier/feature intent.
- All selected caps MUST be logged and audited.
- RenderCaps MUST be hashed deterministically (sorted fields) and recorded in run_root.

## Prohibitions

- Selection by API name is FORBIDDEN.
- Unversioned RenderCaps is FORBIDDEN.
- Missing required fields is REFUSE.