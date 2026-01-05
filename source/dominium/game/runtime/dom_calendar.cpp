/*
FILE: source/dominium/game/runtime/dom_calendar.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/calendar
RESPONSIBILITY: Calendar registry and deterministic fixed-ratio conversion helpers.
*/
#include "runtime/dom_calendar.h"

#include <stddef.h>
#include <vector>

namespace {

struct CalendarEntry {
    dom_calendar_id id;
    dom_calendar_desc desc;
};

static int mul_div_u64(u64 a, u64 b, u64 div, u64 *out_val) {
    if (!out_val || div == 0ull) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (b != 0ull && a > ((u64)~(u64)0) / b) {
        return DOM_CALENDAR_OVERFLOW;
    }
    *out_val = (a * b) / div;
    return DOM_CALENDAR_OK;
}

static int append_char(char *out, u32 cap, u32 *offset, char c) {
    if (!out || !offset || cap == 0u) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if ((*offset + 1u) >= cap) {
        return DOM_CALENDAR_ERR;
    }
    out[*offset] = c;
    *offset += 1u;
    return DOM_CALENDAR_OK;
}

static int append_u64(char *out, u32 cap, u32 *offset, u64 value) {
    char buf[32];
    u32 len = 0u;
    u32 i;

    if (!out || !offset || cap == 0u) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }

    if (value == 0ull) {
        buf[len++] = '0';
    } else {
        while (value > 0ull && len < sizeof(buf)) {
            buf[len++] = (char)('0' + (value % 10ull));
            value /= 10ull;
        }
    }
    if ((*offset + len + 1u) > cap) {
        return DOM_CALENDAR_ERR;
    }
    for (i = 0u; i < len; ++i) {
        out[*offset + i] = buf[len - 1u - i];
    }
    *offset += len;
    return DOM_CALENDAR_OK;
}

static int append_two_digits(char *out, u32 cap, u32 *offset, u32 value) {
    if (!out || !offset || cap == 0u) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if ((*offset + 2u + 1u) > cap) {
        return DOM_CALENDAR_ERR;
    }
    out[*offset + 0u] = (char)('0' + ((value / 10u) % 10u));
    out[*offset + 1u] = (char)('0' + (value % 10u));
    *offset += 2u;
    return DOM_CALENDAR_OK;
}

} // namespace

struct dom_calendar_registry {
    std::vector<CalendarEntry> entries;
};

dom_calendar_registry *dom_calendar_registry_create(void) {
    return new dom_calendar_registry();
}

void dom_calendar_registry_destroy(dom_calendar_registry *registry) {
    if (!registry) {
        return;
    }
    delete registry;
}

int dom_calendar_registry_register(dom_calendar_registry *registry,
                                   dom_calendar_id id,
                                   const dom_calendar_desc *desc) {
    size_t i;
    CalendarEntry entry;
    if (!registry || !desc || id == 0u) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    for (i = 0u; i < registry->entries.size(); ++i) {
        if (registry->entries[i].id == id) {
            return DOM_CALENDAR_DUPLICATE_ID;
        }
    }
    entry.id = id;
    entry.desc = *desc;
    registry->entries.push_back(entry);
    return DOM_CALENDAR_OK;
}

int dom_calendar_registry_get(const dom_calendar_registry *registry,
                              dom_calendar_id id,
                              dom_calendar_desc *out_desc) {
    size_t i;
    if (!registry || !out_desc) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    for (i = 0u; i < registry->entries.size(); ++i) {
        if (registry->entries[i].id == id) {
            *out_desc = registry->entries[i].desc;
            return DOM_CALENDAR_OK;
        }
    }
    return DOM_CALENDAR_NOT_FOUND;
}

