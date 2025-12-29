#include "dsk/dsk_splat_caps.h"
#include "dsk/dsk_digest.h"

#include <algorithm>

void dsk_splat_caps_clear(dsk_splat_caps_t *caps) {
    if (!caps) {
        return;
    }
    caps->supported_platform_triples.clear();
    caps->supported_scopes = 0u;
    caps->supported_ui_modes = 0u;
    caps->supports_atomic_swap = DSK_FALSE;
    caps->supports_resume = DSK_FALSE;
    caps->supports_pkg_ownership = DSK_FALSE;
    caps->supports_portable_ownership = DSK_FALSE;
    caps->supports_actions = 0u;
    caps->default_root_convention = DSK_SPLAT_ROOT_CONVENTION_UNKNOWN;
    caps->elevation_required = DSK_SPLAT_ELEVATION_NEVER;
    caps->rollback_semantics = DSK_SPLAT_ROLLBACK_NONE;
    caps->notes.clear();
}

dsk_u32 dsk_splat_caps_to_flags(const dsk_splat_caps_t *caps) {
    dsk_u32 flags = 0u;
    if (!caps) {
        return 0u;
    }
    if (caps->supports_atomic_swap) {
        flags |= DSK_SPLAT_CAP_ATOMIC_SWAP;
    }
    if (caps->supports_resume) {
        flags |= DSK_SPLAT_CAP_RESUME;
    }
    if (caps->supports_pkg_ownership) {
        flags |= DSK_SPLAT_CAP_PKG_OWNERSHIP;
    }
    if (caps->supports_portable_ownership) {
        flags |= DSK_SPLAT_CAP_PORTABLE_OWNERSHIP;
    }
    flags |= caps->supports_actions;
    return flags;
}

static dsk_u64 dsk_digest_u8(dsk_u64 hash, dsk_u8 v) {
    return dsk_digest64_update(hash, &v, 1u);
}

static dsk_u64 dsk_digest_u16(dsk_u64 hash, dsk_u16 v) {
    dsk_u8 b[2];
    b[0] = (dsk_u8)(v & 0xFFu);
    b[1] = (dsk_u8)((v >> 8) & 0xFFu);
    return dsk_digest64_update(hash, b, 2u);
}

static dsk_u64 dsk_digest_u32(dsk_u64 hash, dsk_u32 v) {
    dsk_u8 b[4];
    b[0] = (dsk_u8)(v & 0xFFu);
    b[1] = (dsk_u8)((v >> 8) & 0xFFu);
    b[2] = (dsk_u8)((v >> 16) & 0xFFu);
    b[3] = (dsk_u8)((v >> 24) & 0xFFu);
    return dsk_digest64_update(hash, b, 4u);
}

static dsk_u64 dsk_digest_string(dsk_u64 hash, const std::string &value) {
    hash = dsk_digest_u32(hash, (dsk_u32)value.size());
    if (!value.empty()) {
        hash = dsk_digest64_update(hash,
                                   reinterpret_cast<const dsk_u8 *>(value.c_str()),
                                   (dsk_u32)value.size());
    }
    return hash;
}

static bool dsk_string_less(const std::string &a, const std::string &b) {
    return a < b;
}

dsk_u64 dsk_splat_caps_digest64(const dsk_splat_caps_t *caps) {
    dsk_u64 hash;
    std::vector<std::string> platforms;
    dsk_u32 i;

    if (!caps) {
        return 0u;
    }

    hash = dsk_digest64_init();
    platforms = caps->supported_platform_triples;
    std::sort(platforms.begin(), platforms.end(), dsk_string_less);
    hash = dsk_digest_u32(hash, (dsk_u32)platforms.size());
    for (i = 0u; i < platforms.size(); ++i) {
        hash = dsk_digest_string(hash, platforms[i]);
    }

    hash = dsk_digest_u32(hash, caps->supported_scopes);
    hash = dsk_digest_u32(hash, caps->supported_ui_modes);
    hash = dsk_digest_u8(hash, (dsk_u8)(caps->supports_atomic_swap ? 1u : 0u));
    hash = dsk_digest_u8(hash, (dsk_u8)(caps->supports_resume ? 1u : 0u));
    hash = dsk_digest_u8(hash, (dsk_u8)(caps->supports_pkg_ownership ? 1u : 0u));
    hash = dsk_digest_u8(hash, (dsk_u8)(caps->supports_portable_ownership ? 1u : 0u));
    hash = dsk_digest_u32(hash, caps->supports_actions);
    hash = dsk_digest_u16(hash, caps->default_root_convention);
    hash = dsk_digest_u16(hash, caps->elevation_required);
    hash = dsk_digest_u16(hash, caps->rollback_semantics);
    hash = dsk_digest_string(hash, caps->notes);

    return hash;
}
