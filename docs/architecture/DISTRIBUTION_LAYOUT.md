Status: CANONICAL
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

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


- `docs/architecture/INSTALLER_CONTRACT.md`


- `docs/architecture/LAUNCHER_CONTRACT.md`
