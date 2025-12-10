#include "dominium/repo.h"
#include "dominium/paths.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static const char* dmn_os_tag(DomOSFamily fam)
{
    switch (fam) {
    case DOM_OSFAM_WIN_NT: return "WinNT";
    case DOM_OSFAM_WIN_9X: return "Win9X";
    case DOM_OSFAM_WIN_3X: return "Win3X";
    case DOM_OSFAM_DOS: return "DOS";
    case DOM_OSFAM_MAC_OS_X: return "MacOSX";
    case DOM_OSFAM_MAC_CLASSIC: return "MacClassic";
    case DOM_OSFAM_LINUX: return "Linux";
    case DOM_OSFAM_ANDROID: return "Android";
    case DOM_OSFAM_CPM: return "CPM";
    case DOM_OSFAM_WEB: return "Web";
    default: break;
    }
    return "unknown";
}

static const char* dmn_arch_tag(DomArch arch)
{
    switch (arch) {
    case DOM_ARCH_X86_16: return "x86-16";
    case DOM_ARCH_X86_32: return "x86-32";
    case DOM_ARCH_X86_64: return "x86-64";
    case DOM_ARCH_ARM_32: return "arm-32";
    case DOM_ARCH_ARM_64: return "arm-64";
    case DOM_ARCH_M68K_32: return "m68k-32";
    case DOM_ARCH_PPC_32: return "ppc-32";
    case DOM_ARCH_PPC_64: return "ppc-64";
    case DOM_ARCH_Z80_8: return "z80-8";
    case DOM_ARCH_WASM_32: return "wasm-32";
    case DOM_ARCH_WASM_64: return "wasm-64";
    default: break;
    }
    return "unknown";
}

int dmn_repo_find_product_build(const char* product,
                                const char* version,
                                const char* core_version,
                                DomOSFamily osfam,
                                DomArch arch,
                                char* out_path,
                                size_t out_path_cap)
{
    const char* home;
    const char* os_tag;
    const char* arch_tag;
    const char sep =
#if defined(_WIN32)
        '\\';
#else
        '/';
#endif
    ;

    if (!product || !version || !core_version || !out_path || out_path_cap == 0) {
        return -1;
    }
    home = dmn_get_dominium_home();
    if (!home || !home[0]) {
        return -1;
    }
    os_tag = dmn_os_tag(osfam);
    arch_tag = dmn_arch_tag(arch);

    snprintf(out_path, out_path_cap,
             "%s%crepo%cproducts%c%s%c%s%ccore-%s%c%s-%s",
             home, sep, sep, sep,
             product,
             sep, version,
             sep, core_version,
             sep, os_tag, arch_tag);
    return 0;
}

int dmn_repo_list_mods(DmnRepoItemList* out)
{
    if (out) {
        out->items = NULL;
        out->count = 0;
    }
    return 0;
}

int dmn_repo_resolve_mod(const char* id, const char* version, char* out_path, size_t out_path_cap)
{
    (void)id;
    (void)version;
    if (out_path && out_path_cap) {
        out_path[0] = '\0';
    }
    return -1;
}

int dmn_repo_list_packs(DmnRepoItemList* out)
{
    if (out) {
        out->items = NULL;
        out->count = 0;
    }
    return 0;
}

int dmn_repo_resolve_pack(const char* id, const char* version, char* out_path, size_t out_path_cap)
{
    (void)id;
    (void)version;
    if (out_path && out_path_cap) {
        out_path[0] = '\0';
    }
    return -1;
}

void dmn_repo_free_item_list(DmnRepoItemList* list)
{
    if (!list) return;
    if (list->items) {
        free(list->items);
        list->items = NULL;
    }
    list->count = 0;
}
