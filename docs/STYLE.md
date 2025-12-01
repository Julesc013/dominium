# Dominium — CODE STYLE AND NAMING RULES

This file defines the coding standards for C89/C++98.

---

## 1. FILE NAMING

- All core engine C files: `dom_*.c`, `dom_*.h`
- Modules follow: `dom_<module>_<subsystem>.c`
- Tests: `tests/test_<module>.c`

---

## 2. NAMING CONVENTIONS

### Types
- `dom_<module>_<TypeName>`

### Structs
- `struct dom_<module>_<thing>`

### Functions
- `dom_<module>_<action>()`

Examples:
- `dom_rng_next_u32()`
- `dom_bus_init()`

### Constants
- `DOM_<MODULE>_<NAME>`

---

## 3. INDENTATION & FORMATTING

- 4 spaces, never tabs.
- No trailing whitespace.
- Max line length: 100 chars.
- K&R brace style:

int f(void)
{
...
}


---

## 4. ERROR HANDLING

- Core modules return error codes, never abort.
- Fatal errors go through `dom_log_fatal()`.
- Logging levels: TRACE, DEBUG, INFO, WARN, ERROR, FATAL.

---

## 5. HEADER RULES

- All headers must be self-contained.
- Include guards: `#ifndef DOM_<NAME>_H`
- No including implementation details.

---

## 6. TESTING STYLE

- Minimal C89 test harness using `fprintf`.
- Assertions implemented manually.

