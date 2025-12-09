#define COBJMACROS
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "gl2_gfx.h"
#include "domino/sys.h"

#if defined(_WIN32)
#include <windows.h>
#include <GL/gl.h>
#elif defined(__APPLE__)
#include <OpenGL/gl.h>
#include <dlfcn.h>
#else
#include <GL/gl.h>
#include <GL/glx.h>
#include <dlfcn.h>
#endif

#ifndef GL_ARRAY_BUFFER
#define GL_ARRAY_BUFFER 0x8892
#endif
#ifndef GL_ELEMENT_ARRAY_BUFFER
#define GL_ELEMENT_ARRAY_BUFFER 0x8893
#endif
#ifndef GL_STATIC_DRAW
#define GL_STATIC_DRAW 0x88E4
#endif
#ifndef GL_DYNAMIC_DRAW
#define GL_DYNAMIC_DRAW 0x88E8
#endif
#ifndef GL_FRAGMENT_SHADER
#define GL_FRAGMENT_SHADER 0x8B30
#endif
#ifndef GL_VERTEX_SHADER
#define GL_VERTEX_SHADER 0x8B31
#endif
#ifndef GL_COMPILE_STATUS
#define GL_COMPILE_STATUS 0x8B81
#endif
#ifndef GL_LINK_STATUS
#define GL_LINK_STATUS 0x8B82
#endif
#ifndef GL_INFO_LOG_LENGTH
#define GL_INFO_LOG_LENGTH 0x8B84
#endif
#ifndef GL_VALIDATE_STATUS
#define GL_VALIDATE_STATUS 0x8B83
#endif
#ifndef GLchar
typedef char GLchar;
#endif
#ifndef GLsizeiptr
typedef ptrdiff_t GLsizeiptr;
#endif
#ifndef GLintptr
typedef ptrdiff_t GLintptr;
#endif

typedef void (APIENTRYP PFNGLGENBUFFERSPROC)(GLsizei, GLuint*);
typedef void (APIENTRYP PFNGLBINDBUFFERPROC)(GLenum, GLuint);
typedef void (APIENTRYP PFNGLBUFFERDATAPROC)(GLenum, GLsizeiptr, const void*, GLenum);
typedef void (APIENTRYP PFNGLDELETEBUFFERSPROC)(GLsizei, const GLuint*);
typedef GLuint(APIENTRYP PFNGLCREATESHADERPROC)(GLenum);
typedef void (APIENTRYP PFNGLSHADERSOURCEPROC)(GLuint, GLsizei, const GLchar* const*, const GLint*);
typedef void (APIENTRYP PFNGLCOMPILESHADERPROC)(GLuint);
typedef void (APIENTRYP PFNGLGETSHADERIVPROC)(GLuint, GLenum, GLint*);
typedef void (APIENTRYP PFNGLGETSHADERINFOLOGPROC)(GLuint, GLsizei, GLsizei*, GLchar*);
typedef void (APIENTRYP PFNGLDELETESHADERPROC)(GLuint);
typedef GLuint(APIENTRYP PFNGLCREATEPROGRAMPROC)(void);
typedef void (APIENTRYP PFNGLATTACHSHADERPROC)(GLuint, GLuint);
typedef void (APIENTRYP PFNGLLINKPROGRAMPROC)(GLuint);
typedef void (APIENTRYP PFNGLGETPROGRAMIVPROC)(GLuint, GLenum, GLint*);
typedef void (APIENTRYP PFNGLGETPROGRAMINFOLOGPROC)(GLuint, GLsizei, GLsizei*, GLchar*);
typedef void (APIENTRYP PFNGLDELETEPROGRAMPROC)(GLuint);
typedef void (APIENTRYP PFNGLUSEPROGRAMPROC)(GLuint);
typedef GLint(APIENTRYP PFNGLGETUNIFORMLOCATIONPROC)(GLuint, const GLchar*);
typedef void (APIENTRYP PFNGLUNIFORMMATRIX4FVPROC)(GLint, GLsizei, GLboolean, const GLfloat*);
typedef void (APIENTRYP PFNGLUNIFORM1IPROC)(GLint, GLint);
typedef void (APIENTRYP PFNGLUNIFORM4FVPROC)(GLint, GLsizei, const GLfloat*);
typedef void (APIENTRYP PFNGLENABLEVERTEXATTRIBARRAYPROC)(GLuint);
typedef void (APIENTRYP PFNGLDISABLEVERTEXATTRIBARRAYPROC)(GLuint);
typedef void (APIENTRYP PFNGLVERTEXATTRIBPOINTERPROC)(GLuint, GLint, GLenum, GLboolean, GLsizei, const void*);
typedef void (APIENTRYP PFNGLBINDATTRIBLOCATIONPROC)(GLuint, GLuint, const GLchar*);
typedef GLint(APIENTRYP PFNGLGETATTRIBLOCATIONPROC)(GLuint, const GLchar*);

