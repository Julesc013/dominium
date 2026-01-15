/*
FILE: source/dominium/launcher/tui/launch_tui.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/tui/launch_tui
RESPONSIBILITY: Implements `launch_tui`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <curses.h>

#include "domino/core.h"
#include "domino/sys.h"
#include "domino/view.h"
#include "domino/model_table.h"
#include "domino/pkg.h"
#include "domino/sim.h"
#include "dominium/launch_api.h"

static void trim_trailing(char* s)
{
    size_t len;
    if (!s) return;
    len = strlen(s);
    while (len > 0u && (s[len - 1u] == ' ' || s[len - 1u] == '\t' ||
                        s[len - 1u] == '\r' || s[len - 1u] == '\n')) {
        s[len - 1u] = '\0';
        len -= 1u;
    }
}

static dom_instance_id instance_id_from_row(dom_core* core, uint32_t row)
{
    char buf[64];
    if (!dom_table_get_cell(core, "instances_table", row, 0u, buf, sizeof(buf))) {
        return 0u;
    }
    return (dom_instance_id)strtoul(buf, NULL, 10);
}

static void clear_region(int x, int y, int w, int h)
{
    int r, c;
    for (r = 0; r < h; ++r) {
        move(y + r, x);
        for (c = 0; c < w; ++c) {
            addch(' ');
        }
    }
}

static void draw_instances(dom_core* core, int x, int y, int w, int h,
                           uint32_t selected_row, uint32_t scroll)
{
    dom_table_meta meta;
    uint32_t row;
    uint32_t visible;
    int line;
    const int col_id_w = 5;
    const int col_name_w = 18;
    int col_path_w;
    char cell[256];

    clear_region(x, y, w, h);
    move(y, x);
    attron(A_BOLD);
    printw("Instances");
    attroff(A_BOLD);

    if (!dom_table_get_meta(core, "instances_table", &meta)) {
        move(y + 1, x);
        printw("(no data)");
        return;
    }

    col_path_w = w - col_id_w - col_name_w - 4;
    if (col_path_w < 8) {
        col_path_w = 8;
    }

    move(y + 1, x);
    printw("%-*s %-*s %-*s %s",
           col_id_w, "ID",
           col_name_w, "Name",
           col_path_w, "Path",
           "Flags");

    visible = (h > 2) ? (uint32_t)(h - 2) : 0u;
    if (visible == 0u) {
        return;
    }

    line = 0;
    for (row = scroll; row < meta.row_count && line < (int)visible; ++row, ++line) {
        int is_sel = (row == selected_row);
        char name_buf[128];
        char path_buf[256];
        char flags_buf[64];

        if (!dom_table_get_cell(core, "instances_table", row, 1u, name_buf, sizeof(name_buf))) {
            strcpy(name_buf, "-");
        }
        if (!dom_table_get_cell(core, "instances_table", row, 2u, path_buf, sizeof(path_buf))) {
            strcpy(path_buf, "-");
        }
        if (!dom_table_get_cell(core, "instances_table", row, 3u, flags_buf, sizeof(flags_buf))) {
            strcpy(flags_buf, "0");
        }
        if (!dom_table_get_cell(core, "instances_table", row, 0u, cell, sizeof(cell))) {
            strcpy(cell, "?");
        }

        if (is_sel) attron(A_REVERSE);
        move(y + 2 + line, x);
        printw("%-*s %-*.*s %-*.*s %s",
               col_id_w, cell,
               col_name_w, col_name_w, name_buf,
               col_path_w, col_path_w, path_buf,
               flags_buf);
        if (is_sel) attroff(A_REVERSE);
    }
}

static void draw_detail(dom_core* core, int x, int y, int w, int h, dom_instance_id inst_id)
{
    dom_query               q;
    dom_query_inst_info_in  in_inst;
    dom_query_inst_info_out out_inst;
    dom_sim_state           sim;
    uint32_t                i;
    int                     line = 0;

    clear_region(x, y, w, h);
    move(y, x);
    attron(A_BOLD);
    printw("Details");
    attroff(A_BOLD);

    if (inst_id == 0u) {
        move(y + 1, x);
        printw("No instance selected.");
        return;
    }

    memset(&in_inst, 0, sizeof(in_inst));
    memset(&out_inst, 0, sizeof(out_inst));
    in_inst.id = inst_id;
    memset(&q, 0, sizeof(q));
    q.id = DOM_QUERY_INST_INFO;
    q.in = &in_inst;
    q.in_size = sizeof(in_inst);
    q.out = &out_inst;
    q.out_size = sizeof(out_inst);

    if (!dom_core_query(core, &q) || out_inst.info.struct_size == 0u) {
        move(y + 1, x);
        printw("Instance %u not found", (unsigned int)inst_id);
        return;
    }

    line = 1;
    move(y + line++, x);
    printw("ID: %u", (unsigned int)out_inst.info.id);
    move(y + line++, x);
    printw("Name: %s", out_inst.info.name);
    move(y + line++, x);
    printw("Path: %s", out_inst.info.path);
    move(y + line++, x);
    printw("Flags: %u", (unsigned int)out_inst.info.flags);

    memset(&sim, 0, sizeof(sim));
    sim.struct_size = sizeof(sim);
    sim.struct_version = 1;
    if (dom_sim_get_state(core, inst_id, &sim)) {
        move(y + line++, x);
        printw("Sim: ticks=%llu paused=%d", (unsigned long long)sim.ticks, sim.paused ? 1 : 0);
    }

    move(y + line++, x);
    printw("Packages:");
    for (i = 0u; i < out_inst.info.pkg_count && (y + line) < (y + h); ++i) {
        dom_package_info pkg;
        memset(&pkg, 0, sizeof(pkg));
        if (dom_pkg_get(core, out_inst.info.pkgs[i], &pkg)) {
            move(y + line, x + 2);
            printw("%u: %s (%s)", (unsigned int)pkg.id, pkg.name, pkg.version);
        } else {
            move(y + line, x + 2);
            printw("%u: [missing]", (unsigned int)out_inst.info.pkgs[i]);
        }
        line += 1;
    }
}

static void draw_status(int w, int h, const char* status)
{
    move(h - 1, 0);
    clrtoeol();
    attron(A_REVERSE);
    printw("F2:New  F3:Delete  F5:Launch  Up/Down:Move  PgUp/PgDn:Scroll  ESC/q:Quit");
    attroff(A_REVERSE);
    if (status && status[0] != '\0') {
        int slen = (int)strlen(status);
        if (slen + 2 < w) {
            move(h - 1, w - slen - 1);
            printw("%s", status);
        }
    }
}

static void update_selection(dom_launch_ctx* ctx, dom_core* core, uint32_t selected_row)
{
    dom_instance_id inst_id = instance_id_from_row(core, selected_row);
    if (inst_id != 0u) {
        dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_EDIT_INSTANCE, inst_id, NULL);
    }
}

int main(int argc, char** argv)
{
    dsys_result     dres;
    dom_core_desc   core_desc;
    dom_core*       core;
    dom_launch_desc ldesc;
    dom_launch_ctx* ctx;
    dom_table_meta  meta;
    uint32_t        selected;
    uint32_t        scroll;
    int             running;
    char            status[128];
    dom_instance_id last_inst_id;

    (void)argc;
    (void)argv;

    dres = dsys_init();
    if (dres != DSYS_OK) {
        fprintf(stderr, "dsys_init failed (%d)\n", (int)dres);
        return 1;
    }

    memset(&core_desc, 0, sizeof(core_desc));
    core_desc.api_version = 1;
    core = dom_core_create(&core_desc);
    if (!core) {
        fprintf(stderr, "Failed to create dom_core\n");
        dsys_shutdown();
        return 1;
    }

    memset(&ldesc, 0, sizeof(ldesc));
    ldesc.struct_size = sizeof(ldesc);
    ldesc.struct_version = 1;
    ldesc.core = core;
    ldesc.ui_mode = DOM_UI_MODE_TUI;
    ldesc.product_id = "dominium";
    ldesc.version = "0.0.0";
    ctx = dom_launch_create(&ldesc);
    if (!ctx) {
        fprintf(stderr, "Failed to create launcher context\n");
        dom_core_destroy(core);
        dsys_shutdown();
        return 1;
    }

    initscr();
    cbreak();
    noecho();
    keypad(stdscr, TRUE);
    curs_set(0);

    memset(status, 0, sizeof(status));
    strcpy(status, "Ready");
    selected = 0u;
    scroll = 0u;
    last_inst_id = 0u;
    dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_LIST_INSTANCES, 0u, NULL);

    running = 1;
    while (running) {
        int width, height;
        int ch;
        uint32_t visible;
        dom_instance_id current_inst;

        if (!dom_table_get_meta(core, "instances_table", &meta)) {
            memset(&meta, 0, sizeof(meta));
        }

        if (meta.row_count == 0u) {
            selected = 0u;
            scroll = 0u;
        } else {
            if (selected >= meta.row_count) {
                selected = meta.row_count - 1u;
            }
        }

        getmaxyx(stdscr, height, width);

        {
            int inst_w = (width * 60) / 100;
            int detail_w = width - inst_w;
            int top_h = (height > 1) ? (height - 1) : height;
            dom_instance_id current_inst_id;

            if ((int)selected < (int)scroll) {
                scroll = selected;
            }
            visible = (top_h > 2) ? (uint32_t)(top_h - 2) : 0u;
            if (visible > 0u && selected >= scroll + visible) {
                scroll = selected - visible + 1u;
            }

            draw_instances(core, 0, 0, inst_w, top_h, selected, scroll);
            current_inst_id = (meta.row_count > 0u) ? instance_id_from_row(core, selected) : 0u;
            if (current_inst_id != last_inst_id) {
                if (current_inst_id != 0u) {
                    dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_EDIT_INSTANCE, current_inst_id, NULL);
                }
                last_inst_id = current_inst_id;
            }
            draw_detail(core, inst_w, 0, detail_w, top_h, current_inst_id);
            draw_status(width, height, status);
        }

        refresh();
        ch = getch();
        switch (ch) {
        case KEY_UP:
            if (selected > 0u) {
                selected -= 1u;
                update_selection(ctx, core, selected);
                last_inst_id = instance_id_from_row(core, selected);
            }
            break;
        case KEY_DOWN:
            if (selected + 1u < meta.row_count) {
                selected += 1u;
                update_selection(ctx, core, selected);
                last_inst_id = instance_id_from_row(core, selected);
            }
            break;
        case KEY_PPAGE:
            if (selected > 0u) {
                if (selected > 10u) selected -= 10u; else selected = 0u;
                update_selection(ctx, core, selected);
                last_inst_id = instance_id_from_row(core, selected);
            }
            break;
        case KEY_NPAGE:
            if (meta.row_count > 0u && selected + 1u < meta.row_count) {
                if (selected + 10u < meta.row_count) selected += 10u;
                else selected = meta.row_count - 1u;
                update_selection(ctx, core, selected);
                last_inst_id = instance_id_from_row(core, selected);
            }
            break;
        case KEY_F(2): {
            dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_CREATE_INSTANCE, 0u, "New Instance");
            dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_LIST_INSTANCES, 0u, NULL);
            if (dom_table_get_meta(core, "instances_table", &meta) && meta.row_count > 0u) {
                selected = meta.row_count - 1u;
                update_selection(ctx, core, selected);
            }
            last_inst_id = 0u;
            strcpy(status, "Created instance");
            break;
        }
        case KEY_F(3): {
            dom_instance_id inst = instance_id_from_row(core, selected);
            if (inst != 0u) {
                strcpy(status, "Delete? (y/N)");
                draw_status(width, height, status);
                refresh();
                ch = getch();
                if (ch == 'y' || ch == 'Y') {
                    dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_DELETE_INSTANCE, inst, NULL);
                    dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_LIST_INSTANCES, 0u, NULL);
                    if (dom_table_get_meta(core, "instances_table", &meta) && meta.row_count > 0u) {
                        if (selected >= meta.row_count) {
                            selected = meta.row_count - 1u;
                        }
                        last_inst_id = instance_id_from_row(core, selected);
                    } else {
                        selected = 0u;
                        last_inst_id = 0u;
                    }
                    strcpy(status, "Deleted");
                } else {
                    strcpy(status, "Cancelled");
                }
            }
            break;
        }
        case KEY_F(5): {
            dom_instance_id inst = instance_id_from_row(core, selected);
            if (inst != 0u) {
                dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_LAUNCH_INSTANCE, inst, NULL);
                strcpy(status, "Launching...");
            }
            break;
        }
        case 27: /* ESC */
        case 'q':
        case 'Q':
            running = 0;
            break;
        default:
            break;
        }
    }

    endwin();
    dom_launch_destroy(ctx);
    dom_core_destroy(core);
    dsys_shutdown();
    return 0;
}
