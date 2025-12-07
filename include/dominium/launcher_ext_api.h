#ifndef DOMINIUM_LAUNCHER_EXT_API_H
#define DOMINIUM_LAUNCHER_EXT_API_H

#include "domino/mod.h"

struct dominium_launcher_context;

/* Query instances */
int launcher_ext_list_instances(struct dominium_launcher_context* ctx,
                                domino_instance_desc* out,
                                unsigned int max_count,
                                unsigned int* out_count);

/* Launch an instance */
int launcher_ext_run_instance(struct dominium_launcher_context* ctx,
                              const char* instance_id);

/* Query launcher-target packages */
int launcher_ext_list_launcher_packages(struct dominium_launcher_context* ctx,
                                        domino_package_desc* out,
                                        unsigned int max_count,
                                        unsigned int* out_count);

#endif /* DOMINIUM_LAUNCHER_EXT_API_H */