static PFNGLGENBUFFERSPROC              p_glGenBuffers = NULL;
static PFNGLBINDBUFFERPROC              p_glBindBuffer = NULL;
static PFNGLBUFFERDATAPROC              p_glBufferData = NULL;
static PFNGLDELETEBUFFERSPROC           p_glDeleteBuffers = NULL;
static PFNGLCREATESHADERPROC            p_glCreateShader = NULL;
static PFNGLSHADERSOURCEPROC            p_glShaderSource = NULL;
static PFNGLCOMPILESHADERPROC           p_glCompileShader = NULL;
static PFNGLGETSHADERIVPROC             p_glGetShaderiv = NULL;
static PFNGLGETSHADERINFOLOGPROC        p_glGetShaderInfoLog = NULL;
static PFNGLDELETESHADERPROC            p_glDeleteShader = NULL;
static PFNGLCREATEPROGRAMPROC           p_glCreateProgram = NULL;
static PFNGLATTACHSHADERPROC            p_glAttachShader = NULL;
static PFNGLLINKPROGRAMPROC             p_glLinkProgram = NULL;
static PFNGLGETPROGRAMIVPROC            p_glGetProgramiv = NULL;
static PFNGLGETPROGRAMINFOLOGPROC       p_glGetProgramInfoLog = NULL;
static PFNGLDELETEPROGRAMPROC           p_glDeleteProgram = NULL;
static PFNGLUSEPROGRAMPROC              p_glUseProgram = NULL;
static PFNGLGETUNIFORMLOCATIONPROC      p_glGetUniformLocation = NULL;
static PFNGLUNIFORMMATRIX4FVPROC        p_glUniformMatrix4fv = NULL;
static PFNGLUNIFORM1IPROC               p_glUniform1i = NULL;
static PFNGLUNIFORM4FVPROC              p_glUniform4fv = NULL;
static PFNGLENABLEVERTEXATTRIBARRAYPROC p_glEnableVertexAttribArray = NULL;
static PFNGLDISABLEVERTEXATTRIBARRAYPROC p_glDisableVertexAttribArray = NULL;
static PFNGLVERTEXATTRIBPOINTERPROC     p_glVertexAttribPointer = NULL;
static PFNGLBINDATTRIBLOCATIONPROC      p_glBindAttribLocation = NULL;
static PFNGLGETATTRIBLOCATIONPROC       p_glGetAttribLocation = NULL;

typedef struct gl2_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} gl2_cmd_clear_payload_t;

typedef struct gl2_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} gl2_lines_header_t;

typedef struct gl2_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} gl2_line_vertex_t;

typedef struct gl2_sprite_vertex_t {
    float    x;
    float    y;
    float    z;
    float    u;
    float    v;
    uint32_t color;
} gl2_sprite_vertex_t;

typedef struct gl2_mesh_vertex_t {
    float x;
    float y;
    float z;
    float nx;
    float ny;
    float nz;
    float u;
    float v;
} gl2_mesh_vertex_t;

gl2_state_t g_gl2;

static bool      gl2_init(const dgfx_desc* desc);
static void      gl2_shutdown(void);
static dgfx_caps gl2_get_caps(void);
static void      gl2_resize(int width, int height);
static void      gl2_begin_frame(void);
static void      gl2_execute(const dgfx_cmd_buffer* cmd_buf);
static void      gl2_end_frame(void);

static bool gl2_create_context(void);
static bool gl2_create_context_win32(void);
static bool gl2_create_context_cocoa(void);
static bool gl2_create_context_x11(void);
static void gl2_init_gl_state(void);
static bool gl2_load_gl_functions(void);
static bool gl2_create_programs(void);
static bool gl2_create_buffers(void);
static void gl2_build_caps(void);
static unsigned int gl2_compile_shader(GLenum type, const char* src);
static unsigned int gl2_link_program(unsigned int vs, unsigned int fs, int bind_attrs);
static void gl2_cmd_clear(const uint8_t* payload, size_t payload_size);
static void gl2_cmd_set_viewport(const uint8_t* payload);
static void gl2_cmd_set_camera(const uint8_t* payload);
static void gl2_cmd_set_pipeline(const uint8_t* payload);
static void gl2_cmd_set_texture(const uint8_t* payload);
static void gl2_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void gl2_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void gl2_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void gl2_cmd_draw_text(const uint8_t* payload, size_t payload_size);
static void gl2_set_identity(float* m);

static const dgfx_backend_vtable g_gl2_vtable = {
    gl2_init,
    gl2_shutdown,
    gl2_get_caps,
    gl2_resize,
    gl2_begin_frame,
    gl2_execute,
    gl2_end_frame
};

const dgfx_backend_vtable* dgfx_gl2_get_vtable(void)
{
    return &g_gl2_vtable;
}

static void gl2_set_identity(float* m)
{
    int i;
    if (!m) {
        return;
    }
    for (i = 0; i < 16; ++i) {
        m[i] = 0.0f;
    }
    m[0] = 1.0f;
    m[5] = 1.0f;
    m[10] = 1.0f;
    m[15] = 1.0f;
}

static void* gl2_get_proc(const char* name)
{
    void* p = NULL;
    if (!name) {
        return NULL;
    }
#if defined(_WIN32)
    p = (void*)wglGetProcAddress(name);
    if (!p) {
        HMODULE mod = LoadLibraryA("opengl32.dll");
        if (mod) {
            p = (void*)GetProcAddress(mod, name);
        }
    }
#elif defined(__APPLE__)
    p = dlsym(RTLD_DEFAULT, name);
#else
    p = (void*)glXGetProcAddress((const GLubyte*)name);
    if (!p) {
        p = dlsym(RTLD_DEFAULT, name);
    }
#endif
    return p;
}

