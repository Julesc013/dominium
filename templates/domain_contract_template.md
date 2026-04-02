Status: TEMPLATE
Last Reviewed: 2026-04-02
Supersedes: none
Superseded By: none
Template Version: 1.0.0
Compatibility: Must inherit `specs/reality/SPEC_DOMINIUM_UNIVERSAL_REALITY_FRAMEWORK.md` v1.0.0 and conform to `schema/reality/domain_contract.schema.json`.
Stability: template
Future Series: Λ, Σ, Φ
Replacement Target: instantiate into concrete domain constitutions rather than edit the template ad hoc

# Domain Contract Template

Use this template to author a lawful Dominium domain constitution.

Rules:

- Do not redefine Truth, Perceived, Rendered state, sparse materialization, causal closure, substitution law, or continuity locally.
- If something is not yet defined, say `none declared` or `provisional` explicitly. Do not leave it implicit.
- If ownership overlaps with `schema` / `schemas`, `packs` / `data/packs`, or other live split zones, record that in scope and compatibility notes. Do not silently choose a winner here.
- Recognitions are not primitives.
- Observation is not truth.
- Substitutions are not implicit.

---

# Domain Contract: [DOMAIN_NAME]

## 1. Identity

Schema section: `identity`

- `domain_id`:
- `domain_name`:
- `domain_summary`:
- `domain_classes`:
- `phenomenon_scope`:
- `authority_roots`:
- `owned_truth_classes`:
- `declared_related_roots`:

Guidance:

- Keep this explicit and bounded.
- Cite live repo embodiment roots where helpful.
- Do not use path names alone as ontology.

## 2. Framework Inheritance

Schema section: `inherits_from_framework`

- `artifact_id`: `spec.dominium.universal_reality_framework`
- `minimum_version`: `1.0.0`
- `prohibited_local_redefinitions`:
- `notes`:

Guidance:

- This section is mandatory.
- A domain may specialize the framework. It may not compete with it.

## 3. Scope

Schema section: `scope`

- `governs`:
- `boundary_claims`:
- `explicit_non_goals`:
- `overlap_statement`:
- `known_overlap_zones`:
- `ownership_notes`:

Guidance:

- State exactly what the domain governs.
- State what it does not govern.
- Record overlap or quarantine-sensitive surfaces explicitly.
- If there are no known overlaps, say so directly.

Anti-pattern warning:

- Do not write scope as "everything related to X."
- Do not hide `field` / `fields`, `schema` / `schemas`, or `packs` / `data/packs` sensitivity if it matters.

## 4. Primitive Substrate

Schema section: `primitive_substrate`

- `primitive_units`:
- `truth_bearing_entities`:
- `primitive_invariants`:
- `primitive_refusal_conditions`:
- `higher_order_semantics_not_implicit`: `true`
- `source_roots`:
- `notes`:

Guidance:

- Define the lowest-level truth-bearing substrate the domain owns.
- Keep higher-order meaning out of primitives unless declared explicitly.
- If a concept is recognized, institutional, or interface-facing, it probably is not primitive.

## 5. Process Model

Schema section: `process_model`

- `truth_mutation_rule`: `truth_mutation_only_through_processes`
- `processes`:
- `process_invariants`:
- `process_scope_notes`:

Guidance:

- Every authoritative change path must be expressed through Processes.
- For each Process, state inputs, outputs, invariants, refusal conditions, and determinism notes.
- If external Processes own mutation, say so explicitly.

## 6. Recognition Model

Schema section: `recognition_model`

- `recognitions`:
- `recognitions_cannot_replace_primitives`: `true`
- `recognition_notes`:

Guidance:

- Recognitions are derived patterns or classifications over truth.
- If none are declared yet, say `none declared` and explain.

Anti-pattern warning:

- Do not use recognitions as a substitute for primitive substrate.

## 7. Affordance Model

Schema section: `affordance_model`

- `affordances`:
- `law_gated_affordances_only`: `true`
- `affordance_notes`:

Guidance:

- List actors, authority conditions, Process references, capability references, and refusal conditions.
- Affordances are lawful action surfaces, not UI shortcuts.

## 8. Formalization Model

Schema section: `formalization_model`

- `formalization_policy`: `defined` | `none_declared`
- `formalizations`:
- `formalization_notes`:

Guidance:

