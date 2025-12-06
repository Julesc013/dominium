#ifndef DOM_KEYS_H
#define DOM_KEYS_H

/*
 * Canonical keycodes for Dominium input mapping.
 * Values align with Win32 virtual-key codes for the covered range to keep
 * normalization simple across backends. Other platforms must translate to
 * these codes before handing events to the client layer.
 */

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_keycode_e {
    DOM_KEY_UNKNOWN = 0,

    /* Control keys */
    DOM_KEY_ESCAPE = 0x1B,
    DOM_KEY_TAB    = 0x09,
    DOM_KEY_SHIFT  = 0x10,
    DOM_KEY_CONTROL = 0x11,
    DOM_KEY_ALT    = 0x12,
    DOM_KEY_SPACE  = 0x20,

    /* Digits */
    DOM_KEY_0 = 0x30,
    DOM_KEY_1 = 0x31,
    DOM_KEY_2 = 0x32,
    DOM_KEY_3 = 0x33,
    DOM_KEY_4 = 0x34,
    DOM_KEY_5 = 0x35,
    DOM_KEY_6 = 0x36,
    DOM_KEY_7 = 0x37,
    DOM_KEY_8 = 0x38,
    DOM_KEY_9 = 0x39,

    /* Letters (uppercase ASCII) */
    DOM_KEY_A = 0x41,
    DOM_KEY_B = 0x42,
    DOM_KEY_C = 0x43,
    DOM_KEY_D = 0x44,
    DOM_KEY_E = 0x45,
    DOM_KEY_F = 0x46,
    DOM_KEY_G = 0x47,
    DOM_KEY_H = 0x48,
    DOM_KEY_I = 0x49,
    DOM_KEY_J = 0x4A,
    DOM_KEY_K = 0x4B,
    DOM_KEY_L = 0x4C,
    DOM_KEY_M = 0x4D,
    DOM_KEY_N = 0x4E,
    DOM_KEY_O = 0x4F,
    DOM_KEY_P = 0x50,
    DOM_KEY_Q = 0x51,
    DOM_KEY_R = 0x52,
    DOM_KEY_S = 0x53,
    DOM_KEY_T = 0x54,
    DOM_KEY_U = 0x55,
    DOM_KEY_V = 0x56,
    DOM_KEY_W = 0x57,
    DOM_KEY_X = 0x58,
    DOM_KEY_Y = 0x59,
    DOM_KEY_Z = 0x5A,

    /* Navigation */
    DOM_KEY_LEFT  = 0x25,
    DOM_KEY_UP    = 0x26,
    DOM_KEY_RIGHT = 0x27,
    DOM_KEY_DOWN  = 0x28,

    /* Function keys */
    DOM_KEY_F1  = 0x70,
    DOM_KEY_F2  = 0x71,
    DOM_KEY_F3  = 0x72,
    DOM_KEY_F4  = 0x73,
    DOM_KEY_F5  = 0x74,
    DOM_KEY_F6  = 0x75,
    DOM_KEY_F7  = 0x76,
    DOM_KEY_F8  = 0x77,
    DOM_KEY_F9  = 0x78,
    DOM_KEY_F10 = 0x79,
    DOM_KEY_F11 = 0x7A,
    DOM_KEY_F12 = 0x7B,

    DOM_KEYCODE_MAX = 256
} dom_keycode;

#ifdef __cplusplus
}
#endif

#endif /* DOM_KEYS_H */
