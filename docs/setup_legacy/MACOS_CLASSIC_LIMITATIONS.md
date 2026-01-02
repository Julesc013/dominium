Mac OS Classic Limitations

Scope and Constraints
- Classic Mac OS cannot run the modern Setup Core; it uses a legacy profile.
- No external downloads; all payloads must be on the disk image.
- No Apple branding or copied text is used.

Legacy Capability Profile
- Supported: manifest/invocation TLV subset, copy/delete/mkdir, basic journaled rollback, basic verify.
- Hashing: full SHA-256 validation is not performed; size checks are used.
- Component selection may be flattened where tree UI is not feasible.

OS Band Notes
- Band A (8.1-9.2.2): HFS+ supported; larger volumes OK.
- Band B (System 7.x): HFS only; path length and resource fork behaviors vary.
- System 6: not guaranteed; requires additional testing and tooling.

State Compatibility
- Installed-state is written in DSUS TLV format with zeroed SHA-256 fields.
- This state is compatible with importer/launcher logic that skips unknown or zeroed hashes.

TUI/CLI
- A real TUI is not guaranteed on Classic systems without console access.
- CLI mode is provided for scripted installs where a console exists.

Toolchain
- The Classic GUI app is a source scaffold; build with MPW/Think C or CodeWarrior.
- Define `DSU_CLASSIC_MAC` to enable Dialog Manager calls.
