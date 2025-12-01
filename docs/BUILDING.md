
# Dominium — BUILDING & PLATFORM RULES

---

## 1. SUPPORTED BUILD SYSTEMS

- CMake (primary)
- Make (Linux/minimal)
- MSVC project files (legacy)

---

## 2. TARGET PLATFORMS

### Stage 1
- Windows 2000+
- macOS 10.6+
- Linux (glibc ≥ 2.5)

### Stage 2
- Windows 98 SE+
- macOS 7–9 (via Carbon shim or custom backend)
- DOS (DPMI) experimental

### Future
- iOS / Android
- WebAssembly
- Consoles (Switch, PS2, PS3, etc.)

---

## 3. GRAPHICS BACKENDS

Initial:
- SDL1
- SDL2
- OpenGL 1.1
- OpenGL 2.0
- DirectX 9.0c

Later:
- DirectX 11
- Software renderer

---

## 4. BUILD MODES

- `Debug`
- `Release`
- `DeterministicRelease` (strict FP, lockstep)

---

## 5. OUTPUT ARTIFACTS

The build must produce:

- `dom_client` (GUI)
- `dom_server` (headless)
- `dom_hclient` (headless client)
- `dom_tools_*` (editors, converters)

