Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

# install_request.tlv (SR-4)

All integers are little-endian.

## File header
Same as `install_manifest.tlv` (magic `DSK1`, version `1`, endian `0xFFFE`).

## Top-level TLVs
- `0x2001` `operation` (u16: install=1, repair=2, uninstall=3, verify=4, status=5, upgrade=6)
- `0x2002` `requested_components` (container)
- `0x2003` `excluded_components` (container)
- `0x2004` `install_scope` (u16: user=1, system=2, portable=3)
- `0x2005` `preferred_install_root` (string, optional)
- `0x2006` `ui_mode` (u16: gui=1, tui=2, cli=3)
- `0x2007` `requested_splat_id` (string, optional)
- `0x2008` `policy_flags` (u32 bitset)
- `0x2009` `target_platform_triple` (string)
- `0x200A` `required_caps` (u32 bitset, optional)
- `0x200B` `prohibited_caps` (u32 bitset, optional)
- `0x200C` `ownership_preference` (u16: any=0, portable=1, pkg=2, steam=3; optional)
- `0x200D` `payload_root` (string, optional; defaults to manifest directory)
- `0x200E` `frontend_id` (string, required)

### requested_components container
- `0x2010` `requested_component_entry` (string)

### excluded_components container
- `0x2011` `excluded_component_entry` (string)

## Cap bits (required/prohibited)
- `0x0001` atomic_swap
- `0x0002` resume
- `0x0004` pkg_ownership
- `0x0008` portable_ownership
- `0x0010` shortcuts
- `0x0020` file_assoc
- `0x0040` url_handlers
- `0x0080` codesign_hooks
- `0x0100` pkgmgr_hooks
- `0x0200` steam_hooks

## Canonical ordering
- `requested_components` and `excluded_components` sorted by string.