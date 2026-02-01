Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# Game Primitives and Interfaces (Normative)





This document is normative for the game layer. It MUST be read alongside


`docs/architectureitecture/INVARIANTS.md` and `docs/architectureitecture/TERMINOLOGY.md`.





## Work IR Emission





- Simulation systems MUST emit Work IR deterministically.


- Work IR MUST reflect process intent; it MUST NOT embed hidden mutations.


- Canonical interface: `game/include/dominium/execution/system_iface.h`





## Process Descriptors





- Game systems MUST describe processes using engine process descriptors.


- Process descriptors MUST declare capabilities, authority scope, domains,


  and costs.


- Canonical interface: `game/include/dominium/execution/process_iface.h`


- Engine process definitions live in `engine/include/domino/process.h`.





## Epistemic / Subjective Views





- Subjective views MUST be explicit, deterministic, and non-authoritative.


- Knowledge state MUST differentiate known, inferred, and unknown.


- Canonical interface: `game/include/dominium/epistemic.h`


- Engine knowledge metadata is defined in `engine/include/domino/knowledge_state.h`.





## Authority and Capability Binding





- Game rules MUST request authority via engine authority tokens.


- Game rules MUST declare capability requirements explicitly.


- Authority tokens MUST NOT be forged or escalated.


- Canonical interfaces: `engine/include/domino/authority.h`,


  `engine/include/domino/capability.h`





## Determinism and Provenance





- All rule emission and process scheduling MUST be deterministic.


- Randomness MUST use explicit seed namespaces and deterministic derivations.


- Provenance MUST attach to rule execution and derived data.


- Canonical interface: `engine/include/domino/provenance.h`





## Compatibility Modes





- Game logic MUST respect explicit compatibility modes and degradation rules.


- Authoritative operation MUST NOT proceed when required capabilities are missing.


- Canonical interface: `engine/include/domino/compat_modes.h`





## Universal Pack System (UPS)





- The game MUST register pack manifests with the engine UPS before loading content.


- The game MUST resolve content by capability, not by file path or pack name.


- Pack precedence MUST be explicit and data-driven.


- Canonical interfaces: `engine/include/domino/ups.h`, `game/include/dominium/ups_runtime.h`





## Enforcement Status (Explicit Gaps)





To preserve current behavior, the following norms are specified but not yet


enforced in implementation:





- Work IR is not yet strictly derived from process descriptors in all systems.


- Authority token checks are not yet applied to all mutating rule paths.


- Compatibility negotiation is not yet mandatory for pack/mod/save resolution.





These gaps MUST be resolved only via explicit breaking revision.
