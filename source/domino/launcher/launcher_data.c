#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "domino/launcher_config.h"
#include "domino/launcher_profile.h"
#include "domino/launcher_mods.h"
#include "domino/launcher_process.h"
#include "domino/sys.h"

#define LAUNCHER_MAX_PROFILES 32
#define LAUNCHER_MAX_MODS     64

static launcher_profile g_profiles[LAUNCHER_MAX_PROFILES];
static int              g_profile_count = 0;
static int              g_active_profile = -1;

static launcher_mod_meta g_mods[LAUNCHER_MAX_MODS];
static int               g_mod_count = 0;

static void launcher_path_copy(char* dst, size_t cap, const char* src)
{
    size_t len;
    if (!dst || cap == 0u) {
        return;
    }
    if (!src) {
        dst[0] = '\0';
        return;
    }
    len = strlen(src);
    if (len >= cap) {
        len = cap - 1u;
    }
    memcpy(dst, src, len);
    dst[len] = '\0';
}

static int launcher_path_append(char* dst, size_t cap, const char* tail)
{
    size_t len;
    size_t i;

    if (!dst || !tail || cap == 0u) {
        return 0;
    }
    len = strlen(dst);
    if (len > 0u && dst[len - 1u] != '/' && dst[len - 1u] != '\\') {
        if (len + 1u >= cap) {
            return 0;
        }
        dst[len] = '/';
        dst[len + 1u] = '\0';
        len += 1u;
    }
    for (i = 0u; tail[i] != '\0'; ++i) {
        if (len + 1u >= cap) {
            dst[len] = '\0';
            return 0;
        }
        dst[len] = tail[i];
        len += 1u;
    }
    dst[len] = '\0';
    return 1;
}

static void launcher_path_join(char* dst, size_t cap, const char* a, const char* b)
{
    if (!dst || cap == 0u) {
        return;
    }
    dst[0] = '\0';
    if (a) {
        launcher_path_copy(dst, cap, a);
    }
    if (b) {
        (void)launcher_path_append(dst, cap, b);
    }
}

static void launcher_path_join3(char* dst, size_t cap, const char* a, const char* b, const char* c)
{
    launcher_path_join(dst, cap, a, b);
    if (c) {
        (void)launcher_path_append(dst, cap, c);
    }
}

static size_t launcher_fs_read_text(const char* path, char* buf, size_t cap)
{
    void*  fh;
    size_t total;
    size_t read_count;

    if (!path || !buf || cap == 0u) {
        return 0u;
    }
    fh = dsys_file_open(path, "rb");
    if (!fh) {
        return 0u;
    }
    total = 0u;
    while (total + 1u < cap) {
        read_count = dsys_file_read(fh, buf + total, cap - total - 1u);
        if (read_count == 0u) {
            break;
        }
        total += read_count;
    }
    buf[total] = '\0';
    dsys_file_close(fh);
    return total;
}

static int launcher_fs_write_text(const char* path, const char* text)
{
    void*  fh;
    size_t len;
    size_t written;

    if (!path || !text) {
        return -1;
    }
    fh = dsys_file_open(path, "wb");
    if (!fh) {
        return -1;
    }
    len = strlen(text);
    written = dsys_file_write(fh, text, len);
    dsys_file_close(fh);
    if (written != len) {
        return -1;
    }
    return 0;
}

static void launcher_config_defaults(launcher_config* cfg)
{
    if (!cfg) {
        return;
    }
    memset(cfg, 0, sizeof(*cfg));
    cfg->width = 960;
    cfg->height = 540;
    cfg->soft_only = 1;
    launcher_path_copy(cfg->theme, sizeof(cfg->theme), "default");
    if (!dsys_get_path(DSYS_PATH_USER_CONFIG, cfg->pref_path, sizeof(cfg->pref_path))) {
        launcher_path_copy(cfg->pref_path, sizeof(cfg->pref_path), ".");
    }
}

int launcher_config_load(launcher_config* cfg)
{
    char   path[260];
    char   buf[1024];
    size_t len;
    char*  line;

    launcher_config_defaults(cfg);
    if (!cfg) {
        return -1;
    }

    launcher_path_join(path, sizeof(path), cfg->pref_path, "launcher.cfg");
    len = launcher_fs_read_text(path, buf, sizeof(buf));
    if (len == 0u) {
        return -1;
    }

    line = strtok(buf, "\n\r");
    while (line) {
        if (line[0] == '#' || line[0] == ';') {
            line = strtok(NULL, "\n\r");
            continue;
        }
        if (strncmp(line, "width=", 6) == 0) {
            cfg->width = atoi(line + 6);
        } else if (strncmp(line, "height=", 7) == 0) {
            cfg->height = atoi(line + 7);
        } else if (strncmp(line, "soft_only=", 10) == 0) {
            cfg->soft_only = atoi(line + 10);
        } else if (strncmp(line, "theme=", 6) == 0) {
            launcher_path_copy(cfg->theme, sizeof(cfg->theme), line + 6);
        } else if (strncmp(line, "pref_path=", 10) == 0) {
            launcher_path_copy(cfg->pref_path, sizeof(cfg->pref_path), line + 10);
        }
        line = strtok(NULL, "\n\r");
    }
    return 0;
}

