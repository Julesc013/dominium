# MOD-PACK-TRUST-MODEL-01 Fixtures

These fixtures exercise the provisional mod/pack trust law without enabling a
mod loader, sandbox runtime, native loader, package mount runtime, or Workbench
UI.

The validator checks that:

- data-only packs cannot request filesystem, network, process, or native authority;
- external process adapters declare protocol, process, network/filesystem, and determinism impact;
- native providers require native trust policy and evidence;
- pack overlays cannot silently overwrite conflicts;
- every requested permission is declared;
- determinism impact is explicit.

Run:

```text
python tools/validators/package/check_mod_pack_trust.py --repo-root . --fixtures
```
