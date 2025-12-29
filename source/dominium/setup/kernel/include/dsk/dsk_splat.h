#ifndef DSK_SPLAT_H
#define DSK_SPLAT_H

#include "dsk_splat_select.h"

#ifdef __cplusplus
DSK_API void dsk_splat_registry_list(std::vector<dsk_splat_candidate_t> &out);
DSK_API int dsk_splat_registry_contains(const std::string &id);
DSK_API int dsk_splat_registry_find(const std::string &id,
                                    dsk_splat_candidate_t *out_candidate);
#endif /* __cplusplus */

#endif /* DSK_SPLAT_H */
