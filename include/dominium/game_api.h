#ifndef DOMINIUM_DOM_GAME_MOD_API_H
#define DOMINIUM_DOM_GAME_MOD_API_H

/* TODO: define stable C API for game-side native/script mods. */
#include <stddef.h>
#include <stdint.h>

typedef struct DomGameModAPI {
    uint32_t abi_version;
    /* function pointers to be filled once modding layer is implemented */
} DomGameModAPI;

#endif /* DOMINIUM_DOM_GAME_MOD_API_H */
