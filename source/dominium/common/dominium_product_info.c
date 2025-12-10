#include "dominium/product_info.h"
#include <string.h>

static const char* dmn_os_family_str(DomOSFamily fam)
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
    return "Unknown";
}

static const char* dmn_arch_str(DomArch arch)
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

DomOSFamily dominium_detect_os_family(void)
{
#if defined(_WIN32) || defined(_WIN64)
    return DOM_OSFAM_WIN_NT;
#elif defined(__APPLE__)
    return DOM_OSFAM_MAC_OS_X;
#elif defined(__ANDROID__)
    return DOM_OSFAM_ANDROID;
#elif defined(__linux__)
    return DOM_OSFAM_LINUX;
#elif defined(__EMSCRIPTEN__)
    return DOM_OSFAM_WEB;
#elif defined(__CPM__) || defined(__cpm__)
    return DOM_OSFAM_CPM;
#else
    return DOM_OSFAM_LINUX;
#endif
}

DomArch dominium_detect_arch(void)
{
#if defined(__wasm64__)
    return DOM_ARCH_WASM_64;
#elif defined(__wasm32__)
    return DOM_ARCH_WASM_32;
#elif defined(_M_X64) || defined(__x86_64__) || defined(__amd64__)
    return DOM_ARCH_X86_64;
#elif defined(_M_IX86) || defined(__i386__)
    return DOM_ARCH_X86_32;
#elif defined(__arm__) || defined(_M_ARM)
    return DOM_ARCH_ARM_32;
#elif defined(__aarch64__)
    return DOM_ARCH_ARM_64;
#elif defined(__m68k__)
    return DOM_ARCH_M68K_32;
#elif defined(__powerpc64__) || defined(__ppc64__) || defined(__PPC64__)
    return DOM_ARCH_PPC_64;
#elif defined(__powerpc__) || defined(__ppc__) || defined(__PPC__)
    return DOM_ARCH_PPC_32;
#elif defined(__Z80__)
    return DOM_ARCH_Z80_8;
#elif defined(_M_IA64)
    return DOM_ARCH_X86_64;
#else
    return DOM_ARCH_X86_64;
#endif
}

static void dmn_print_capability(const char* name, const DomVersionedCapability* cap, int trailing, FILE* out)
{
    fprintf(out, "    \"%s\": {\"current\": %u, \"min\": %u, \"max\": %u}%s\n",
            name ? name : "",
            cap ? cap->current : 0u,
            cap ? cap->min_compat : 0u,
            cap ? cap->max_compat : 0u,
            trailing ? "," : "");
}

void dominium_print_product_info_json(const DomProductInfo* info, FILE* out)
{
    if (!out) out = stdout;
    if (!info) {
        fprintf(out, "{}\n");
        return;
    }

    fprintf(out, "{\n");
    fprintf(out, "  \"product\": \"%s\",\n", info->product ? info->product : "");
    fprintf(out, "  \"role\": \"%d\",\n", (int)info->role);
    fprintf(out, "  \"role_detail\": \"%s\",\n", info->role_detail ? info->role_detail : "");
    fprintf(out, "  \"product_version\": \"%s\",\n", info->product_version ? info->product_version : "");
    fprintf(out, "  \"core_version\": \"%s\",\n", info->core_version ? info->core_version : "");
    fprintf(out, "  \"suite_version\": \"%s\",\n", info->suite_version ? info->suite_version : "");
    fprintf(out, "  \"os_family\": \"%s\",\n", dmn_os_family_str(info->os_family));
    fprintf(out, "  \"arch\": \"%s\",\n", dmn_arch_str(info->arch));
    fprintf(out, "  \"compat\": {\n");
    dmn_print_capability("core", &info->compat.core, 1, out);
    dmn_print_capability("save_format", &info->compat.save_format, 1, out);
    dmn_print_capability("pack_format", &info->compat.pack_format, 1, out);
    dmn_print_capability("replay_format", &info->compat.replay_format, 1, out);
    dmn_print_capability("net_proto", &info->compat.net_proto, 1, out);
    dmn_print_capability("launcher_game_proto", &info->compat.launcher_game_proto, 1, out);
    dmn_print_capability("tools_game_proto", &info->compat.tools_game_proto, 0, out);
    fprintf(out, "  }\n");
    fprintf(out, "}\n");
}