int launcher_config_save(const launcher_config* cfg)
{
    char path[260];
    char text[256];
    int  n;

    if (!cfg) {
        return -1;
    }
    launcher_path_join(path, sizeof(path), cfg->pref_path, "launcher.cfg");
    n = sprintf(text,
                "width=%d\nheight=%d\nsoft_only=%d\ntheme=%s\npref_path=%s\n",
                cfg->width,
                cfg->height,
                cfg->soft_only,
                cfg->theme,
                cfg->pref_path);
    if (n <= 0) {
        return -1;
    }
    text[sizeof(text) - 1u] = '\0';
    return launcher_fs_write_text(path, text);
}

static int launcher_profile_parse(const char* path, launcher_profile* out)
{
    char   buf[1024];
    char*  line;
    size_t len;

    if (!path || !out) {
        return 0;
    }
    memset(out, 0, sizeof(*out));
    len = launcher_fs_read_text(path, buf, sizeof(buf));
    if (len == 0u) {
        return 0;
    }
    line = strtok(buf, "\n\r");
    while (line) {
        if (line[0] == '#' || line[0] == ';') {
            line = strtok(NULL, "\n\r");
            continue;
        }
        if (strncmp(line, "id=", 3) == 0) {
            launcher_path_copy(out->id, sizeof(out->id), line + 3);
        } else if (strncmp(line, "name=", 5) == 0) {
            launcher_path_copy(out->name, sizeof(out->name), line + 5);
        } else if (strncmp(line, "install_path=", 13) == 0) {
            launcher_path_copy(out->install_path, sizeof(out->install_path), line + 13);
        } else if (strncmp(line, "modset=", 7) == 0) {
            launcher_path_copy(out->modset, sizeof(out->modset), line + 7);
        }
        line = strtok(NULL, "\n\r");
    }
    return 1;
}

int launcher_profile_load_all(void)
{
    char          root[260];
    char          path[260];
    dsys_dir_iter* it;
    dsys_dir_entry ent;

    g_profile_count = 0;
    g_active_profile = -1;

    if (!dsys_get_path(DSYS_PATH_USER_DATA, root, sizeof(root))) {
        launcher_path_copy(root, sizeof(root), ".");
    }
    launcher_path_append(root, sizeof(root), "profiles");

    it = dsys_dir_open(root);
    if (!it) {
        return 0;
    }

    while (dsys_dir_next(it, &ent)) {
        if (ent.is_dir) {
            continue;
        }
        if (ent.name[0] == '.' || g_profile_count >= LAUNCHER_MAX_PROFILES) {
            continue;
        }
        launcher_path_join(path, sizeof(path), root, ent.name);
        if (launcher_profile_parse(path, &g_profiles[g_profile_count])) {
            if (g_profiles[g_profile_count].id[0] == '\0') {
                launcher_path_copy(g_profiles[g_profile_count].id, sizeof(g_profiles[g_profile_count].id), ent.name);
            }
            if (g_profiles[g_profile_count].name[0] == '\0') {
                launcher_path_copy(g_profiles[g_profile_count].name, sizeof(g_profiles[g_profile_count].name), ent.name);
            }
            g_profile_count += 1;
        }
    }
    dsys_dir_close(it);

    if (g_profile_count > 0) {
        g_active_profile = 0;
    }
    return g_profile_count;
}

const launcher_profile* launcher_profile_get(int index)
{
    if (index < 0 || index >= g_profile_count) {
        return NULL;
    }
    return &g_profiles[index];
}

int launcher_profile_count(void)
{
    return g_profile_count;
}

int launcher_profile_set_active(int index)
{
    if (index < 0 || index >= g_profile_count) {
        return -1;
    }
    g_active_profile = index;
    return 0;
}

int launcher_profile_get_active(void)
{
    return g_active_profile;
}

int launcher_profile_save(const launcher_profile* p)
{
    char root[260];
    char path[260];
    char text[512];
    char filename[128];
    int  n;

    if (!p || p->id[0] == '\0') {
        return -1;
    }

    if (!dsys_get_path(DSYS_PATH_USER_DATA, root, sizeof(root))) {
        launcher_path_copy(root, sizeof(root), ".");
    }
    launcher_path_append(root, sizeof(root), "profiles");
    launcher_path_copy(filename, sizeof(filename), p->id);
    n = (int)strlen(filename);
    if (n + 9 < (int)sizeof(filename)) {
        strcat(filename, ".profile");
    }
    launcher_path_join(path, sizeof(path), root, filename);

    n = sprintf(text,
                "id=%s\nname=%s\ninstall_path=%s\nmodset=%s\n",
                p->id,
                p->name,
                p->install_path,
                p->modset);
    if (n <= 0) {
        return -1;
    }
    text[sizeof(text) - 1u] = '\0';
    return launcher_fs_write_text(path, text);
}

