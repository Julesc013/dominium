# SERVICES_FACADES

All Layer 1 services are vtables with an opaque `ctx` pointer. No global state.

FS (dss_fs)
- read_file_bytes, write_file_bytes_atomic, make_dir, remove_file, remove_dir_if_empty
- list_dir (sorted), canonicalize_path, join_path, temp_dir
- atomic_rename, dir_swap, exists, file_size
- Fake backend enforces sandbox root and rejects path traversal.

PROC (dss_proc)
- spawn(argv, env, cwd, capture flags)
- Fake backend returns deterministic exit + empty output.

HASH (dss_hash)
- compute_digest64_bytes
- compute_digest64_file
- Uses FNV-1a 64 to match kernel digest.

ARCHIVE (dss_archive)
- extract_deterministic
- validate_archive_table
- Real backend uses the deterministic DSU archive format.

PERMS (dss_perms)
- is_elevated, request_elevation_supported
- get_user_scope_paths, get_system_scope_paths
- SR-2 uses stubs with stable signatures.

PLATFORM (dss_platform)
- get_platform_triple, get_os_family, get_arch
- Fake backend returns configured triple.

REGISTRY_WIN / PKGMGR_LINUX / CODESIGN_MACOS
- Stub-only in SR-2; interfaces exist for future expansion.
