# Dominium — LANGUAGE POLICY

This document defines universal rules for all Dominium source code. These are mandatory.

---

## 1. C89 RULES (CORE ENGINE)

The simulation core, deterministic systems, and all portable foundation modules MUST compile cleanly as C89 under:

- MSVC 6.0+
- mingw32
- gcc for Linux
- clang for macOS 10.6+

### C89 Restrictions

- No `stdbool.h`, `stdint.h`, or C99 headers.
- No mixed declarations and statements.
- No C99-style `//` comments.
- No variable-length arrays.
- No designated initialisers.
- No implicit function declarations.
- No non-portable extensions (e.g., GNU VLA, MSVC declspecs).

### Allowed Standard Library
- `<stdio.h>`
- `<string.h>`
- `<stdlib.h>`
- `<stddef.h>`
- `<limits.h>`
- `<float.h>`

No other headers may be included unless platform-layer wrappers provide compatibility shims.

---

## 2. C++98 RULES (NON-CORE MODULES)

For optional modules that do not participate in deterministic simulation:

- Must compile as C++98.
- No exceptions.
- No RTTI.
- No STL containers exposed across API boundaries.
- Internally, STL containers are allowed but discouraged.
- No templates beyond basic utility templates.

---

## 3. DETERMINISM REQUIREMENTS

The entire simulation must be reproducible across:

- Windows 2000+
- macOS 10.6+
- Linux (various distros)
- future retroports (DOS, Win95, Win3.x, Classic MacOS)

### Determinism Rules

- No `rand()` or OS RNG sources.
- No time‐dependent behaviour.
- No floating-point non-determinism (strict FP mode).
- All randomness must come from a seeded software RNG (xoroshiro, LCG, etc.).
- All update ordering must be fixed and documented.
- Multithreading must follow fixed work scheduling (no racing, no nondeterministic queues).

---

## 4. PLATFORM ABSTRACTION

No platform-specific code is allowed in core modules.

Each OS/graphics backend must be behind a platform interface.

---

## 5. MEMORY RULES

- No allocator churn in the simulation loop.
- All memory must be allocated during load or expansion phases.
- No global mutable state unless defined in the spec.
- No hidden singletons.

---

## 6. DATA INTEGRITY

All serialised forms must be:

- endian-neutral
- alignment-neutral
- forward/backward compatible

