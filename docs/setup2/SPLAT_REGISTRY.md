# Setup2 SPLAT Registry (SR-1 stub)

## Registered SPLAT IDs
- `splat_portable`
- `splat_win32_nt5`
- `splat_macos_pkg`
- `splat_linux_deb`
- `splat_linux_rpm`
- `splat_steam`

## Selection rules
1) If `requested_splat` is present and exists, select it.
2) Else select by request platform triple when allowed by manifest targets.
3) Else fall back to `splat_portable`.

Candidates and rejections are always recorded in the audit selection reason.
