# Public Header Contract Fixtures

Status: DERIVED
Last Reviewed: 2026-05-20
Supersedes: none
Superseded By: none
Stability: fixture

These fixtures exercise `tools/validators/abi/check_public_headers.py`.

- `valid_c89_header.h` models the intended stable C89-compatible public ABI shape.
- `invalid_cpp_type_header.h` intentionally leaks C++ API constructs.
- `invalid_platform_header.h` intentionally leaks a platform header.
- `valid_consumer.c` is a tiny C consumer for the valid fixture and future compile integration.

Fixtures are not product public surfaces.
