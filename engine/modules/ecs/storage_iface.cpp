/*
FILE: engine/modules/ecs/storage_iface.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / ecs
RESPONSIBILITY: ECS storage backend interface symbols.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside ecs.
DETERMINISM: N/A (interface only).
*/
#include "domino/ecs/ecs_storage_iface.h"

IEcsStorageBackend::~IEcsStorageBackend() {}
