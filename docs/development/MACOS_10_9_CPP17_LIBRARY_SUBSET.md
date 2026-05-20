Status: DERIVED
Last Reviewed: 2026-05-21
Supersedes: none
Superseded By: none
Stability: provisional
Binding Sources: `contracts/build/language_baseline.contract.toml`

# macOS 10.9 C++17 Library Subset

Dominium may compile C++ as C++17 while still targeting macOS 10.9.5, but not
every C++17 standard-library surface is acceptable as a required dependency.

## Forbidden Required Surfaces

Do not require these in mainline code that must support macOS 10.9.5:

- `std::filesystem`
- `std::pmr` / `<memory_resource>`
- `std::to_chars` / `std::from_chars`
- `std::any`
- throwing `std::optional::value()` paths
- throwing `std::variant` access paths

The validator fails high-confidence uses of the forbidden headers or namespaces
and warns on optional/variant patterns that need review.

## Preferred Project Patterns

- project path abstraction instead of `std::filesystem`
- explicit result values instead of exceptions in low-level paths
- `has_value`, `operator bool`, and `operator*` instead of throwing
  `optional::value()`
- deterministic project serialization instead of raw type layout
- C-compatible ABI result/refusal codes at module and provider boundaries

## Validator

```text
python tools/validators/build/check_cpp17_forbidden_library_use.py --repo-root . --strict
```
