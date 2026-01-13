# Dominium Security, Vulnerability, and Integrity Policy  
## Version 1.0

This document defines the security expectations, threat model, vulnerability reporting process, and architectural integrity rules governing the Dominium engine, game, tools, and ecosystem.

Dominium is a deterministic, offline-first, multi-platform engine.  
Security focuses on **code integrity**, **input validation**, **determinism preservation**, **memory safety**, and **mod sandboxing**, rather than internet threat surfaces.

---

# 1. SCOPE

This policy applies to:

- All source code under this repository  
- All binaries built from this repository  
- All asset pipelines and tools  
- All modding APIs and script runtimes  
- All network protocols used by multiplayer modes  
- All build and packaging systems  

It does **not** apply to:

- Third-party mods outside `/mods`  
- Unofficial forks  
- Server infrastructures not controlled by the Author  

---

# 2. SECURITY MODEL OVERVIEW

Dominium’s security is built on three pillars:

### 2.1 Determinism Integrity  
Simulation determinism must be preserved.  
Any deviation is categorised as a **high-severity security violation**.

### 2.2 Memory and Execution Safety  
The engine targets systems ranging from DOS to modern OSes, all in C89/C++98.  
Memory safety, overflow protection, and strict bounds checking are mandatory.

### 2.3 Mod and Input Containment  
Mods and save files must not be able to:

- Break determinism  
- Execute arbitrary system-level code  
- Modify engine binaries  
- Access system files outside allowed sandbox areas  

---

# 3. THREAT CATEGORIES

Dominium defines the following classes of threats:

---

## 3.1 Determinism Breaks  
**Severity: Critical**

Examples:

- Floating-point operations in simulation  
- Use of system time  
- Non-deterministic ordering (hash tables with unstable iteration)  
- Thread races  
- Platform-dependent branch behaviour  
- Unspecified or undefined C behaviour  

Any determinism break is treated as a security vulnerability because it compromises:

- Replays  
- Multiplayer integrity  
- Save compatibility  
- Simulation correctness  

---

## 3.2 Memory Corruption  
**Severity: Critical**

Examples:

- Buffer overflows  
- Out-of-bounds array access  
- Use-after-free  
- Double frees  
- Stack corruption  
- Integer overflow or wraparound if unchecked  

Memory corruption is unacceptable on all targets, but especially critical on retro platforms with no OS protection.

---

## 3.3 Sandbox Violations  
**Severity: High**

Mods or user content must never:

- Access system files  
- Spawn processes  
- Allocate arbitrary memory  
- Escape their data sandbox  
- Modify engine binaries or platforms  
- Inject code  

Dominium modding runs inside an explicit sandbox with restricted access.

---

## 3.4 Malicious Saves, Mods, or Packs  
**Severity: High to Critical**

The engine must defend against malformed or intentionally crafted:

- Save games  
- Map files  
- Prefab files  
- Script bundles  
- Asset packs (textures, animations)  

Every loader must:

- Validate type ranges  
- Validate lengths  
- Validate magic numbers  
- Validate version fields  
- Validate CRCs  

No untrusted binary or textual data should ever be treated as trusted input.

---

## 3.5 Network Abuse (Multiplayer)  
**Severity: Medium to Critical**

Lockstep multiplayer requires:

- Strict packet validation  
- Version matching  
- CRC checks  
- Tick-range verification  
- Rejection of malformed or unexpected packets  

Clients must not be able to:

- Inject state  
- Override authoritative simulation  
- Desync others intentionally  

Any packet that cannot be validated deterministically must be dropped.

---

## 3.6 Build Integrity Problems  
**Severity: High**

Issues include:

- Unverified third-party dependencies  
- Modification of vendored libraries without documentation  
- Compiler optimisations that break determinism  
- Toolchain inconsistencies  
- Incorrect include directories resolving differently on contributors' systems  

All builds must be reproducible using:

