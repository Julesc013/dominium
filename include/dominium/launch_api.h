#ifndef DOMINIUM_LAUNCH_API_H
#define DOMINIUM_LAUNCH_API_H

/* Public launcher surface (WIP). */
struct dominium_launch_exports {
    unsigned api_version;
    int (*launch_game)(const char* product_id);
};

#endif /* DOMINIUM_LAUNCH_API_H */
