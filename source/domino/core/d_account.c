#include <string.h>

#include "core/d_account.h"

#define DACCOUNT_MAX 1024u

typedef struct d_account_entry_s {
    d_account acc;
    int       in_use;
} d_account_entry;

static d_account_entry g_accounts[DACCOUNT_MAX];
static d_account_id g_next_account_id = 1u;
static int g_accounts_initialized = 0;

int d_account_system_init(void) {
    if (g_accounts_initialized) {
        return 0;
    }
    memset(g_accounts, 0, sizeof(g_accounts));
    g_next_account_id = 1u;
    g_accounts_initialized = 1;
    return 0;
}

void d_account_system_shutdown(void) {
    memset(g_accounts, 0, sizeof(g_accounts));
    g_next_account_id = 1u;
    g_accounts_initialized = 0;
}

static d_account_entry *d_account_find(d_account_id id) {
    u32 i;
    if (id == 0u) {
        return (d_account_entry *)0;
    }
    for (i = 0u; i < DACCOUNT_MAX; ++i) {
        if (g_accounts[i].in_use && g_accounts[i].acc.id == id) {
            return &g_accounts[i];
        }
    }
    return (d_account_entry *)0;
}

static d_account_entry *d_account_alloc(void) {
    u32 i;
    for (i = 0u; i < DACCOUNT_MAX; ++i) {
        if (!g_accounts[i].in_use) {
            return &g_accounts[i];
        }
    }
    return (d_account_entry *)0;
}

d_account_id d_account_create(q32_32 initial_balance) {
    d_account_entry *e;
    d_account_id id;
    if (!g_accounts_initialized) {
        (void)d_account_system_init();
    }
    e = d_account_alloc();
    if (!e) {
        return 0u;
    }
    id = g_next_account_id++;
    memset(e, 0, sizeof(*e));
    e->acc.id = id;
    e->acc.balance = initial_balance;
    e->in_use = 1;
    return id;
}

int d_account_get(d_account_id id, d_account *out) {
    d_account_entry *e;
    if (!out) {
        return -1;
    }
    e = d_account_find(id);
    if (!e) {
        return -1;
    }
    *out = e->acc;
    return 0;
}

int d_account_update(const d_account *acc) {
    d_account_entry *e;
    if (!acc || acc->id == 0u) {
        return -1;
    }
    e = d_account_find(acc->id);
    if (!e) {
        return -1;
    }
    e->acc = *acc;
    return 0;
}

int d_account_transfer(
    d_account_id from,
    d_account_id to,
    q32_32       amount
) {
    d_account_entry *a;
    d_account_entry *b;
    if (from == 0u || to == 0u) {
        return -1;
    }
    if (amount <= 0) {
        return -1;
    }
    a = d_account_find(from);
    b = d_account_find(to);
    if (!a || !b) {
        return -1;
    }
    if (a->acc.balance < amount) {
        return -1;
    }
    a->acc.balance -= amount;
    b->acc.balance += amount;
    return 0;
}

