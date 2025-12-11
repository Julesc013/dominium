/* TLV tag definitions for content protos (C89). */
#ifndef D_CONTENT_TAGS_H
#define D_CONTENT_TAGS_H

#include "domino/core/types.h"

enum {
    D_CONTENT_TAG_MATERIALS       = 0x2000,
    D_CONTENT_TAG_ITEMS           = 0x2001,
    D_CONTENT_TAG_CONTAINERS      = 0x2002,
    D_CONTENT_TAG_PROCESSES       = 0x2003,
    D_CONTENT_TAG_DEPOSITS        = 0x2004,
    D_CONTENT_TAG_STRUCTURES      = 0x2005,
    D_CONTENT_TAG_MODULES         = 0x2006,
    D_CONTENT_TAG_VEHICLES        = 0x2007,
    D_CONTENT_TAG_SPLINE_PROFILES = 0x2008,
    D_CONTENT_TAG_JOB_TEMPLATES   = 0x2009,
    D_CONTENT_TAG_BUILDINGS       = 0x200A,
    D_CONTENT_TAG_BLUEPRINTS      = 0x200B
};

#endif /* D_CONTENT_TAGS_H */