static bool gl2_load_gl_functions(void)
{
    p_glGenBuffers = (PFNGLGENBUFFERSPROC)gl2_get_proc("glGenBuffers");
    p_glBindBuffer = (PFNGLBINDBUFFERPROC)gl2_get_proc("glBindBuffer");
    p_glBufferData = (PFNGLBUFFERDATAPROC)gl2_get_proc("glBufferData");
    p_glDeleteBuffers = (PFNGLDELETEBUFFERSPROC)gl2_get_proc("glDeleteBuffers");
    p_glCreateShader = (PFNGLCREATESHADERPROC)gl2_get_proc("glCreateShader");
    p_glShaderSource = (PFNGLSHADERSOURCEPROC)gl2_get_proc("glShaderSource");
    p_glCompileShader = (PFNGLCOMPILESHADERPROC)gl2_get_proc("glCompileShader");
    p_glGetShaderiv = (PFNGLGETSHADERIVPROC)gl2_get_proc("glGetShaderiv");
    p_glGetShaderInfoLog = (PFNGLGETSHADERINFOLOGPROC)gl2_get_proc("glGetShaderInfoLog");
    p_glDeleteShader = (PFNGLDELETESHADERPROC)gl2_get_proc("glDeleteShader");
    p_glCreateProgram = (PFNGLCREATEPROGRAMPROC)gl2_get_proc("glCreateProgram");
    p_glAttachShader = (PFNGLATTACHSHADERPROC)gl2_get_proc("glAttachShader");
    p_glLinkProgram = (PFNGLLINKPROGRAMPROC)gl2_get_proc("glLinkProgram");
    p_glGetProgramiv = (PFNGLGETPROGRAMIVPROC)gl2_get_proc("glGetProgramiv");
    p_glGetProgramInfoLog = (PFNGLGETPROGRAMINFOLOGPROC)gl2_get_proc("glGetProgramInfoLog");
    p_glDeleteProgram = (PFNGLDELETEPROGRAMPROC)gl2_get_proc("glDeleteProgram");
    p_glUseProgram = (PFNGLUSEPROGRAMPROC)gl2_get_proc("glUseProgram");
    p_glGetUniformLocation = (PFNGLGETUNIFORMLOCATIONPROC)gl2_get_proc("glGetUniformLocation");
    p_glUniformMatrix4fv = (PFNGLUNIFORMMATRIX4FVPROC)gl2_get_proc("glUniformMatrix4fv");
    p_glUniform1i = (PFNGLUNIFORM1IPROC)gl2_get_proc("glUniform1i");
    p_glUniform4fv = (PFNGLUNIFORM4FVPROC)gl2_get_proc("glUniform4fv");
    p_glEnableVertexAttribArray = (PFNGLENABLEVERTEXATTRIBARRAYPROC)gl2_get_proc("glEnableVertexAttribArray");
    p_glDisableVertexAttribArray = (PFNGLDISABLEVERTEXATTRIBARRAYPROC)gl2_get_proc("glDisableVertexAttribArray");
    p_glVertexAttribPointer = (PFNGLVERTEXATTRIBPOINTERPROC)gl2_get_proc("glVertexAttribPointer");
    p_glBindAttribLocation = (PFNGLBINDATTRIBLOCATIONPROC)gl2_get_proc("glBindAttribLocation");
    p_glGetAttribLocation = (PFNGLGETATTRIBLOCATIONPROC)gl2_get_proc("glGetAttribLocation");

    if (!p_glGenBuffers || !p_glBindBuffer || !p_glBufferData ||
        !p_glDeleteBuffers || !p_glCreateShader || !p_glShaderSource ||
        !p_glCompileShader || !p_glGetShaderiv || !p_glCreateProgram ||
        !p_glAttachShader || !p_glLinkProgram || !p_glGetProgramiv ||
        !p_glUseProgram || !p_glGetUniformLocation || !p_glUniformMatrix4fv ||
        !p_glUniform1i || !p_glEnableVertexAttribArray ||
        !p_glDisableVertexAttribArray || !p_glVertexAttribPointer) {
        return false;
    }

    return true;
}

static bool gl2_create_context(void)
{
#if defined(_WIN32)
    return gl2_create_context_win32();
#elif defined(__APPLE__)
    return gl2_create_context_cocoa();
#else
    return gl2_create_context_x11();
#endif
}

static bool gl2_create_context_win32(void)
{
#if defined(_WIN32)
    HWND hwnd;
    HDC hdc;
    HGLRC hglrc;
    PIXELFORMATDESCRIPTOR pfd;
    int pf;

    hwnd = (HWND)g_gl2.native_window;
    if (!hwnd) {
        return false;
    }

    hdc = GetDC(hwnd);
    if (!hdc) {
        return false;
    }

    memset(&pfd, 0, sizeof(pfd));
    pfd.nSize = sizeof(pfd);
    pfd.nVersion = 1;
    pfd.dwFlags = PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER;
    pfd.iPixelType = PFD_TYPE_RGBA;
    pfd.cColorBits = 32;
    pfd.cDepthBits = 24;
    pfd.cStencilBits = 8;
    pfd.iLayerType = PFD_MAIN_PLANE;

    pf = ChoosePixelFormat(hdc, &pfd);
    if (pf == 0) {
        ReleaseDC(hwnd, hdc);
        return false;
    }
    if (!SetPixelFormat(hdc, pf, &pfd)) {
        ReleaseDC(hwnd, hdc);
        return false;
    }

    hglrc = wglCreateContext(hdc);
    if (!hglrc) {
        ReleaseDC(hwnd, hdc);
        return false;
    }
    if (!wglMakeCurrent(hdc, hglrc)) {
        wglDeleteContext(hglrc);
        ReleaseDC(hwnd, hdc);
        return false;
    }

    g_gl2.gl_drawable = (void*)hdc;
    g_gl2.gl_context = (void*)hglrc;
    return true;
#else
    return false;
#endif
}

