#include <string.h>
#include <stdio.h>
#include "dgfx_demo.h"
#include "domino/gfx.h"

static dgfx_backend_t parse_backend(const char *name)
{
    if (!name) return DGFX_BACKEND_SOFT;
    if (strcmp(name, "soft") == 0) return DGFX_BACKEND_SOFT;
    if (strcmp(name, "dx7") == 0) return DGFX_BACKEND_DX7;
    if (strcmp(name, "dx9") == 0) return DGFX_BACKEND_DX9;
    if (strcmp(name, "dx11") == 0) return DGFX_BACKEND_DX11;
    if (strcmp(name, "vk1") == 0) return DGFX_BACKEND_VK1;
    if (strcmp(name, "gl1") == 0) return DGFX_BACKEND_GL1;
    if (strcmp(name, "gl2") == 0) return DGFX_BACKEND_GL2;
    if (strcmp(name, "quickdraw") == 0) return DGFX_BACKEND_QUICKDRAW;
    if (strcmp(name, "quartz") == 0) return DGFX_BACKEND_QUARTZ;
    if (strcmp(name, "metal") == 0) return DGFX_BACKEND_METAL;
    if (strcmp(name, "gdi") == 0) return DGFX_BACKEND_GDI;
    if (strcmp(name, "vesa") == 0) return DGFX_BACKEND_VESA;
    if (strcmp(name, "vga") == 0) return DGFX_BACKEND_VGA;
    if (strcmp(name, "cga") == 0) return DGFX_BACKEND_CGA;
    if (strcmp(name, "ega") == 0) return DGFX_BACKEND_EGA;
    if (strcmp(name, "xga") == 0) return DGFX_BACKEND_XGA;
    if (strcmp(name, "herc") == 0) return DGFX_BACKEND_HERC;
    if (strcmp(name, "mda") == 0) return DGFX_BACKEND_MDA;
    if (strcmp(name, "x11") == 0) return DGFX_BACKEND_X11;
    if (strcmp(name, "cocoa") == 0) return DGFX_BACKEND_COCOA;
    if (strcmp(name, "sdl1") == 0) return DGFX_BACKEND_SDL1;
    if (strcmp(name, "sdl2") == 0) return DGFX_BACKEND_SDL2;
    if (strcmp(name, "wayland") == 0) return DGFX_BACKEND_WAYLAND;
    if (strcmp(name, "null") == 0) return DGFX_BACKEND_NULL;
    return DGFX_BACKEND_SOFT;
}

int main(int argc, char **argv)
{
    dgfx_backend_t backend;
    const char *name;

    name = (argc > 1) ? argv[1] : "soft";
    backend = parse_backend(name);

    printf("dgfx demo running on backend: %s\n", name);
    return dgfx_run_demo(backend);
}
