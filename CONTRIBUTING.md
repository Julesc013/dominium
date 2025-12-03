# Dominium — Contribution Requirements and Developer Contract  
## Version 1.0

This document defines the rules, constraints, and expectations for anyone wishing to contribute to the Dominium engine, game, tools, documentation, or related content.

Dominium is a **deterministic, integer-math, multi-platform simulation engine**.  
Contributions must preserve determinism, architecture, modularity, and long-term maintainability.

If a contribution violates these principles, it will not be accepted.

---

# 1. OVERVIEW

Dominium consists of:

- `/engine` — deterministic core engine  
- `/game` — Dominium gameplay layer  
- `/data` — first-party assets  
- `/mods` — third-party mod ecosystem  
- `/ports` — retro/alternative platform adapters  
- `/tools` — editors and pipelines  
- `/docs` — specifications and design rules  

This structure is governed by the **Directory Contract** in `/docs/spec/DIRECTORY_CONTRACT.md`.  
Contributions must comply with it exactly.

---

# 2. CONTRIBUTION TYPES

Accepted contribution categories:

1. **Bug fixes**  
2. **Deterministic correctness improvements**  
3. **Documentation improvements**  
4. **Specification updates**  
5. **Additions to tools/editor suites**  
6. **Rendering backend improvements**  
7. **Platform backend implementations**  
8. **Testing (unit, integration, replay)**  

The following categories are restricted or disallowed:

- **New gameplay features** — must be preceded by a spec update.  
- **Modding API changes** — must not break determinism or backwards compatibility.  
- **Simulation changes** — require design review and deterministic test coverage.  
- **Asset additions** — require compliance with licensing and file format rules.

---

# 3. CONTRIBUTION FLOW

Every contribution follows this sequence:

1. **Issue or Proposal Opened**  
   - Describe the problem, not the solution.  
   - Reference relevant sections of the spec.

2. **Specification Review (if needed)**  
   - Simulation-affecting changes must update `/docs/spec/SPEC-core.md` first.  
   - Rendering/platform-only changes may skip this.

3. **Pull Request**  
   Must include:
   - Exact files changed  
   - Rationale  
   - Determinism impact analysis  
   - Test coverage  
   - Code style compliance  

4. **CI Determinism Validation**  
   - Replay tests  
   - Hash-based world state comparisons  
   - Cross-platform determinism checks  

5. **Human Review**  
   Reviews focus on:
   - Architectural compliance  
   - Determinism  
   - Abstraction boundaries  
   - Maintainability  
   - Simplicity  

6. **Merge or Revision Requested**

---

# 4. CODING STANDARDS

### 4.1 Language Restrictions  
- `/engine/core` and `/engine/sim` must use **strict C89**.  
- High-level game code may use **C++98** but not beyond.  
- No exceptions, RTTI, templates, or STL.  
- No C99/C11 features.  
- No floating-point in simulation.  
- No platform headers in engine code.

### 4.2 Naming Conventions  
Everything in the engine follows:

dom_<subsystem><module><function>()
DOM_<SUBSYSTEM><CONST_NAME>
dom<structname>_t

Game code follows parallel conventions:

dg_<module>action()
dg<component>_t

### 4.3 File Structure  
Each module pair must be:

something.h
something.c

No header-only simulation code.  
All private helper functions must be `static` in `.c` files.

### 4.4 Include Rules  
- Headers include only forward declarations or minimal engine headers.  
- No circular includes.  
- No platform or OS headers in the engine.  
- No third-party headers outside `/external`.

### 4.5 Memory Rules  
- No malloc inside tight loops.  
- No unbounded allocations.  
- All simulation memory must be owned by a stable allocator.  
- Pointers must never be persisted across simulation frames unless explicitly guaranteed stable.

---

# 5. DETERMINISM REQUIREMENTS

Every contribution must maintain determinism across:

- CPU architectures  
- Endianness  
- Compilers  
- Operating systems  
- Rendering backends  
- Platform backends  

