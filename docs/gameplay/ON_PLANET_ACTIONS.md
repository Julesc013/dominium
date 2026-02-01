Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# On-Planet Actions





This document defines the universal action grammar for on-planet activity.


It is AUTHORITATIVE for gameplay intent and MUST be read alongside:


- `docs/architectureitecture/INVARIANTS.md`


- `docs/architectureitecture/TERMINOLOGY.md`


- `docs/content/UPS_OVERVIEW.md`





## Core Rule





All on-planet actions MUST be expressed as processes operating on fields,


domains, parts, assemblies, networks, and institutional state. No special-case


mechanics are permitted.





## Required Primitives





On-planet actions MUST use these primitives from PROMPT B:


- Topology nodes and attached domains


- Domain volumes


- Fields with representation tiers


- Processes with declared inputs/outputs/waste


- Capabilities and authority tokens


- Institutional constraints as process-gated state





## Process Grammar





Every on-planet action MUST:


- Declare affected fields and domain volumes


- Declare material inputs, outputs, and waste references


- Declare time and energy cost descriptors


- Declare failure modes and provenance


- Require explicit capabilities and authority scope





Process classes MUST be used as defined in `docs/architectureitecture/TERMINOLOGY.md`.





## Conservation and Provenance





All material movement and transformation MUST be represented through process


inputs, outputs, and waste. Provenance MUST be attached to every process and


every data record referenced by the process.





## Authority and Institutions





Mutations MUST require explicit authority scope. Regulatory and ownership


constraints MUST be expressed as institutional processes, not hardcoded rules.





## Scaling and Degradation





Processes MUST support arbitrary scale and MUST allow explicit degradation or


partial simulation. No action may assume a specific tool, species, or platform.





## Schema References





This document relies on the canonical schemas:


- `schema/process.schema`


- `schema/field.schema`


- `schema/domain.schema`


- `schema/part_and_interface.schema`


- `schema/assembly.schema`


- `schema/network.schema`


- `schema/institution.schema`


- `schema/knowledge.schema`





## UPS Packaging





Action libraries MUST be delivered via UPS packs and resolved by capability.


No action may depend on file paths or mandatory content.
