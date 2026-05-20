#ifndef DOMINO_TEST_VALID_C89_HEADER_H
#define DOMINO_TEST_VALID_C89_HEADER_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct domino_test_engine domino_test_engine_t;

typedef enum domino_test_result {
    DOMINO_TEST_OK = 0,
    DOMINO_TEST_REFUSED = 1
} domino_test_result_t;

typedef struct domino_test_config {
    unsigned int struct_size;
    unsigned int api_version;
    void *user;
} domino_test_config_t;

typedef void (*domino_test_callback_t)(void *user, domino_test_result_t result);

domino_test_result_t domino_test_engine_create(const domino_test_config_t *config,
                                               domino_test_engine_t **out_engine);
void domino_test_engine_destroy(domino_test_engine_t *engine);
domino_test_result_t domino_test_engine_set_callback(domino_test_engine_t *engine,
                                                     domino_test_callback_t callback,
                                                     void *user);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_TEST_VALID_C89_HEADER_H */
