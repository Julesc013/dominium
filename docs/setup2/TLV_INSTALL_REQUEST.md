# install_request.tlv (SR-1)

All integers are little-endian.

## File header
Same as `install_manifest.tlv` (magic `DSK1`, version `1`, endian `0xFFFE`).

## Top-level TLVs
- `0x2001` `operation` (u16: install=1, repair=2, uninstall=3, verify=4, status=5)
- `0x2002` `requested_components` (container)
- `0x2003` `excluded_components` (container)
- `0x2004` `install_scope` (u16: user=1, system=2, portable=3)
- `0x2005` `preferred_install_root` (string, optional)
- `0x2006` `ui_mode` (u16: gui=1, tui=2, cli=3)
- `0x2007` `requested_splat` (string, optional)
- `0x2008` `policy_flags` (u32 bitset)
- `0x2009` `platform_triple` (string)

### requested_components container
- `0x2010` `requested_component_entry` (string)

### excluded_components container
- `0x2011` `excluded_component_entry` (string)

## Canonical ordering
- `requested_components` and `excluded_components` sorted by string.