static bool gl2_create_context_cocoa(void)
{
#if defined(__APPLE__)
    (void)g_gl2;
    return false;
#else
    return false;
#endif
}

static bool gl2_create_context_x11(void)
{
#if !defined(_WIN32) && !defined(__APPLE__)
    (void)g_gl2;
    return false;
#else
    return false;
#endif
}

static void gl2_init_gl_state(void)
{
    glViewport(0, 0, g_gl2.width, g_gl2.height);

    glDisable(GL_LIGHTING);
    glDisable(GL_FOG);
    glDisable(GL_CULL_FACE);
    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LEQUAL);

    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    glClearColor(0.0f, 0.0f, 0.0f, 1.0f);
}

static void gl2_build_caps(void)
{
    GLint max_tex = 0;
    memset(&g_gl2.caps, 0, sizeof(g_gl2.caps));
    g_gl2.caps.name = "gl2";
    g_gl2.caps.supports_2d = true;
    g_gl2.caps.supports_3d = true;
    g_gl2.caps.supports_text = false;
    g_gl2.caps.supports_rt = false;
    g_gl2.caps.supports_alpha = true;
    glGetIntegerv(GL_MAX_TEXTURE_SIZE, &max_tex);
    g_gl2.caps.max_texture_size = (int32_t)max_tex;
}

static unsigned int gl2_compile_shader(GLenum type, const char* src)
{
    GLuint sh;
    GLint ok;

    if (!src || !p_glCreateShader || !p_glShaderSource || !p_glCompileShader || !p_glGetShaderiv) {
        return 0u;
    }

    sh = p_glCreateShader(type);
    if (!sh) {
        return 0u;
    }
    p_glShaderSource(sh, 1, &src, NULL);
    p_glCompileShader(sh);
    p_glGetShaderiv(sh, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        if (p_glGetShaderInfoLog) {
            char log[512];
            GLsizei len = 0;
            log[0] = '\0';
            p_glGetShaderInfoLog(sh, (GLsizei)sizeof(log) - 1, &len, log);
        }
        if (p_glDeleteShader) {
            p_glDeleteShader(sh);
        }
        sh = 0u;
    }
    return sh;
}

static unsigned int gl2_link_program(unsigned int vs, unsigned int fs, int bind_attrs)
{
    GLuint prog;
    GLint ok;

    if (!vs || !fs || !p_glCreateProgram || !p_glAttachShader || !p_glLinkProgram || !p_glGetProgramiv) {
        return 0u;
    }

    prog = p_glCreateProgram();
    if (!prog) {
        return 0u;
    }

    if (bind_attrs && p_glBindAttribLocation) {
        p_glBindAttribLocation(prog, 0, "a_pos");
        p_glBindAttribLocation(prog, 1, "a_color");
        p_glBindAttribLocation(prog, 2, "a_uv");
    }

    p_glAttachShader(prog, vs);
    p_glAttachShader(prog, fs);
    p_glLinkProgram(prog);
    p_glGetProgramiv(prog, GL_LINK_STATUS, &ok);
    if (!ok) {
        if (p_glGetProgramInfoLog) {
            char log[512];
            GLsizei len = 0;
            log[0] = '\0';
            p_glGetProgramInfoLog(prog, (GLsizei)sizeof(log) - 1, &len, log);
        }
        if (p_glDeleteProgram) {
            p_glDeleteProgram(prog);
        }
        prog = 0u;
    }

    return prog;
}

