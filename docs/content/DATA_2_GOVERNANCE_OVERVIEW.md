Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# DATA-2 Governance Overview

Purpose: Provide optional, data-only governance packs so permissions, safety, enforcement, and anarchy emerge from the same process + authority framework. No engine/game code changes are required.

Packs and maturity:
- org.dominium.core.institutions.basic — STRUCTURAL
- org.dominium.core.law.basic — STRUCTURAL
- org.dominium.core.contracts.basic — PARAMETRIC
- org.dominium.core.standards.certification — PARAMETRIC
- org.dominium.core.instruments.inspection — PARAMETRIC
- org.dominium.core.enforcement.basic — BOUNDED

How gameplay emerges from data:
- Law is expressed as process families, constraints, and refusal codes.
- Institutions provide jurisdiction, legitimacy tags, and authority references.
- Enforcement is modeled as process families with parameterized error, bias, and corruption envelopes.

Anarchy vs regulation:
- Anarchy is the absence of law/institution/enforcement packs.
- Regulation is the presence of those packs and their data-driven constraints.
- No special code paths are used; only pack selection changes.

Corruption and failure modeling:
- Corruption likelihood, error rates, and bias are parameter fields in enforcement processes.
- Refusals and outcomes are deterministic and data-driven.

Modding guidance:
- Add new institutions, law families, and enforcement profiles by extending schemas and using new IDs.
- Do not reuse IDs or encode domain semantics; keep processes generic and parameterized.
- If a new concept cannot be expressed, document the gap rather than adding code.

Fixtures:
- tests/fixtures/data_2 includes lockfiles and variants for anarchy, light regulation, and strict regulation.
- These fixtures are intended to drive deterministic tests without requiring any hardcoded governance logic.