int dom_calendar_ticks_to_time(const dom_calendar_desc *desc,
                               dom_tick tick,
                               dom_ups ups,
                               dom_calendar_time *out_time) {
    u64 day_ticks = 0ull;
    u64 year_ticks = 0ull;
    u64 tick_in_year;
    u64 tick_in_day;
    u64 sec_in_day;
    u64 day_seconds_int;
    int rc;

    if (!desc || !out_time || ups == 0u) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (desc->kind != DOM_CALENDAR_FIXED_RATIO) {
        return DOM_CALENDAR_NOT_IMPLEMENTED;
    }
    if (desc->day_seconds_num == 0ull || desc->day_seconds_den == 0ull ||
        desc->year_seconds_num == 0ull || desc->year_seconds_den == 0ull) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    rc = mul_div_u64(desc->day_seconds_num, (u64)ups, desc->day_seconds_den, &day_ticks);
    if (rc != DOM_CALENDAR_OK || day_ticks == 0ull) {
        return DOM_CALENDAR_OVERFLOW;
    }
    rc = mul_div_u64(desc->year_seconds_num, (u64)ups, desc->year_seconds_den, &year_ticks);
    if (rc != DOM_CALENDAR_OK || year_ticks == 0ull) {
        return DOM_CALENDAR_OVERFLOW;
    }

    out_time->year = (u64)(tick / year_ticks);
    tick_in_year = (u64)(tick % year_ticks);
    out_time->day_of_year = (u32)(tick_in_year / day_ticks);
    tick_in_day = (u64)(tick_in_year % day_ticks);
    sec_in_day = (u64)(tick_in_day / ups);
    out_time->subsecond_ticks = (u32)(tick_in_day % ups);

    day_seconds_int = desc->day_seconds_num / desc->day_seconds_den;
    if (day_seconds_int == 0ull) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }
    if (sec_in_day >= day_seconds_int) {
        sec_in_day = day_seconds_int - 1ull;
    }
    out_time->hour = (u32)(sec_in_day / 3600ull);
    out_time->minute = (u32)((sec_in_day / 60ull) % 60ull);
    out_time->second = (u32)(sec_in_day % 60ull);
    return DOM_CALENDAR_OK;
}

int dom_calendar_format_basic(const dom_calendar_time *t,
                              char *out,
                              u32 out_cap) {
    u32 offset = 0u;
    int rc;

    if (!t || !out || out_cap == 0u) {
        return DOM_CALENDAR_INVALID_ARGUMENT;
    }

    rc = append_char(out, out_cap, &offset, 'Y');
    if (rc != DOM_CALENDAR_OK) return rc;
    rc = append_u64(out, out_cap, &offset, t->year);
    if (rc != DOM_CALENDAR_OK) return rc;
    rc = append_char(out, out_cap, &offset, ' ');
    if (rc != DOM_CALENDAR_OK) return rc;
    rc = append_char(out, out_cap, &offset, 'D');
    if (rc != DOM_CALENDAR_OK) return rc;
    rc = append_u64(out, out_cap, &offset, (u64)t->day_of_year);
    if (rc != DOM_CALENDAR_OK) return rc;
    rc = append_char(out, out_cap, &offset, ' ');
    if (rc != DOM_CALENDAR_OK) return rc;
    rc = append_two_digits(out, out_cap, &offset, t->hour);
    if (rc != DOM_CALENDAR_OK) return rc;
    rc = append_char(out, out_cap, &offset, ':');
    if (rc != DOM_CALENDAR_OK) return rc;
    rc = append_two_digits(out, out_cap, &offset, t->minute);
    if (rc != DOM_CALENDAR_OK) return rc;
    rc = append_char(out, out_cap, &offset, ':');
    if (rc != DOM_CALENDAR_OK) return rc;
    rc = append_two_digits(out, out_cap, &offset, t->second);
    if (rc != DOM_CALENDAR_OK) return rc;

    if (offset >= out_cap) {
        return DOM_CALENDAR_ERR;
    }
    out[offset] = '\0';
    return DOM_CALENDAR_OK;
}