static bool gl2_create_programs(void)
{
    static const char* vs_2d_src =
        "uniform mat4 u_mvp;\n"
        "attribute vec3 a_pos;\n"
        "attribute vec4 a_color;\n"
        "attribute vec2 a_uv;\n"
        "varying vec4 v_color;\n"
        "varying vec2 v_uv;\n"
        "void main() {\n"
        "    v_color = a_color;\n"
        "    v_uv = a_uv;\n"
        "    gl_Position = u_mvp * vec4(a_pos, 1.0);\n"
        "}\n";

    static const char* fs_2d_src =
        "varying vec4 v_color;\n"
        "varying vec2 v_uv;\n"
        "uniform sampler2D u_tex;\n"
        "void main() {\n"
        "    vec4 t = texture2D(u_tex, v_uv);\n"
        "    gl_FragColor = v_color * t;\n"
        "}\n";

    static const char* vs_lines_src =
        "uniform mat4 u_mvp;\n"
        "attribute vec3 a_pos;\n"
        "attribute vec4 a_color;\n"
        "varying vec4 v_color;\n"
        "void main() {\n"
        "    v_color = a_color;\n"
        "    gl_Position = u_mvp * vec4(a_pos, 1.0);\n"
        "}\n";

    static const char* fs_lines_src =
        "varying vec4 v_color;\n"
        "void main() {\n"
        "    gl_FragColor = v_color;\n"
        "}\n";

    static const char* vs_3d_src =
        "uniform mat4 u_view;\n"
        "uniform mat4 u_proj;\n"
        "uniform mat4 u_world;\n"
        "attribute vec3 a_pos;\n"
        "void main() {\n"
        "    gl_Position = u_proj * u_view * u_world * vec4(a_pos, 1.0);\n"
        "}\n";

    static const char* fs_3d_src =
        "void main() {\n"
        "    gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);\n"
        "}\n";

    GLuint vs;
    GLuint fs;
    GLuint prog;

    vs = gl2_compile_shader(GL_VERTEX_SHADER, vs_2d_src);
    fs = gl2_compile_shader(GL_FRAGMENT_SHADER, fs_2d_src);
    if (!vs || !fs) {
        if (vs && p_glDeleteShader) p_glDeleteShader(vs);
        if (fs && p_glDeleteShader) p_glDeleteShader(fs);
        return false;
    }
    prog = gl2_link_program(vs, fs, 1);
    if (p_glDeleteShader) {
        p_glDeleteShader(vs);
        p_glDeleteShader(fs);
    }
    g_gl2.program_2d = prog;
    if (!g_gl2.program_2d) {
        return false;
    }

    vs = gl2_compile_shader(GL_VERTEX_SHADER, vs_lines_src);
    fs = gl2_compile_shader(GL_FRAGMENT_SHADER, fs_lines_src);
    if (!vs || !fs) {
        if (vs && p_glDeleteShader) p_glDeleteShader(vs);
        if (fs && p_glDeleteShader) p_glDeleteShader(fs);
        return false;
    }
    prog = gl2_link_program(vs, fs, 1);
    if (p_glDeleteShader) {
        p_glDeleteShader(vs);
        p_glDeleteShader(fs);
    }
    g_gl2.program_lines = prog;
    if (!g_gl2.program_lines) {
        return false;
    }

    vs = gl2_compile_shader(GL_VERTEX_SHADER, vs_3d_src);
    fs = gl2_compile_shader(GL_FRAGMENT_SHADER, fs_3d_src);
    if (!vs || !fs) {
        if (vs && p_glDeleteShader) p_glDeleteShader(vs);
        if (fs && p_glDeleteShader) p_glDeleteShader(fs);
        return false;
    }
    prog = gl2_link_program(vs, fs, 1);
    if (p_glDeleteShader) {
        p_glDeleteShader(vs);
        p_glDeleteShader(fs);
    }
    g_gl2.program_3d = prog;
    if (!g_gl2.program_3d) {
        return false;
    }

    if (p_glGetUniformLocation) {
        g_gl2.u_2d_mvp = p_glGetUniformLocation(g_gl2.program_2d, "u_mvp");
        g_gl2.u_2d_color = p_glGetUniformLocation(g_gl2.program_2d, "u_color");
        g_gl2.u_2d_tex = p_glGetUniformLocation(g_gl2.program_2d, "u_tex");

        g_gl2.u_lines_mvp = p_glGetUniformLocation(g_gl2.program_lines, "u_mvp");
        g_gl2.u_lines_color = p_glGetUniformLocation(g_gl2.program_lines, "u_color");

        g_gl2.u_3d_view = p_glGetUniformLocation(g_gl2.program_3d, "u_view");
        g_gl2.u_3d_proj = p_glGetUniformLocation(g_gl2.program_3d, "u_proj");
        g_gl2.u_3d_world = p_glGetUniformLocation(g_gl2.program_3d, "u_world");
    } else {
        g_gl2.u_2d_mvp = -1;
        g_gl2.u_2d_color = -1;
        g_gl2.u_2d_tex = -1;
        g_gl2.u_lines_mvp = -1;
        g_gl2.u_lines_color = -1;
        g_gl2.u_3d_view = -1;
        g_gl2.u_3d_proj = -1;
        g_gl2.u_3d_world = -1;
    }

    if (p_glGetAttribLocation) {
        g_gl2.a_2d_pos = p_glGetAttribLocation(g_gl2.program_2d, "a_pos");
        g_gl2.a_2d_color = p_glGetAttribLocation(g_gl2.program_2d, "a_color");
        g_gl2.a_2d_uv = p_glGetAttribLocation(g_gl2.program_2d, "a_uv");
        g_gl2.a_lines_pos = p_glGetAttribLocation(g_gl2.program_lines, "a_pos");
        g_gl2.a_lines_color = p_glGetAttribLocation(g_gl2.program_lines, "a_color");
    } else {
        g_gl2.a_2d_pos = 0;
        g_gl2.a_2d_color = 1;
        g_gl2.a_2d_uv = 2;
        g_gl2.a_lines_pos = 0;
        g_gl2.a_lines_color = 1;
    }

    return true;
}

