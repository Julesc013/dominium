/*


FILE: include/domino/field_layer.h


MODULE: Domino


LAYER / SUBSYSTEM: Domino API / field_layer


RESPONSIBILITY: Defines field layer metadata over domains (typed, unitful).


ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.


FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.


THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.


ERROR MODEL: Return codes/NULL pointers; no exceptions.


DETERMINISM: Layer metadata and query results are deterministic.


VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.


EXTENSION POINTS: Extend via public headers and relevant `docs/architecture/**`.


*/


#ifndef DOMINO_FIELD_LAYER_H


#define DOMINO_FIELD_LAYER_H





#include "domino/dfield.h"


#include "domino/domain.h"


#include "domino/representation.h"


#include "domino/knowledge_state.h"


#include "domino/provenance.h"





#ifdef __cplusplus


extern "C" {


#endif





/* dom_field_id: Alias to FieldId for field-layer metadata. */


typedef FieldId dom_field_id;





/* dom_field_layer_flags: Metadata flags for field layers. */


typedef enum dom_field_layer_flags {


    DOM_FIELD_LAYER_NONE = 0u,


    DOM_FIELD_LAYER_PARTIAL = (1u << 0u),


    DOM_FIELD_LAYER_LATENT = (1u << 1u)


} dom_field_layer_flags;





/* dom_field_layer_desc: Read-only metadata for a field layer. */


typedef struct dom_field_layer_desc {


    dom_field_id            field_id;


    UnitKind                unit;


    FieldStorageKind        storage;


    u32                     resolution; /* LOD/resolution index */


    dom_representation_meta representation;


    dom_domain_volume_ref   domain;


    dom_knowledge_meta      knowledge;


    dom_provenance_id       provenance_id;


    u32                     flags; /* dom_field_layer_flags */


} dom_field_layer_desc;





/* Opaque field layer handle. */


typedef struct dom_field_layer_handle dom_field_layer_handle;





/* Purpose: Describe a field layer handle. */


int dom_field_layer_describe(const dom_field_layer_handle* layer,


                             dom_field_layer_desc* out_desc);





#ifdef __cplusplus


} /* extern "C" */


#endif





#endif /* DOMINO_FIELD_LAYER_H */