### Determinism Prohibitions  
- No random numbers without using `dom_core_rng`.  
- No floating-point arithmetic in simulation.  
- No time-based behaviour.  
- No OS-dependent scheduling or file operations.  
- No thread-based race conditions.  
- No reliance on undefined or implementation-defined C behaviour.  

---

# 6. TESTING REQUIREMENTS

All contributions must include:

### 6.1 Unit Tests  
Under `/tests/unit`.

### 6.2 Integration Tests  
Under `/tests/integration`.

### 6.3 Replay Determinism Tests  
Under `/tests/replay`.

Simulation bugs are not accepted without a replay test demonstrating reproducibility.

---

# 7. DIRECTORY BOUNDARY RULES (MANDATORY)

### 7.1 `/engine`  
Contains deterministic engine logic only.  
No game rules.  
No assets.  
No platform-specific code.  
No OS calls.

### 7.2 `/engine/platform`  
Contains OS-specific wrappers only.  
No simulation code.  
No rendering or audio code.

### 7.3 `/engine/render`  
Rendering backends only.  
No simulation logic.  
No gameplay rules.

### 7.4 `/game`  
Contains gameplay layer.  
Must not depend on platform code directly.

### 7.5 `/data`  
Contains assets.  
No executable code.

### 7.6 `/mods`  
User mods.  
Must not modify engine source.  
Must not introduce nondeterministic behaviour.

### 7.7 `/ports`  
Experimental or legacy platform adapters.  
Must not alter core engine architecture.

Breaking boundary rules is grounds for rejection.

---

# 8. DOCUMENTATION REQUIREMENTS

Every contribution must:

- Document all new functions in headers.  
- Update relevant sections of `/docs/spec`.  
- Provide comments explaining invariants, constraints, and determinism concerns.  
- Include diagrams or flow descriptions for complex systems.  
- Provide rationale for architectural decisions.  

Undocumented contributions will not be merged.

---

# 9. SECURITY & SAFETY REQUIREMENTS

Contributions must not introduce:

- Unsafe memory behaviour  
- Buffer overflows  
- Undefined behaviour  
- Race conditions  
- Input handling vulnerabilities  
- Unbounded loops  
- Crash-on-invalid-input scenarios  

All file formats must validate input boundaries.

---

# 10. REVIEW HIERARCHY

If a contribution touches any of the following, it requires **architectural approval**:

- Simulation tick pipeline  
- Determinism kernel  
- ECS model  
- Serialization  
- Networking  
- Rendering abstraction  
- Platform abstraction  
- Modding API  

Minor cosmetic fixes do not require full review.

---

# 11. WHAT WILL NOT BE ACCEPTED

The following contributions are automatically rejected:

- Floating-point simulation logic  
- Non-deterministic features  
- Platform-dependent behaviour in engine code  
- Refactors that degrade clarity  
- Memory-increasing changes without justification  
- C99/C11/C++11 syntax  
- Gameplay changes without corresponding spec updates  
- Engine redesign proposals outside spec boundaries  
- Attempts to bypass the Directory Contract  
- New dependencies not approved by maintainers  

---

# 12. HOW TO GET STARTED

1. Read `/docs/spec/SPEC-core.md`  
2. Read `/docs/spec/DIRECTORY_CONTRACT.md`  
3. Build the engine following `/docs/spec/BUILDING.md`  
4. Run deterministic replay tests  
5. Open an issue describing the intended contribution  
6. Await architectural approval before writing major code  

---

# 13. CONTACT

Development discussion channels will be posted after public release.  
Until then, use GitHub Issues for all proposals and discussions.

---

# 14. LEGAL

Contributions may only be accepted if the contributor agrees to assign or license the contribution to the Author under terms consistent with the project’s restrictive licensing.

No contributor gains copyright ownership of the project.

---

# 15. FINAL NOTES

Dominium is built for longevity, determinism, and correctness.  
Code must be simple, predictable, and maintainable for decades.  
Contributors are expected to uphold these principles.
