# Distribution Layout (DIST0)

Status: binding.
Scope: installed binaries and data root layout.

## Install layout (example)
```
install/
├── bin/
├── licenses/
└── data/    # runtime data root (relocatable)
```

Rules:
- Installers place binaries and create data root.
- No content installed by default.
- Data root is selectable via `--data-root`.

## See also
- `docs/arch/INSTALLER_CONTRACT.md`
- `docs/arch/LAUNCHER_CONTRACT.md`