static bool gl2_create_buffers(void)
{
    GLuint buffers[4];

    if (!p_glGenBuffers || !p_glBindBuffer || !p_glBufferData) {
        return false;
    }

    p_glGenBuffers(4, buffers);
    g_gl2.vbo_sprites = buffers[0];
    g_gl2.vbo_lines = buffers[1];
    g_gl2.vbo_mesh = buffers[2];
    g_gl2.ibo_mesh = buffers[3];

    p_glBindBuffer(GL_ARRAY_BUFFER, g_gl2.vbo_sprites);
    p_glBufferData(GL_ARRAY_BUFFER, 0, NULL, GL_DYNAMIC_DRAW);

    p_glBindBuffer(GL_ARRAY_BUFFER, g_gl2.vbo_lines);
    p_glBufferData(GL_ARRAY_BUFFER, 0, NULL, GL_DYNAMIC_DRAW);

    p_glBindBuffer(GL_ARRAY_BUFFER, g_gl2.vbo_mesh);
    p_glBufferData(GL_ARRAY_BUFFER, 0, NULL, GL_DYNAMIC_DRAW);

    p_glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, g_gl2.ibo_mesh);
    p_glBufferData(GL_ELEMENT_ARRAY_BUFFER, 0, NULL, GL_DYNAMIC_DRAW);

    p_glBindBuffer(GL_ARRAY_BUFFER, 0);
    p_glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0);

    return true;
}

static bool gl2_init(const dgfx_desc* desc)
{
    if (!desc || !desc->window) {
        return false;
    }

    memset(&g_gl2, 0, sizeof(g_gl2));

    g_gl2.window = desc->window;
    g_gl2.native_window = dsys_window_get_native_handle(desc->window);
    if (!g_gl2.native_window) {
        return false;
    }
    g_gl2.width = (desc->width > 0) ? desc->width : 800;
    g_gl2.height = (desc->height > 0) ? desc->height : 600;
    g_gl2.fullscreen = 0;
    g_gl2.vsync = desc->vsync ? 1 : 0;

#if defined(_WIN32)
    g_gl2.platform = 1;
#elif defined(__APPLE__)
    g_gl2.platform = 2;
#else
    g_gl2.platform = 3;
#endif

    gl2_set_identity(g_gl2.view);
    gl2_set_identity(g_gl2.proj);
    gl2_set_identity(g_gl2.world);

    if (!gl2_create_context()) {
        gl2_shutdown();
        return false;
    }

    if (!gl2_load_gl_functions()) {
        gl2_shutdown();
        return false;
    }

    gl2_init_gl_state();

    if (!gl2_create_programs()) {
        gl2_shutdown();
        return false;
    }

    if (!gl2_create_buffers()) {
        gl2_shutdown();
        return false;
    }

    gl2_build_caps();

    g_gl2.frame_in_progress = 0;
    g_gl2.current_pipeline = 0;

    return true;
}

static void gl2_shutdown(void)
{
    if (g_gl2.program_2d && p_glDeleteProgram) {
        p_glDeleteProgram(g_gl2.program_2d);
    }
    if (g_gl2.program_3d && p_glDeleteProgram) {
        p_glDeleteProgram(g_gl2.program_3d);
    }
    if (g_gl2.program_lines && p_glDeleteProgram) {
        p_glDeleteProgram(g_gl2.program_lines);
    }

    if ((g_gl2.vbo_sprites || g_gl2.vbo_lines || g_gl2.vbo_mesh || g_gl2.ibo_mesh) &&
        p_glDeleteBuffers) {
        GLuint buffers[4];
        GLsizei count = 0;
        if (g_gl2.vbo_sprites) buffers[count++] = g_gl2.vbo_sprites;
        if (g_gl2.vbo_lines) buffers[count++] = g_gl2.vbo_lines;
        if (g_gl2.vbo_mesh) buffers[count++] = g_gl2.vbo_mesh;
        if (g_gl2.ibo_mesh) buffers[count++] = g_gl2.ibo_mesh;
        if (count > 0) {
            p_glDeleteBuffers(count, buffers);
        }
    }

#if defined(_WIN32)
    {
        HDC hdc = (HDC)g_gl2.gl_drawable;
        HGLRC hglrc = (HGLRC)g_gl2.gl_context;
        HWND hwnd = (HWND)g_gl2.native_window;

        if (hglrc && wglGetCurrentContext() == hglrc) {
            wglMakeCurrent(NULL, NULL);
        }
        if (hglrc) {
            wglDeleteContext(hglrc);
        }
        if (hdc && hwnd) {
            ReleaseDC(hwnd, hdc);
        }
    }
#elif defined(__APPLE__)
    /* NSOpenGLContext cleanup would go here. */
#else
    /* GLX cleanup would go here. */
#endif

    memset(&g_gl2, 0, sizeof(g_gl2));
}

static dgfx_caps gl2_get_caps(void)
{
    return g_gl2.caps;
}

static void gl2_resize(int width, int height)
{
    if (width <= 0 || height <= 0) {
        return;
    }
    g_gl2.width = width;
    g_gl2.height = height;

    glViewport(0, 0, g_gl2.width, g_gl2.height);
}

static void gl2_begin_frame(void)
{
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    g_gl2.frame_in_progress = 1;
}

static void gl2_end_frame(void)
{
    if (!g_gl2.frame_in_progress) {
        return;
    }

    glFlush();

#if defined(_WIN32)
    {
        HDC hdc = (HDC)g_gl2.gl_drawable;
        if (hdc) {
            SwapBuffers(hdc);
        }
    }
#elif defined(__APPLE__)
    /* [NSOpenGLContext flushBuffer] would be called here. */
#else
    /* glXSwapBuffers(display, window) would be called here. */
#endif

    g_gl2.frame_in_progress = 0;
}

