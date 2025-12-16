/*
FILE: source/dominium/setup/os/dos/setup_dos_tui.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/os/dos/setup_dos_tui
RESPONSIBILITY: Implements `setup_dos_tui`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#if defined(_MSC_VER) || defined(__WATCOMC__) || defined(__BORLANDC__) || defined(__TURBOC__)
#include <direct.h>
#define MKDIR(path) _mkdir(path)
#else
#include <sys/stat.h>
#define MKDIR(path) mkdir(path, 0777)
#endif

#define PATH_MAX_LEN 260

static void trim_newline(char* s)
{
    size_t len;
    if (!s) {
        return;
    }
    len = strlen(s);
    while (len > 0 && (s[len - 1] == '\n' || s[len - 1] == '\r')) {
        s[len - 1] = '\0';
        --len;
    }
}

static void wait_for_key(void)
{
    printf("\nPress ENTER to continue...");
    fflush(stdout);
    (void)getchar();
}

static void normalize_path(char* path)
{
    size_t len;
    if (!path) {
        return;
    }
    len = strlen(path);
    while (len > 0 && (path[len - 1] == '\\' || path[len - 1] == '/')) {
        path[len - 1] = '\0';
        --len;
    }
}

static void join_path(char* out, size_t cap, const char* base, const char* name)
{
    size_t blen;
    if (!out || cap == 0) {
        return;
    }
    out[0] = '\0';
    if (!base) {
        base = "";
    }
    blen = strlen(base);
    strncpy(out, base, cap - 1);
    out[cap - 1] = '\0';
    if (blen > 0 && out[blen - 1] != '\\' && out[blen - 1] != '/') {
        strncat(out, "\\", cap - strlen(out) - 1);
    }
    if (name) {
        strncat(out, name, cap - strlen(out) - 1);
    }
}

static int copy_file(const char* src, const char* dst)
{
    FILE* in;
    FILE* out;
    char buf[1024];
    size_t n;

    in = fopen(src, "rb");
    if (!in) {
        return 0;
    }
    out = fopen(dst, "wb");
    if (!out) {
        fclose(in);
        return 0;
    }

    while ((n = fread(buf, 1, sizeof(buf), in)) > 0) {
        if (fwrite(buf, 1, n, out) != n) {
            fclose(in);
            fclose(out);
            return 0;
        }
    }

    fclose(in);
    fclose(out);
    return 1;
}

static void ensure_dir(const char* path)
{
    if (path && path[0] != '\0') {
        MKDIR(path);
    }
}

static void write_launcher_bat(const char* target_root)
{
    char bat_path[PATH_MAX_LEN];
    FILE* f;

    if (!target_root) {
        return;
    }

    join_path(bat_path, sizeof(bat_path), target_root, "DOMINIUM.BAT");
    f = fopen(bat_path, "w");
    if (!f) {
        return;
    }

    fprintf(f, "@echo off\r\n");
    fprintf(f, "cd %s\\bin\r\n", target_root);
    fprintf(f, "dominium.exe %%1 %%2 %%3 %%4 %%5 %%6 %%7 %%8 %%9\r\n");
    fclose(f);
}

static void copy_payload(const char* target_root)
{
    char bin_dir[PATH_MAX_LEN];
    char data_dir[PATH_MAX_LEN];
    char dst[PATH_MAX_LEN];
    size_t i;

    const char* bin_files[] = {
        "dominium.exe",
        "dominium.com",
        "dominium-setup-cli.exe",
        NULL
    };

    const char* data_files[] = {
        "data\\readme.txt",
        NULL
    };

    if (!target_root) {
        return;
    }

    join_path(bin_dir, sizeof(bin_dir), target_root, "bin");
    join_path(data_dir, sizeof(data_dir), target_root, "data");
    ensure_dir(target_root);
    ensure_dir(bin_dir);
    ensure_dir(data_dir);

    for (i = 0; bin_files[i]; ++i) {
        join_path(dst, sizeof(dst), bin_dir, bin_files[i]);
        if (copy_file(bin_files[i], dst)) {
            printf("Copied %s -> %s\n", bin_files[i], dst);
        } else {
            printf("Skipped missing file: %s\n", bin_files[i]);
        }
    }

    for (i = 0; data_files[i]; ++i) {
        const char* name = data_files[i];
        if (strncmp(name, "data\\", 5) == 0 || strncmp(name, "data/", 5) == 0) {
            name += 5;
        }
        join_path(dst, sizeof(dst), data_dir, name);
        if (copy_file(data_files[i], dst)) {
            printf("Copied %s -> %s\n", data_files[i], dst);
        } else {
            printf("Skipped missing data file: %s\n", data_files[i]);
        }
    }

    write_launcher_bat(target_root);
}

static void perform_install(const char* target_root)
{
    printf("\nInstalling to: %s\n", target_root);
    copy_payload(target_root);
    printf("Install complete.\n");
}

static void perform_uninstall(const char* target_root)
{
    char bat_path[PATH_MAX_LEN];
    (void)remove(target_root); /* No recursive removal; keep user data. */
    join_path(bat_path, sizeof(bat_path), target_root, "DOMINIUM.BAT");
    remove(bat_path);
    printf("Uninstall cleanup done (files may remain in %s).\n", target_root);
}

static void prompt_target(char* out, size_t cap)
{
    if (!out || cap == 0) {
        return;
    }
    printf("Enter install directory [C:\\DOMINIUM]: ");
    fflush(stdout);
    if (!fgets(out, (int)cap, stdin)) {
        out[0] = '\0';
        return;
    }
    trim_newline(out);
    if (out[0] == '\0') {
        strncpy(out, "C:\\DOMINIUM", cap - 1);
        out[cap - 1] = '\0';
    }
    normalize_path(out);
}

int main(void)
{
    char choice[8];
    char target[PATH_MAX_LEN];
    int running = 1;

    printf("Dominium DOS Installer\n");
    printf("======================\n");

    while (running) {
        printf("\nSelect an option:\n");
        printf("  1) Install\n");
        printf("  2) Repair\n");
        printf("  3) Uninstall\n");
        printf("  q) Quit\n");
        printf("Choice: ");
        fflush(stdout);

        if (!fgets(choice, sizeof(choice), stdin)) {
            break;
        }
        switch (choice[0]) {
        case '1':
            prompt_target(target, sizeof(target));
            perform_install(target);
            wait_for_key();
            break;
        case '2':
            prompt_target(target, sizeof(target));
            perform_install(target);
            printf("Repair completed.\n");
            wait_for_key();
            break;
        case '3':
            prompt_target(target, sizeof(target));
            perform_uninstall(target);
            wait_for_key();
            break;
        case 'q':
        case 'Q':
            running = 0;
            break;
        default:
            printf("Unknown choice.\n");
            break;
        }
    }

    printf("Exiting Dominium DOS installer.\n");
    return 0;
}
