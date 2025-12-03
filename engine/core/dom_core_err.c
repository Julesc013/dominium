#include "dom_core_err.h"

const char *dom_err_str(dom_err_t code)
{
    switch (code) {
    case DOM_OK:                 return "OK";
    case DOM_ERR_UNKNOWN:        return "UNKNOWN";
    case DOM_ERR_INVALID_ARG:    return "INVALID_ARG";
    case DOM_ERR_OUT_OF_MEMORY:  return "OUT_OF_MEMORY";
    case DOM_ERR_OVERFLOW:       return "OVERFLOW";
    case DOM_ERR_UNDERFLOW:      return "UNDERFLOW";
    case DOM_ERR_BOUNDS:         return "BOUNDS";
    case DOM_ERR_NOT_FOUND:      return "NOT_FOUND";
    case DOM_ERR_NOT_IMPLEMENTED:return "NOT_IMPLEMENTED";
    case DOM_ERR_IO:             return "IO";
    default:                     return "UNSPECIFIED";
    }
}