static void gl2_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    gl2_cmd_clear_payload_t clr;
    float r;
    float g;
    float b;
    float a;

    r = 0.0f;
    g = 0.0f;
    b = 0.0f;
    a = 1.0f;

    if (payload && payload_size >= sizeof(gl2_cmd_clear_payload_t)) {
        memcpy(&clr, payload, sizeof(clr));
        r = (float)clr.r / 255.0f;
        g = (float)clr.g / 255.0f;
        b = (float)clr.b / 255.0f;
        a = (float)clr.a / 255.0f;
    }

    glClearColor(r, g, b, a);
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
}

static void gl2_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
    glViewport(0, 0, g_gl2.width, g_gl2.height);
}

static void gl2_cmd_set_camera(const uint8_t* payload)
{
    (void)payload;

    if (!p_glUseProgram || !p_glUniformMatrix4fv) {
        return;
    }

    if (g_gl2.program_3d) {
        p_glUseProgram(g_gl2.program_3d);
        if (g_gl2.u_3d_view >= 0) {
            p_glUniformMatrix4fv(g_gl2.u_3d_view, 1, GL_FALSE, g_gl2.view);
        }
        if (g_gl2.u_3d_proj >= 0) {
            p_glUniformMatrix4fv(g_gl2.u_3d_proj, 1, GL_FALSE, g_gl2.proj);
        }
        if (g_gl2.u_3d_world >= 0) {
            p_glUniformMatrix4fv(g_gl2.u_3d_world, 1, GL_FALSE, g_gl2.world);
        }
    }

    if (g_gl2.program_2d && g_gl2.u_2d_mvp >= 0) {
        float mvp[16];
        int i;
        for (i = 0; i < 16; ++i) {
            mvp[i] = (i % 5 == 0) ? 1.0f : 0.0f;
        }
        p_glUseProgram(g_gl2.program_2d);
        p_glUniformMatrix4fv(g_gl2.u_2d_mvp, 1, GL_FALSE, mvp);
    }

    if (g_gl2.program_lines && g_gl2.u_lines_mvp >= 0) {
        float mvp_line[16];
        int i;
        for (i = 0; i < 16; ++i) {
            mvp_line[i] = (i % 5 == 0) ? 1.0f : 0.0f;
        }
        p_glUseProgram(g_gl2.program_lines);
        p_glUniformMatrix4fv(g_gl2.u_lines_mvp, 1, GL_FALSE, mvp_line);
    }
}

static void gl2_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;

    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LEQUAL);
    glEnable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    g_gl2.current_pipeline = 0;
}

static void gl2_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
    glBindTexture(GL_TEXTURE_2D, 0);
}

static void gl2_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    gl2_sprite_vertex_t verts[6];

    (void)payload;
    (void)payload_size;

    if (!g_gl2.program_2d || !p_glUseProgram || !p_glBindBuffer || !p_glBufferData ||
        !p_glEnableVertexAttribArray || !p_glVertexAttribPointer || !p_glDisableVertexAttribArray) {
        return;
    }

    verts[0].x = -0.5f; verts[0].y = -0.5f; verts[0].z = 0.0f;
    verts[0].u = 0.0f;  verts[0].v = 1.0f;  verts[0].color = 0xffffffffu;
    verts[1].x = -0.5f; verts[1].y =  0.5f; verts[1].z = 0.0f;
    verts[1].u = 0.0f;  verts[1].v = 0.0f;  verts[1].color = 0xffffffffu;
    verts[2].x =  0.5f; verts[2].y =  0.5f; verts[2].z = 0.0f;
    verts[2].u = 1.0f;  verts[2].v = 0.0f;  verts[2].color = 0xffffffffu;

    verts[3] = verts[0];
    verts[4] = verts[2];
    verts[5].x =  0.5f; verts[5].y = -0.5f; verts[5].z = 0.0f;
    verts[5].u = 1.0f;  verts[5].v = 1.0f;  verts[5].color = 0xffffffffu;

    p_glUseProgram(g_gl2.program_2d);
    p_glBindBuffer(GL_ARRAY_BUFFER, g_gl2.vbo_sprites);
    p_glBufferData(GL_ARRAY_BUFFER, (GLsizeiptr)sizeof(verts), verts, GL_DYNAMIC_DRAW);

    if (g_gl2.a_2d_pos >= 0) {
        p_glEnableVertexAttribArray((GLuint)g_gl2.a_2d_pos);
        p_glVertexAttribPointer((GLuint)g_gl2.a_2d_pos, 3, GL_FLOAT, GL_FALSE,
                                (GLsizei)sizeof(gl2_sprite_vertex_t), (const void*)0);
    }
    if (g_gl2.a_2d_color >= 0) {
        p_glEnableVertexAttribArray((GLuint)g_gl2.a_2d_color);
        p_glVertexAttribPointer((GLuint)g_gl2.a_2d_color, 4, GL_UNSIGNED_BYTE, GL_TRUE,
                                (GLsizei)sizeof(gl2_sprite_vertex_t),
                                (const void*)(sizeof(float) * 5));
    }
    if (g_gl2.a_2d_uv >= 0) {
        p_glEnableVertexAttribArray((GLuint)g_gl2.a_2d_uv);
        p_glVertexAttribPointer((GLuint)g_gl2.a_2d_uv, 2, GL_FLOAT, GL_FALSE,
                                (GLsizei)sizeof(gl2_sprite_vertex_t),
                                (const void*)(sizeof(float) * 3));
    }

    glDrawArrays(GL_TRIANGLES, 0, 6);

    if (g_gl2.a_2d_pos >= 0) p_glDisableVertexAttribArray((GLuint)g_gl2.a_2d_pos);
    if (g_gl2.a_2d_color >= 0) p_glDisableVertexAttribArray((GLuint)g_gl2.a_2d_color);
    if (g_gl2.a_2d_uv >= 0) p_glDisableVertexAttribArray((GLuint)g_gl2.a_2d_uv);
    p_glBindBuffer(GL_ARRAY_BUFFER, 0);
}

