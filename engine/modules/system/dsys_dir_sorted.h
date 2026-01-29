/*
FILE: source/domino/system/dsys_dir_sorted.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/dsys_dir_sorted
RESPONSIBILITY: Deterministic directory listing helpers (sorting + stable iteration).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**`.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Deterministic ordering via canonical name comparison.
VERSIONING / ABI / DATA FORMAT NOTES: Internal only.
EXTENSION POINTS: Replace enumeration with platform-native sorted listing if available.
*/
#ifndef DSYS_DIR_SORTED_H
#define DSYS_DIR_SORTED_H

#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

int  dsys_dir_collect_sorted(const char* path, dsys_dir_entry** out_entries, uint32_t* out_count);
bool dsys_dir_next_sorted(dsys_dir_iter* it, dsys_dir_entry* out);
void dsys_dir_free_sorted(dsys_dir_iter* it);

#ifdef __cplusplus
}
#endif

#endif /* DSYS_DIR_SORTED_H */
