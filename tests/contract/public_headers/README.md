# Public Header Contract Fixtures

Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: fixture

These fixtures exercise `tools/validators/abi/check_public_headers.py`.

- `valid_c17_header.h` models the intended stable C17 C-compatible public ABI shape.
- `invalid_cpp_type_header.h` intentionally leaks C++ API constructs.
- `invalid_platform_header.h` intentionally leaks a platform header.
- `valid_consumer.c` is a tiny C consumer for the valid fixture and future compile integration.

Fixtures are not product public surfaces.
