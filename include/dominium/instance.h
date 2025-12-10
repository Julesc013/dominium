#ifndef DOMINIUM_INSTANCE_H
#define DOMINIUM_INSTANCE_H

#include <stddef.h>

typedef struct DmnInstanceAttachment_ {
    char id[64];
    char version[32];
    char source[32];
} DmnInstanceAttachment;

typedef struct DmnInstanceProducts_ {
    char runtime_build_id[128];
    char launcher_build_id[128];
    char tools_build_id[128];
} DmnInstanceProducts;

typedef struct DmnInstanceFlags_ {
    int demo_mode;
} DmnInstanceFlags;

typedef struct DmnInstance_ {
    char                 instance_id[64];
    char                 label[128];
    DmnInstanceProducts  products;
    DmnInstanceAttachment mods[16];
    size_t               mod_count;
    DmnInstanceAttachment packs[16];
    size_t               pack_count;
    char                 data_root[260];
    DmnInstanceFlags     flags;
} DmnInstance;

typedef struct DmnInstanceList_ {
    DmnInstance* instances;
    size_t       count;
} DmnInstanceList;

int dmn_instance_load(const char* instance_id, DmnInstance* out);
int dmn_instance_save(const DmnInstance* inst);
int dmn_instance_list(DmnInstanceList* out);
void dmn_instance_list_free(DmnInstanceList* list);

#endif /* DOMINIUM_INSTANCE_H */