- Use this for standards, models, blueprints, institutional declarations, or other explicit formal artifacts.
- If none exist yet, state `none declared` explicitly.

## 9. Representation Model

Schema section: `representation_model`

- `representations`:
- `representation_invariants`:
- `substitution_policy.mode`: `none_declared` | `lawful_substitutions_defined`
- `substitution_policy.implicit_substitution_forbidden`: `true`
- `substitution_policy.substitutions`:
- `representation_notes`:

Guidance:

- Every representation must state what it preserves and what horizon it is valid for.
- If substitutions are allowed, define preserved invariants, continuity conditions, activation conditions, and refusal conditions.
- If substitutions are not defined, say so explicitly.

Anti-pattern warning:

- Do not imply capsules or substitutions without writing them down.

## 10. Failure Model

Schema section: `failure_model`

- `ordinary_vs_failure_boundary`:
- `failure_modes`:
- `degradation_rules`:
- `failure_notes`:

Guidance:

- Distinguish degraded, invalid, unsafe, unknown, and absent states where relevant.
- State what failure does to truth, observation, refusal, and recovery.

## 11. Verification

Schema section: `verification`

- `invariants`:
- `audit_surfaces`:
- `replay_requirements`:
- `determinism_requirements`:
- `proof_artifacts`:
- `verification_notes`:

Guidance:

- State what later tooling or review should be able to check.
- Include manual checks if automation does not exist yet.

## 12. Observation Bindings

Schema section: `observation_bindings`

- `truth_is_not_observation`: `true`
- `bindings`:
- `observation_notes`:

Guidance:

- Describe channels, epistemic artifacts, and redaction or quantization rules.
- Observation remains derived from truth.

Anti-pattern warning:

- Do not let observation summaries stand in for truth structure.

## 13. Interface Bindings

Schema section: `interface_bindings`

- `reality_is_interface_agnostic`: `true`
- `embodied_user`:
- `abstract_planner`:
- `ai_agent`:
- `npc_actor`:
- `system_actor`:
- `interface_notes`:

Guidance:

- Every class must be addressed explicitly, even if the answer is `not_supported`.
- Record interaction modes, observation dependencies, refusal conditions, and notes.

## 14. Compatibility And Stability

Schema section: `compatibility_and_stability`

- `contract_version`:
- `stability`:
- `replacement_target`:
- `future_series_note`:
- `compatibility_considerations`:
- `semantic_contract_pin.framework_artifact_id`: `spec.dominium.universal_reality_framework`
- `semantic_contract_pin.framework_version_minimum`: `1.0.0`
- `semantic_contract_pin.prohibited_local_redefinitions`:
- `ownership_sensitivity_notes`:

Guidance:

- Use this section to pin the contract semantically.
- If the domain is provisional, say what replaces it later.
- Record overlap or compatibility sensitivity explicitly.

## 15. Civilization Scaling Path

Schema section: `civilization_scaling_path`

- `scale_model.supports_macro`:
- `scale_model.supports_micro`:
- `scale_model.intermediate_bands`:
- `macro_summary_rules`:
- `micro_detail_triggers`:
- `continuity_requirements`:
- `scale_notes`:

Guidance:

- Explain how the domain works across large-scale summaries and local detail.
- State what must remain consistent across scale changes.

## 16. Mod And Extension Path

Schema section: `mod_extension_path`

- `pack_extension_points`:
- `specializable_elements`:
- `non_overridable_elements`:
- `compatibility_requirements`:
- `refusal_rules`:
- `extension_notes`:

Guidance:

- Record how packs or mods may extend the domain lawfully.
- State what is specializable and what must never be overridden.
- Missing or invalid extensions must refuse or degrade explicitly.

## 17. Minimum Completeness Check

Complete this checklist before treating the domain as constitutionally valid:

- inheritance from `Λ-0` is explicit
- identity and scope are explicit
- overlap zones are declared or explicitly absent
- primitive substrate is defined
- Process mutation path is defined
- recognitions are defined or explicitly absent
- affordances are defined or explicitly absent
- formalization posture is explicit
- representation and substitution posture is explicit
- failure semantics are explicit
- verification surfaces are explicit
- observation bindings are explicit
- interface bindings are explicit
- compatibility and stability metadata are explicit
- scaling path is explicit
- mod and extension path is explicit

Refuse to advance the domain if any of those remain implicit.
