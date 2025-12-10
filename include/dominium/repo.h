#ifndef DOMINIUM_REPO_H
#define DOMINIUM_REPO_H

#include "domino/compat.h"
#include <stddef.h>

typedef struct DmnRepoItem_ {
    char id[64];
    char version[32];
    char source[32];
    char path[260];
} DmnRepoItem;

typedef struct DmnRepoItemList_ {
    DmnRepoItem* items;
    size_t       count;
} DmnRepoItemList;

int dmn_repo_find_product_build(const char* product,
                                const char* version,
                                const char* core_version,
                                DomOSFamily osfam,
                                DomArch arch,
                                char* out_path,
                                size_t out_path_cap);

int dmn_repo_list_mods(DmnRepoItemList* out);
int dmn_repo_resolve_mod(const char* id, const char* version, char* out_path, size_t out_path_cap);

int dmn_repo_list_packs(DmnRepoItemList* out);
int dmn_repo_resolve_pack(const char* id, const char* version, char* out_path, size_t out_path_cap);

void dmn_repo_free_item_list(DmnRepoItemList* list);

#endif /* DOMINIUM_REPO_H */
