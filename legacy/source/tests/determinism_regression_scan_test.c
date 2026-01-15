/*
FILE: source/tests/determinism_regression_scan_test.c
MODULE: Repository
LAYER / SUBSYSTEM: source/tests
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <ctype.h>
#include <stdio.h>
#include <string.h>

#include "dg_det_scan_files.h"

typedef enum det_scan_state {
    DET_SCAN_NORMAL = 0,
    DET_SCAN_LINE_COMMENT,
    DET_SCAN_BLOCK_COMMENT,
    DET_SCAN_STRING,
    DET_SCAN_CHAR
} det_scan_state;

static int det_is_ws(int c) {
    return (c == ' ' || c == '\t' || c == '\r' || c == '\v' || c == '\f');
}

static int det_is_ident_start(int c) {
    return (isalpha(c) || c == '_') ? 1 : 0;
}

static int det_is_ident(int c) {
    return (isalnum(c) || c == '_') ? 1 : 0;
}

static int det_streq(const char *a, const char *b) {
    if (!a || !b) return 0;
    return strcmp(a, b) == 0 ? 1 : 0;
}

static void det_report(const char *path, unsigned line, const char *rule, const char *detail) {
    if (!detail) {
        detail = "";
    }
    printf("determinism-scan: %s:%u: %s %s\n", path ? path : "(null)", line, rule ? rule : "(rule)", detail);
}

static int det_check_forbidden_include(const char *path, unsigned line, const char *header) {
    static const char *banned[] = {
        "time.h",
        "sys/time.h",
        "windows.h",
        "unistd.h",
        "unordered_map",
        "unordered_set"
    };
    unsigned i;
    if (!header) {
        return 0;
    }
    for (i = 0u; i < (unsigned)(sizeof(banned) / sizeof(banned[0])); ++i) {
        if (det_streq(header, banned[i])) {
            det_report(path, line, "forbidden include:", header);
            return 1;
        }
    }
    return 0;
}

static int det_scan_pp_line(FILE *f, const char *path, unsigned *io_line) {
    char buf[512];
    unsigned len = 0u;
    int c;
    const unsigned start_line = io_line ? *io_line : 0u;
    const char *p;
    char word[32];
    unsigned wi;
    char header[128];
    unsigned hi;

    if (!f || !io_line) {
        return 0;
    }

    while ((c = fgetc(f)) != EOF) {
        if (c == '\n') {
            *io_line += 1u;
            break;
        }
        if (len + 1u < (unsigned)sizeof(buf)) {
            buf[len++] = (char)c;
        }
    }
    buf[len] = '\0';

    p = buf;
    while (*p && det_is_ws((unsigned char)*p)) {
        ++p;
    }
    wi = 0u;
    while (*p && det_is_ident((unsigned char)*p)) {
        if (wi + 1u < (unsigned)sizeof(word)) {
            word[wi++] = *p;
        }
        ++p;
    }
    word[wi] = '\0';

    if (!det_streq(word, "include")) {
        return 0;
    }

    while (*p && det_is_ws((unsigned char)*p)) {
        ++p;
    }
    if (*p != '<' && *p != '"') {
        return 0;
    }

    {
        const char end = (*p == '<') ? '>' : '"';
        ++p;
        hi = 0u;
        while (*p && *p != end) {
            if (hi + 1u < (unsigned)sizeof(header)) {
                header[hi++] = *p;
            }
            ++p;
        }
        header[hi] = '\0';
    }

    return det_check_forbidden_include(path, start_line, header);
}

static int det_scan_file(const char *path) {
    FILE *f;
    det_scan_state st;
    unsigned line;
    int c;
    int pending_call;
    unsigned pending_line;
    int at_line_start;
    int esc;
    int prev;

    f = fopen(path, "rb");
    if (!f) {
        det_report(path, 0u, "unable to open:", "");
        return 1;
    }

    st = DET_SCAN_NORMAL;
    line = 1u;
    pending_call = 0;
    pending_line = 0u;
    at_line_start = 1;
    esc = 0;
    prev = 0;

    while ((c = fgetc(f)) != EOF) {
        if (c == '\n') {
            line += 1u;
            at_line_start = 1;
            pending_call = 0;
            pending_line = 0u;
            if (st == DET_SCAN_LINE_COMMENT) {
                st = DET_SCAN_NORMAL;
            }
            prev = 0;
            continue;
        }

        if (st == DET_SCAN_LINE_COMMENT) {
            continue;
        }
        if (st == DET_SCAN_BLOCK_COMMENT) {
            if (prev == '*' && c == '/') {
                st = DET_SCAN_NORMAL;
                prev = 0;
                continue;
            }
            prev = c;
            continue;
        }
        if (st == DET_SCAN_STRING) {
            if (esc) {
                esc = 0;
                continue;
            }
            if (c == '\\') {
                esc = 1;
                continue;
            }
            if (c == '"') {
                st = DET_SCAN_NORMAL;
            }
            continue;
        }
        if (st == DET_SCAN_CHAR) {
            if (esc) {
                esc = 0;
                continue;
            }
            if (c == '\\') {
                esc = 1;
                continue;
            }
            if (c == '\'') {
                st = DET_SCAN_NORMAL;
            }
            continue;
        }

        /* DET_SCAN_NORMAL */
        if (at_line_start && det_is_ws(c)) {
            continue;
        }
        if (at_line_start && c == '#') {
            /* Preprocessor line: currently only include bans. */
            if (det_scan_pp_line(f, path, &line)) {
                fclose(f);
                return 1;
            }
            at_line_start = 1;
            pending_call = 0;
            pending_line = 0u;
            prev = 0;
            continue;
        }
        at_line_start = 0;

        if (c == '/') {
            int n = fgetc(f);
            if (n == '/') {
                st = DET_SCAN_LINE_COMMENT;
                continue;
            }
            if (n == '*') {
                st = DET_SCAN_BLOCK_COMMENT;
                prev = 0;
                continue;
            }
            if (n != EOF) {
                ungetc(n, f);
            }
        }

        if (c == '"') {
            st = DET_SCAN_STRING;
            esc = 0;
            continue;
        }
        if (c == '\'') {
            st = DET_SCAN_CHAR;
            esc = 0;
            continue;
        }

        if (det_is_ident_start(c)) {
            char tok[64];
            unsigned ti = 0u;
            int n;

            tok[ti++] = (char)c;
            while ((n = fgetc(f)) != EOF && det_is_ident(n)) {
                if (ti + 1u < (unsigned)sizeof(tok)) {
                    tok[ti++] = (char)n;
                }
            }
            tok[ti] = '\0';
            if (n != EOF) {
                ungetc(n, f);
            }

            if (det_streq(tok, "float") || det_streq(tok, "double")) {
                det_report(path, line, "forbidden fp type:", tok);
                fclose(f);
                return 1;
            }

            if (det_streq(tok, "rand")) {
                pending_call = 1;
                pending_line = line;
            } else if (det_streq(tok, "srand")) {
                pending_call = 2;
                pending_line = line;
            } else if (det_streq(tok, "time")) {
                pending_call = 3;
                pending_line = line;
            } else if (det_streq(tok, "clock")) {
                pending_call = 4;
                pending_line = line;
            } else if (det_streq(tok, "sin")) {
                pending_call = 5;
                pending_line = line;
            } else if (det_streq(tok, "cos")) {
                pending_call = 6;
                pending_line = line;
            } else if (det_streq(tok, "sqrt")) {
                pending_call = 7;
                pending_line = line;
            } else if (det_streq(tok, "sinf")) {
                pending_call = 8;
                pending_line = line;
            } else if (det_streq(tok, "cosf")) {
                pending_call = 9;
                pending_line = line;
            } else if (det_streq(tok, "sqrtf")) {
                pending_call = 10;
                pending_line = line;
            } else if (det_streq(tok, "pow")) {
                pending_call = 11;
                pending_line = line;
            } else if (det_streq(tok, "powf")) {
                pending_call = 12;
                pending_line = line;
            }

            continue;
        }

        if (pending_call) {
            if (det_is_ws(c)) {
                continue;
            }
            if (c == '(') {
                const char *name = (pending_call == 1) ? "rand(" :
                                   (pending_call == 2) ? "srand(" :
                                   (pending_call == 3) ? "time(" :
                                   (pending_call == 4) ? "clock(" :
                                   (pending_call == 5) ? "sin(" :
                                   (pending_call == 6) ? "cos(" :
                                   (pending_call == 7) ? "sqrt(" :
                                   (pending_call == 8) ? "sinf(" :
                                   (pending_call == 9) ? "cosf(" :
                                   (pending_call == 10) ? "sqrtf(" :
                                   (pending_call == 11) ? "pow(" :
                                   "powf(";
                det_report(path, pending_line ? pending_line : line, "forbidden call:", name);
                fclose(f);
                return 1;
            }
            pending_call = 0;
            pending_line = 0u;
        }
    }

    fclose(f);
    return 0;
}

int main(void) {
    unsigned i;
    for (i = 0u; i < dg_det_scan_file_count; ++i) {
        if (det_scan_file(dg_det_scan_files[i]) != 0) {
            return 1;
        }
    }
    return 0;
}