static void gl2_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    gl2_lines_header_t header;
    const gl2_line_vertex_t* src;
    GLsizei count;
    size_t required;

    if (!g_gl2.program_lines || !p_glUseProgram || !p_glBindBuffer || !p_glBufferData ||
        !p_glEnableVertexAttribArray || !p_glVertexAttribPointer || !p_glDisableVertexAttribArray ||
        !payload) {
        return;
    }
    if (payload_size < sizeof(header)) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    required = sizeof(header) + ((size_t)header.vertex_count * sizeof(gl2_line_vertex_t));
    if (payload_size < required || header.vertex_count == 0u) {
        return;
    }

    src = (const gl2_line_vertex_t*)(payload + sizeof(header));
    count = (GLsizei)header.vertex_count;

    p_glUseProgram(g_gl2.program_lines);
    p_glBindBuffer(GL_ARRAY_BUFFER, g_gl2.vbo_lines);
    p_glBufferData(GL_ARRAY_BUFFER, (GLsizeiptr)(sizeof(gl2_line_vertex_t) * count),
                   src, GL_DYNAMIC_DRAW);

    if (g_gl2.a_lines_pos >= 0) {
        p_glEnableVertexAttribArray((GLuint)g_gl2.a_lines_pos);
        p_glVertexAttribPointer((GLuint)g_gl2.a_lines_pos, 3, GL_FLOAT, GL_FALSE,
                                (GLsizei)sizeof(gl2_line_vertex_t), (const void*)0);
    }
    if (g_gl2.a_lines_color >= 0) {
        p_glEnableVertexAttribArray((GLuint)g_gl2.a_lines_color);
        p_glVertexAttribPointer((GLuint)g_gl2.a_lines_color, 4, GL_UNSIGNED_BYTE, GL_TRUE,
                                (GLsizei)sizeof(gl2_line_vertex_t),
                                (const void*)(sizeof(float) * 3));
    }

    glDrawArrays(GL_LINES, 0, count);

    if (g_gl2.a_lines_pos >= 0) p_glDisableVertexAttribArray((GLuint)g_gl2.a_lines_pos);
    if (g_gl2.a_lines_color >= 0) p_glDisableVertexAttribArray((GLuint)g_gl2.a_lines_color);
    p_glBindBuffer(GL_ARRAY_BUFFER, 0);
}

static void gl2_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    gl2_mesh_vertex_t verts[3];

    (void)payload;
    (void)payload_size;

    if (!g_gl2.program_3d || !p_glUseProgram || !p_glBindBuffer || !p_glBufferData ||
        !p_glEnableVertexAttribArray || !p_glVertexAttribPointer || !p_glDisableVertexAttribArray) {
        return;
    }

    verts[0].x = 0.0f; verts[0].y = 0.5f; verts[0].z = 0.0f;
    verts[1].x = -0.5f; verts[1].y = -0.5f; verts[1].z = 0.0f;
    verts[2].x = 0.5f; verts[2].y = -0.5f; verts[2].z = 0.0f;

    p_glUseProgram(g_gl2.program_3d);
    p_glBindBuffer(GL_ARRAY_BUFFER, g_gl2.vbo_mesh);
    p_glBufferData(GL_ARRAY_BUFFER, (GLsizeiptr)sizeof(verts), verts, GL_DYNAMIC_DRAW);

    p_glEnableVertexAttribArray(0);
    p_glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE,
                            (GLsizei)sizeof(gl2_mesh_vertex_t), (const void*)0);

    glDrawArrays(GL_TRIANGLES, 0, 3);

    p_glDisableVertexAttribArray(0);
    p_glBindBuffer(GL_ARRAY_BUFFER, 0);
}

static void gl2_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
}

static void gl2_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_gl2.frame_in_progress) {
        return;
    }

    header_size = sizeof(dgfx_cmd);
    ptr = cmd_buf->data;
    end = cmd_buf->data + cmd_buf->size;

    while (ptr + header_size <= end) {
        const dgfx_cmd* cmd;
        const uint8_t* payload;
        size_t payload_size;
        size_t total_size;

        cmd = (const dgfx_cmd*)ptr;
        payload_size = cmd->payload_size;
        total_size = header_size + payload_size;
        if (ptr + total_size > end) {
            break;
        }
        payload = ptr + header_size;

        switch (cmd->opcode) {
        case DGFX_CMD_CLEAR:
            gl2_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            gl2_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            gl2_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            gl2_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            gl2_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            gl2_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            gl2_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            gl2_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            gl2_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
