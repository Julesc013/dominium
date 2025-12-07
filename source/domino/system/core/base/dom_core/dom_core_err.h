#ifndef DOM_CORE_ERR_H
#define DOM_CORE_ERR_H

#include "dom_core_types.h"

enum dom_err_codes {
    DOM_OK = 0,
    DOM_ERR_UNKNOWN = 1,
    DOM_ERR_INVALID_ARG = 2,
    DOM_ERR_OUT_OF_MEMORY = 3,
    DOM_ERR_OVERFLOW = 4,
    DOM_ERR_UNDERFLOW = 5,
    DOM_ERR_BOUNDS = 6,
    DOM_ERR_NOT_FOUND = 7,
    DOM_ERR_NOT_IMPLEMENTED = 8,
    DOM_ERR_IO = 9
};

const char *dom_err_str(dom_err_t code);

#endif /* DOM_CORE_ERR_H */
