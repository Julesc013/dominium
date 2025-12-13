/* Subsystem TLV tags used in save/load containers. */
#ifndef D_SERIALIZE_TAGS_H
#define D_SERIALIZE_TAGS_H

enum {
    TAG_SUBSYS_DWORLD  = 0x1000,
    TAG_SUBSYS_DRES    = 0x1001,
    TAG_SUBSYS_DENV    = 0x1002,
    TAG_SUBSYS_DBULD   = 0x1003,
    TAG_SUBSYS_DTRANS  = 0x1004,
    TAG_SUBSYS_DSTRUCT = 0x1005,
    TAG_SUBSYS_DVEH    = 0x1006,
    TAG_SUBSYS_DJOB    = 0x1007,
    TAG_SUBSYS_DNET    = 0x1008,
    TAG_SUBSYS_DREPLAY = 0x1009,
    TAG_SUBSYS_DHYDRO  = 0x100A,
    TAG_SUBSYS_DLITHO  = 0x100B
    /* Reserve 0x2000+ for mod/third-party subsystems */
};

#endif /* D_SERIALIZE_TAGS_H */
