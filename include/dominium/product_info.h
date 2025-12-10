#ifndef DOMINIUM_PRODUCT_INFO_H
#define DOMINIUM_PRODUCT_INFO_H

#include "domino/compat.h"
#include <stdio.h>

#define DMN_EMPTY_COMPAT_PROFILE \
    { {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0}, {0, 0, 0} }

#ifdef __cplusplus
extern "C" {
#endif

const DomProductInfo* dom_get_product_info_game(void);
const DomProductInfo* dom_get_product_info_launcher(void);
const DomProductInfo* dom_get_product_info_setup(void);
const DomProductInfo* dom_get_product_info_tools(void);

DomOSFamily dominium_detect_os_family(void);
DomArch dominium_detect_arch(void);

void dominium_print_product_info_json(const DomProductInfo* info, FILE* out);

#ifdef __cplusplus
}
#endif

#endif /* DOMINIUM_PRODUCT_INFO_H */
