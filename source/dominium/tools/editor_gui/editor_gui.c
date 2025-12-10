#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdint.h>

#include "domino/sys.h"
#include "dominium/world_edit_api.h"
#include "dominium/save_edit_api.h"
#include "dominium/game_edit_api.h"
#include "dominium/launcher_edit_api.h"

typedef enum editor_mode_t {
    EDIT_MODE_WORLD = 0,
    EDIT_MODE_GAME,
    EDIT_MODE_LAUNCHER,
    EDIT_MODE_SAVE,
    EDIT_MODE_COUNT
} editor_mode;

typedef struct editor_state_t {
    editor_mode mode;
    dom_world_edit_ctx *world;
    dom_save_edit_ctx  *save;
    dom_game_edit_ctx  *game;
    dom_launcher_edit_ctx *launcher;
    char world_path[260];
    char save_path[260];
    char defs_path[260];
    char launcher_path[260];
    int running;
} editor_state;

static void log_line(const char *msg)
{
    printf("%s\n", msg);
}

static void editor_close(editor_state *st)
{
    if (!st) return;
    if (st->world) {
        dom_world_edit_save(st->world);
        dom_world_edit_close(st->world);
        st->world = NULL;
    }
    if (st->save) {
        dom_save_edit_save(st->save);
        dom_save_edit_close(st->save);
        st->save = NULL;
    }
    if (st->game) {
        dom_game_edit_save(st->game);
        dom_game_edit_close(st->game);
        st->game = NULL;
    }
    if (st->launcher) {
        dom_launcher_edit_save(st->launcher);
        dom_launcher_edit_close(st->launcher);
        st->launcher = NULL;
    }
}

static void editor_open_world(editor_state *st, const char *path)
{
    dom_world_edit_desc desc;
    editor_close(st);
    memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = 1;
    desc.world_path = path;
    st->world = dom_world_edit_open(&desc);
    if (st->world && path) {
        strncpy(st->world_path, path, sizeof(st->world_path) - 1);
    }
}

static void editor_open_save(editor_state *st, const char *path)
{
    dom_save_edit_desc desc;
    if (st->save) {
        dom_save_edit_close(st->save);
        st->save = NULL;
    }
    memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = 1;
    desc.save_path = path;
    st->save = dom_save_edit_open(&desc);
    if (st->save && path) {
        strncpy(st->save_path, path, sizeof(st->save_path) - 1);
    }
}

static void editor_open_defs(editor_state *st, const char *path)
{
    dom_game_edit_desc desc;
    if (st->game) {
        dom_game_edit_close(st->game);
        st->game = NULL;
    }
    memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = 1;
    desc.def_root = path;
    st->game = dom_game_edit_open(&desc);
    if (st->game && path) {
        strncpy(st->defs_path, path, sizeof(st->defs_path) - 1);
    }
}

static void editor_open_launcher(editor_state *st, const char *path)
{
    dom_launcher_edit_desc desc;
    if (st->launcher) {
        dom_launcher_edit_close(st->launcher);
        st->launcher = NULL;
    }
    memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = 1;
    desc.config_path = path;
    st->launcher = dom_launcher_edit_open(&desc);
    if (st->launcher && path) {
        strncpy(st->launcher_path, path, sizeof(st->launcher_path) - 1);
    }
}

static void editor_draw_stub(editor_state *st)
{
    (void)st;
    /* Placeholder for real dgfx/dom_ui rendering. */
}

static void editor_tick(editor_state *st)
{
    dsys_event ev;
    while (dsys_poll_event(&ev)) {
        if (ev.type == DSYS_EVENT_QUIT) {
            st->running = 0;
        } else if (ev.type == DSYS_EVENT_KEY_DOWN) {
            if (ev.payload.key.key == 27) { /* ESC */
                st->running = 0;
            }
        }
    }
    editor_draw_stub(st);
}

int main(int argc, char **argv)
{
    editor_state st;
    dsys_window_desc wdesc;
    dsys_window *win;
    int i;

    memset(&st, 0, sizeof(st));
    st.mode = EDIT_MODE_WORLD;
    st.running = 1;

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--world") == 0 && i + 1 < argc) {
            strncpy(st.world_path, argv[++i], sizeof(st.world_path) - 1);
        } else if (strcmp(argv[i], "--save") == 0 && i + 1 < argc) {
            strncpy(st.save_path, argv[++i], sizeof(st.save_path) - 1);
        } else if (strcmp(argv[i], "--defs") == 0 && i + 1 < argc) {
            strncpy(st.defs_path, argv[++i], sizeof(st.defs_path) - 1);
        } else if (strcmp(argv[i], "--launcher") == 0 && i + 1 < argc) {
            strncpy(st.launcher_path, argv[++i], sizeof(st.launcher_path) - 1);
        }
    }

    if (dsys_init() != DSYS_OK) {
        fprintf(stderr, "Failed to init dsys\n");
        return 1;
    }

    memset(&wdesc, 0, sizeof(wdesc));
    wdesc.width = 1280;
    wdesc.height = 720;
    wdesc.mode = DWIN_MODE_WINDOWED;
    win = dsys_window_create(&wdesc);
    if (!win) {
        fprintf(stderr, "Failed to create window\n");
        dsys_shutdown();
        return 1;
    }

    log_line("Dominium Editor GUI (stub) starting...");

    if (st.world_path[0]) editor_open_world(&st, st.world_path);
    if (st.save_path[0]) editor_open_save(&st, st.save_path);
    if (st.defs_path[0]) editor_open_defs(&st, st.defs_path);
    if (st.launcher_path[0]) editor_open_launcher(&st, st.launcher_path);

    while (st.running) {
        editor_tick(&st);
        dsys_sleep_ms(16);
    }

    editor_close(&st);
    dsys_window_destroy(win);
    dsys_shutdown();
    return 0;
}