int launcher_mods_scan(const char* path)
{
    char           root[260];
    dsys_dir_iter* it;
    dsys_dir_entry ent;
    char           full[260];

    g_mod_count = 0;

    if (path && path[0] != '\0') {
        launcher_path_copy(root, sizeof(root), path);
    } else {
        if (!dsys_get_path(DSYS_PATH_USER_DATA, root, sizeof(root))) {
            launcher_path_copy(root, sizeof(root), ".");
        }
        launcher_path_append(root, sizeof(root), "mods");
    }

    it = dsys_dir_open(root);
    if (!it) {
        return 0;
    }

    while (dsys_dir_next(it, &ent)) {
        size_t name_len;
        const char* ext;
        if (ent.is_dir || g_mod_count >= LAUNCHER_MAX_MODS) {
            continue;
        }
        name_len = strlen(ent.name);
        if (name_len == 0u || ent.name[0] == '.') {
            continue;
        }
        ext = strrchr(ent.name, '.');
        if (!ext || (strcmp(ext, ".json") != 0 && strcmp(ext, ".mod") != 0 && strcmp(ext, ".ini") != 0)) {
            continue;
        }
        launcher_path_join(full, sizeof(full), root, ent.name);
        memset(&g_mods[g_mod_count], 0, sizeof(g_mods[g_mod_count]));
        launcher_path_copy(g_mods[g_mod_count].id, sizeof(g_mods[g_mod_count].id), ent.name);
        launcher_path_copy(g_mods[g_mod_count].name, sizeof(g_mods[g_mod_count].name), ent.name);
        launcher_path_copy(g_mods[g_mod_count].version, sizeof(g_mods[g_mod_count].version), "0.0.0");
        g_mods[g_mod_count].priority = g_mod_count;
        g_mods[g_mod_count].enabled = 1;
        g_mod_count += 1;
        (void)full;
    }

    dsys_dir_close(it);
    return g_mod_count;
}

int launcher_mods_get(int index, launcher_mod_meta* out)
{
    if (!out || index < 0 || index >= g_mod_count) {
        return -1;
    }
    *out = g_mods[index];
    return 0;
}

int launcher_mods_count(void)
{
    return g_mod_count;
}

int launcher_mods_set_enabled(const char* id, int enabled)
{
    int i;
    for (i = 0; i < g_mod_count; ++i) {
        if (strcmp(g_mods[i].id, id) == 0) {
            g_mods[i].enabled = enabled ? 1 : 0;
            return 0;
        }
    }
    return -1;
}

int launcher_mods_resolve_order(void)
{
    int i;
    int swapped;
    if (g_mod_count <= 1) {
        return 0;
    }
    do {
        swapped = 0;
        for (i = 0; i < g_mod_count - 1; ++i) {
            if (g_mods[i].priority > g_mods[i + 1].priority) {
                launcher_mod_meta tmp;
                tmp = g_mods[i];
                g_mods[i] = g_mods[i + 1];
                g_mods[i + 1] = tmp;
                swapped = 1;
            }
        }
    } while (swapped);
    return 0;
}

int launcher_process_spawn(launcher_proc* p, const char* exe, const char* args, const char* cwd)
{
    dsys_process_desc desc;
    const char* argv_local[3];

    if (!p || !exe) {
        return -1;
    }
    memset(&desc, 0, sizeof(desc));
    memset(argv_local, 0, sizeof(argv_local));
    argv_local[0] = exe;
    if (args && args[0] != '\0') {
        argv_local[1] = args;
    }
    desc.exe = exe;
    desc.argv = argv_local;
    desc.flags = 0u;
    p->handle = dsys_process_spawn(&desc);
    if (!p->handle) {
        p->running = 0;
        p->pid = -1;
        return -1;
    }
    launcher_path_copy(p->cmdline, sizeof(p->cmdline), exe);
    if (args && args[0] != '\0') {
        size_t clen;
        size_t alen;
        clen = strlen(p->cmdline);
        alen = strlen(args);
        if (clen + 1u + alen < sizeof(p->cmdline)) {
            p->cmdline[clen] = ' ';
            memcpy(p->cmdline + clen + 1u, args, alen);
            p->cmdline[clen + 1u + alen] = '\0';
        }
    }
    if (cwd) {
        launcher_path_copy(p->cwd, sizeof(p->cwd), cwd);
    } else {
        p->cwd[0] = '\0';
    }
    p->running = 1;
    p->exit_code = 0;
    p->pid = 0;
    return 0;
}

int launcher_process_poll(launcher_proc* p)
{
    int res;
    if (!p || !p->handle) {
        return -1;
    }
    if (!p->running) {
        return p->exit_code;
    }
    res = dsys_process_wait(p->handle);
    if (res >= 0) {
        p->running = 0;
        p->exit_code = res;
    }
    return p->running ? -1 : p->exit_code;
}

int launcher_process_kill(launcher_proc* p)
{
    if (!p) {
        return -1;
    }
    if (p->handle) {
        dsys_process_destroy(p->handle);
        p->handle = NULL;
    }
    p->running = 0;
    return 0;
}

int launcher_process_read_stdout(launcher_proc* p, char* buf, int maxlen)
{
    (void)p;
    (void)buf;
    (void)maxlen;
    return 0;
}
