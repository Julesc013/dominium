/*
FILE: source/domino/system/dsys_term.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_term
RESPONSIBILITY: Implements `dsys_term`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/system/dsys.h"

#include <stdio.h>
#include <string.h>

#ifndef _WIN32

#include <unistd.h>
#include <termios.h>
#include <sys/ioctl.h>
#include <sys/time.h>
#include <sys/select.h>

static struct termios g_dsys_term_orig;
static int g_dsys_term_active = 0;

int dsys_terminal_init(void) {
    struct termios raw;
    if (g_dsys_term_active) {
        return 1;
    }
    if (tcgetattr(STDIN_FILENO, &g_dsys_term_orig) != 0) {
        return 0;
    }
    raw = g_dsys_term_orig;
    raw.c_lflag &= ~(ICANON | ECHO);
    raw.c_cc[VMIN] = 0;
    raw.c_cc[VTIME] = 0;
    if (tcsetattr(STDIN_FILENO, TCSANOW, &raw) != 0) {
        return 0;
    }
    g_dsys_term_active = 1;
    return 1;
}

void dsys_terminal_shutdown(void) {
    if (!g_dsys_term_active) {
        return;
    }
    tcsetattr(STDIN_FILENO, TCSANOW, &g_dsys_term_orig);
    g_dsys_term_active = 0;
}

void dsys_terminal_clear(void) {
    fputs("\033[2J\033[H", stdout);
    fflush(stdout);
}

void dsys_terminal_draw_text(int row, int col, const char* text) {
    if (!text) {
        return;
    }
    printf("\033[%d;%dH%s", row + 1, col + 1, text);
    fflush(stdout);
}

void dsys_terminal_get_size(int* rows, int* cols) {
    struct winsize ws;
    if (rows) *rows = 24;
    if (cols) *cols = 80;
    if (ioctl(STDIN_FILENO, TIOCGWINSZ, &ws) == 0) {
        if (rows) *rows = (int)ws.ws_row;
        if (cols) *cols = (int)ws.ws_col;
    }
}

static int dsys_term_read_byte(void) {
    fd_set set;
    struct timeval tv;
    unsigned char ch;

    FD_ZERO(&set);
    FD_SET(STDIN_FILENO, &set);
    tv.tv_sec = 0;
    tv.tv_usec = 0;

    if (select(STDIN_FILENO + 1, &set, NULL, NULL, &tv) <= 0) {
        return -1;
    }
    if (read(STDIN_FILENO, &ch, 1) == 1) {
        return (int)ch;
    }
    return -1;
}

int dsys_terminal_poll_key(void) {
    int b0;
    b0 = dsys_term_read_byte();
    if (b0 < 0) {
        return 0;
    }
    if (b0 == 27) { /* ESC sequence */
        int b1 = dsys_term_read_byte();
        int b2 = dsys_term_read_byte();
        if (b1 == '[') {
            if (b2 == 'A') return 1001; /* up */
            if (b2 == 'B') return 1002; /* down */
            if (b2 == 'C') return 1003; /* right */
            if (b2 == 'D') return 1004; /* left */
        }
        return 0;
    }
    if (b0 == '\r' || b0 == '\n') {
        return 10;
    }
    return b0;
}

#else /* _WIN32 */

int dsys_terminal_init(void) { return 0; }
void dsys_terminal_shutdown(void) { }
void dsys_terminal_clear(void) { }
void dsys_terminal_draw_text(int row, int col, const char* text) {
    (void)row; (void)col; (void)text;
}
void dsys_terminal_get_size(int* rows, int* cols) {
    if (rows) *rows = 24;
    if (cols) *cols = 80;
}
int dsys_terminal_poll_key(void) { return 0; }

#endif