- Documented compilers  
- Fixed toolchain versions  
- Stable CMake rules  
- Checked-in configuration files  

---

# 4. SECURITY REQUIREMENTS FOR CONTRIBUTORS

Every contribution must:

- Avoid undefined behaviour  
- Respect memory bounds  
- Maintain determinism across all platforms  
- Use only integer or fixed-point math in simulation  
- Validate all external inputs  
- Follow platform boundaries (`source/domino/system/**` only for OS calls)  
- Use stable file formats with versioned schemas  
- Not introduce new dependencies without review  

Violations result in immediate rejection of the contribution.

---

# 5. SECURITY REQUIREMENTS FOR ENGINE CODE

Simulation and engine core must NEVER:

- Use malloc/free unpredictably  
- Use floating-point  
- Use system time  
- Use randomness outside `dom_core_rng`  
- Load or execute external code  
- Read arbitrary paths  
- Depend on OS-specific behaviour  

All engine code must remain self-contained and deterministic.

---

# 6. SECURITY REQUIREMENTS FOR MODS

Mods must:

- Not include binary code  
- Not invoke system functions  
- Not alter engine memory  
- Not modify or replace engine binaries  
- Not exceed deterministic, sandboxed scripting API  

All mod-supplied data is untrusted until validated.

---

# 7. REPORTING VULNERABILITIES

Security issues can be reported:

- Via private email (provided upon public release)  
- Via GitHub private security reports  
- Via encrypted message (PGP key will be published)  

When reporting:

1. Describe the issue clearly  
2. Provide reproduction steps  
3. Include environment (platform, compiler, config)  
4. Provide minimal test cases  

Proof-of-concept code is acceptable.  
Malicious mods or save files must be transmitted privately.

---

# 8. DISCLOSURE POLICY

We follow **coordinated disclosure**:

- A fix is prepared internally  
- Regression tests are added  
- Maintainers coordinate with reporters  
- Patch is released with changelog notes  
- Reporter is credited unless anonymity is requested  

No details will be disclosed before a patch is available.

---

# 9. SECURITY TESTING

Before every release, the following must be executed:

### 9.1 Determinism Replays  
- Long-run deterministic tests  
- Multiple architectures  
- Cross-platform consistency checks  

### 9.2 Fuzzing  
All loaders (saves, maps, prefab files, data packs) must be fuzz-tested offline.

### 9.3 Static Analysis  
Mandatory runs of:

- clang-tidy  
- cppcheck  
- gcc/clang sanitizers (where determinism is not affected)  

### 9.4 Memory Profiling  
- Leak detection  
- Bounds checking  
- Valgrind (on supported systems)  

---

# 10. HANDLING OF RETRO PORT SECURITY

Retro systems (DOS, Win3.x, Win9x, macOS Classic) lack modern memory protection.  
Thus, they must be treated as:

- Hostile to themselves  
- Fully sandboxed by design  
- Never allowed to interpret unvalidated data  

Retro ports must degrade gracefully by:

- Disabling modding  
- Restricting asset loading  
- Using smaller maps  
- Enforcing stronger input checks  

---

# 11. LONG-TERM SECURITY MAINTENANCE

Dominium is designed to be playable decades from now.  
Security must therefore prioritise:

- Deterministic reproducibility  
- Integrity of archived binaries  
- Portability across compilers  
- No reliance on transient third-party ecosystems  

Any dependency or subsystem that threatens longevity will be removed.

---

# 12. CONTACT

Security contact information will be published with the first public release.

At present, security issues should be raised privately via the internal developer channel.

---

# 13. FINAL NOTE

Security is not separate from determinism.  
A deterministic engine is inherently more secure because:

- State cannot be manipulated unpredictably  
- Bugs appear reproducibly  
- Exploits cannot rely on timing variance  
- Replay tests expose corruption rapidly  

Preserve determinism.  
Preserve safety.  
Preserve correctness.
