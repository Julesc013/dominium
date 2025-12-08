#import <Cocoa/Cocoa.h>
#import <CoreFoundation/CoreFoundation.h>

#import "cocoa_sys.h"

#include <string.h>

#define COCOA_EVENT_QUEUE_CAP 64
#define COCOA_INVALID_POS ((int32_t)0x80000000u)

static dsys_window* g_window_list = NULL;
static dsys_event   g_event_queue[COCOA_EVENT_QUEUE_CAP];
static int          g_event_head = 0;
static int          g_event_tail = 0;
static int          g_app_inited = 0;

static void         cocoa_enqueue_event(const dsys_event* ev);
static bool         cocoa_dequeue_event(dsys_event* ev);
static void         cocoa_add_window(dsys_window* win);
static void         cocoa_remove_window(dsys_window* win);
static dsys_window* cocoa_find_window(NSWindow* nswin);
static void         cocoa_update_window_size(dsys_window* win, NSWindow* nswin);
static int32_t      cocoa_round_double(double v);
static void         cocoa_queue_text_input(NSEvent* event);
static bool         cocoa_translate_event(NSEvent* event, dsys_event* out);

@interface DominoWindow : NSObject <NSWindowDelegate>
@property(nonatomic, strong) NSWindow* window;
@property(nonatomic, assign) dsys_window* handle;
@end

@implementation DominoWindow
- (void)windowWillClose:(NSNotification*)notification
{
    dsys_event ev;
    (void)notification;
    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_QUIT;
    if (self.handle) {
        self.handle->native_handle = NULL;
    }
    cocoa_enqueue_event(&ev);
}

- (void)windowDidResize:(NSNotification*)notification
{
    dsys_event ev;
    (void)notification;
    if (!self.window || !self.handle) {
        return;
    }
    cocoa_update_window_size(self.handle, self.window);
    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_WINDOW_RESIZED;
    ev.payload.window.width = self.handle->width;
    ev.payload.window.height = self.handle->height;
    cocoa_enqueue_event(&ev);
}
@end

static void cocoa_enqueue_event(const dsys_event* ev)
{
    int next;
    if (!ev) {
        return;
    }
    next = (g_event_tail + 1) % COCOA_EVENT_QUEUE_CAP;
    if (next == g_event_head) {
        return;
    }
    g_event_queue[g_event_tail] = *ev;
    g_event_tail = next;
}

static bool cocoa_dequeue_event(dsys_event* ev)
{
    if (g_event_head == g_event_tail) {
        return false;
    }
    if (ev) {
        *ev = g_event_queue[g_event_head];
    }
    g_event_head = (g_event_head + 1) % COCOA_EVENT_QUEUE_CAP;
    return true;
}

static void cocoa_add_window(dsys_window* win)
{
    if (!win) {
        return;
    }
    win->next = g_window_list;
    g_window_list = win;
}

static void cocoa_remove_window(dsys_window* win)
{
    dsys_window* cur;
    dsys_window* prev;

    prev = NULL;
    cur = g_window_list;
    while (cur) {
        if (cur == win) {
            if (prev) {
                prev->next = cur->next;
            } else {
                g_window_list = cur->next;
            }
            return;
        }
        prev = cur;
        cur = cur->next;
    }
}

static dsys_window* cocoa_find_window(NSWindow* nswin)
{
    dsys_window* cur;

    cur = g_window_list;
    while (cur) {
        DominoWindow* wrapper;
        wrapper = (__bridge DominoWindow*)cur->objc_ref;
        if (wrapper && wrapper.window == nswin) {
            return cur;
        }
        cur = cur->next;
    }
    return NULL;
}

static int32_t cocoa_round_double(double v)
{
    if (v >= 0.0) {
        return (int32_t)(v + 0.5);
    }
    return (int32_t)(v - 0.5);
}

static void cocoa_queue_text_input(NSEvent* event)
{
    NSString* chars;
    const char* utf8;
    dsys_event ev;

    if (!event) {
        return;
    }

    chars = [event characters];
    if (!chars || [chars length] == 0) {
        return;
    }

    utf8 = [chars UTF8String];
    if (!utf8 || utf8[0] == '\0') {
        return;
    }
    if (([event modifierFlags] & NSCommandKeyMask) != 0) {
        return;
    }

    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_TEXT_INPUT;
    strncpy(ev.payload.text.text, utf8, sizeof(ev.payload.text.text) - 1u);
    ev.payload.text.text[sizeof(ev.payload.text.text) - 1u] = '\0';
    cocoa_enqueue_event(&ev);
}

static void cocoa_update_window_size(dsys_window* win, NSWindow* nswin)
{
    NSRect content_rect;
    if (!win || !nswin) {
        return;
    }
    content_rect = [nswin contentRectForFrameRect:[nswin frame]];
    win->width = (int32_t)content_rect.size.width;
    win->height = (int32_t)content_rect.size.height;
}

static bool cocoa_translate_event(NSEvent* event, dsys_event* out)
{
    NSEventType  type;
    dsys_window* win;

    if (!event || !out) {
        return false;
    }

    win = cocoa_find_window([event window]);
    type = [event type];

    switch (type) {
    case NSEventTypeKeyDown:
    case NSEventTypeKeyUp:
        out->type = (type == NSEventTypeKeyDown) ? DSYS_EVENT_KEY_DOWN : DSYS_EVENT_KEY_UP;
        out->payload.key.key = (int32_t)[event keyCode];
        out->payload.key.repeat = [event isARepeat] ? true : false;
        if (type == NSEventTypeKeyDown) {
            cocoa_queue_text_input(event);
        }
        return true;

    case NSEventTypeLeftMouseDown:
    case NSEventTypeRightMouseDown:
    case NSEventTypeOtherMouseDown:
    case NSEventTypeLeftMouseUp:
    case NSEventTypeRightMouseUp:
    case NSEventTypeOtherMouseUp:
        out->type = DSYS_EVENT_MOUSE_BUTTON;
        out->payload.mouse_button.button = (int32_t)[event buttonNumber] + 1;
        out->payload.mouse_button.pressed = (type == NSEventTypeLeftMouseDown ||
                                             type == NSEventTypeRightMouseDown ||
                                             type == NSEventTypeOtherMouseDown) ? true : false;
        out->payload.mouse_button.clicks = (int32_t)[event clickCount];
        return true;

    case NSEventTypeMouseMoved:
    case NSEventTypeLeftMouseDragged:
    case NSEventTypeRightMouseDragged:
    case NSEventTypeOtherMouseDragged:
        {
            NSView*  view;
            NSPoint  p;
            CGFloat  height;
            int32_t  x;
            int32_t  y;

            view = [[event window] contentView];
            if (!view) {
                return false;
            }

            p = [view convertPoint:[event locationInWindow] fromView:nil];
            height = [view bounds].size.height;
            x = (int32_t)p.x;
            y = (int32_t)(height - p.y);

            out->type = DSYS_EVENT_MOUSE_MOVE;
            out->payload.mouse_move.x = x;
            out->payload.mouse_move.y = y;
            out->payload.mouse_move.dx = 0;
            out->payload.mouse_move.dy = 0;
            if (win) {
                if (win->last_x != COCOA_INVALID_POS && win->last_y != COCOA_INVALID_POS) {
                    out->payload.mouse_move.dx = x - win->last_x;
                    out->payload.mouse_move.dy = y - win->last_y;
                }
                win->last_x = x;
                win->last_y = y;
            }
            return true;
        }

    case NSEventTypeScrollWheel:
        out->type = DSYS_EVENT_MOUSE_WHEEL;
        out->payload.mouse_wheel.delta_x = cocoa_round_double([event scrollingDeltaX]);
        out->payload.mouse_wheel.delta_y = cocoa_round_double([event scrollingDeltaY]);
        return true;

    default:
        break;
    }

    return false;
}

dsys_result cocoa_app_init(void)
{
    @autoreleasepool {
        if (g_app_inited) {
            return DSYS_OK;
        }
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
        [NSApp finishLaunching];
        g_app_inited = 1;
        return DSYS_OK;
    }
}

void cocoa_app_shutdown(void)
{
    dsys_window* cur;
    dsys_window* next;

    @autoreleasepool {
        cur = g_window_list;
        while (cur) {
            next = cur->next;
            cocoa_win_destroy(cur);
            cur = next;
        }
        g_window_list = NULL;
        g_event_head = 0;
        g_event_tail = 0;
        g_app_inited = 0;
    }
}

dsys_window* cocoa_win_create(const dsys_window_desc* desc)
{
    dsys_window_desc local;
    dsys_window*     win;
    DominoWindow*    wrapper;
    NSUInteger       style;
    NSRect           rect;
    NSWindow*        nswin;
    int32_t          w;
    int32_t          h;
    int32_t          x;
    int32_t          y;

    @autoreleasepool {
        if (desc) {
            local = *desc;
        } else {
            local.x = 0;
            local.y = 0;
            local.width = 800;
            local.height = 600;
            local.mode = DWIN_MODE_WINDOWED;
        }

        x = local.x;
        y = local.y;
        w = local.width != 0 ? local.width : 800;
        h = local.height != 0 ? local.height : 600;

        rect = NSMakeRect((CGFloat)x, (CGFloat)y, (CGFloat)w, (CGFloat)h);
        style = NSTitledWindowMask |
                NSClosableWindowMask |
                NSMiniaturizableWindowMask |
                NSResizableWindowMask;

        nswin = [[NSWindow alloc] initWithContentRect:rect
                                            styleMask:style
                                              backing:NSBackingStoreBuffered
                                                defer:NO];
        if (!nswin) {
            return NULL;
        }

        [nswin setTitle:@"Domino"];
        [nswin setAcceptsMouseMovedEvents:YES];

        win = (dsys_window*)malloc(sizeof(dsys_window));
        if (!win) {
            return NULL;
        }
        memset(win, 0, sizeof(*win));
        win->width = w;
        win->height = h;
        win->mode = local.mode;
        win->last_x = COCOA_INVALID_POS;
        win->last_y = COCOA_INVALID_POS;
        win->next = NULL;
        win->native_handle = NULL;
        win->objc_ref = NULL;

        wrapper = [[DominoWindow alloc] init];
        if (!wrapper) {
            free(win);
            return NULL;
        }
        wrapper.window = nswin;
        wrapper.handle = win;
        win->objc_ref = (__bridge_retained void*)wrapper;
        win->native_handle = (void*)nswin;
        [nswin setDelegate:wrapper];
        [nswin makeKeyAndOrderFront:nil];
        [NSApp activateIgnoringOtherApps:YES];

        cocoa_add_window(win);
        cocoa_win_set_mode(win, local.mode);
        cocoa_update_window_size(win, nswin);
        return win;
    }
}

void cocoa_win_destroy(dsys_window* win)
{
    @autoreleasepool {
        DominoWindow* wrapper;
        NSWindow*     nswin;

        if (!win) {
            return;
        }

        wrapper = (__bridge DominoWindow*)win->objc_ref;
        nswin = wrapper ? wrapper.window : nil;

        if (nswin) {
            [nswin orderOut:nil];
            [nswin setDelegate:nil];
            [nswin close];
        }

        if (wrapper) {
            wrapper.handle = NULL;
            wrapper.window = nil;
        }

        cocoa_remove_window(win);
        if (win->objc_ref) {
            CFBridgingRelease(win->objc_ref);
        }
        win->objc_ref = NULL;
        win->native_handle = NULL;
        free(win);
    }
}

void cocoa_win_set_mode(dsys_window* win, dsys_window_mode mode)
{
    @autoreleasepool {
        DominoWindow* wrapper;
        NSWindow*     nswin;

        if (!win) {
            return;
        }

        wrapper = (__bridge DominoWindow*)win->objc_ref;
        nswin = wrapper ? wrapper.window : nil;
        if (!nswin) {
            win->mode = mode;
            return;
        }

        if (mode == DWIN_MODE_FULLSCREEN) {
            [nswin setCollectionBehavior:NSWindowCollectionBehaviorFullScreenPrimary];
            if (([nswin styleMask] & NSFullScreenWindowMask) == 0) {
                [nswin toggleFullScreen:nil];
            }
        } else {
            if (([nswin styleMask] & NSFullScreenWindowMask) != 0) {
                [nswin toggleFullScreen:nil];
            }
            if (mode == DWIN_MODE_BORDERLESS) {
                NSScreen* screen;
                screen = [nswin screen];
                if (!screen) {
                    screen = [NSScreen mainScreen];
                }
                [nswin setStyleMask:NSBorderlessWindowMask];
                [nswin setFrame:[screen frame] display:YES];
            } else {
                NSUInteger new_style;
                new_style = NSTitledWindowMask |
                            NSClosableWindowMask |
                            NSMiniaturizableWindowMask |
                            NSResizableWindowMask;
                [nswin setStyleMask:new_style];
            }
        }
        win->mode = mode;
    }
}

void cocoa_win_set_size(dsys_window* win, int32_t w, int32_t h)
{
    @autoreleasepool {
        DominoWindow* wrapper;
        NSWindow*     nswin;
        NSSize        size;

        if (!win) {
            return;
        }

        wrapper = (__bridge DominoWindow*)win->objc_ref;
        nswin = wrapper ? wrapper.window : nil;
        if (!nswin) {
            return;
        }

        size = NSMakeSize((CGFloat)w, (CGFloat)h);
        [nswin setContentSize:size];
        cocoa_update_window_size(win, nswin);
    }
}

void cocoa_win_get_size(dsys_window* win, int32_t* w, int32_t* h)
{
    @autoreleasepool {
        DominoWindow* wrapper;
        NSWindow*     nswin;

        if (!win) {
            return;
        }

        wrapper = (__bridge DominoWindow*)win->objc_ref;
        nswin = wrapper ? wrapper.window : nil;
        if (nswin) {
            cocoa_update_window_size(win, nswin);
        }

        if (w) {
            *w = win->width;
        }
        if (h) {
            *h = win->height;
        }
    }
}

void* cocoa_win_get_native_handle(dsys_window* win)
{
    if (!win) {
        return NULL;
    }
    return win->native_handle;
}

bool cocoa_win_poll_event(dsys_event* ev)
{
    NSEvent* event;

    if (ev) {
        memset(ev, 0, sizeof(*ev));
    }

    if (cocoa_dequeue_event(ev)) {
        return true;
    }

    @autoreleasepool {
        event = [NSApp nextEventMatchingMask:NSEventMaskAny
                                   untilDate:[NSDate distantPast]
                                      inMode:NSDefaultRunLoopMode
                                     dequeue:YES];
        if (!event) {
            return false;
        }

        if (ev && cocoa_translate_event(event, ev)) {
            [NSApp sendEvent:event];
            [NSApp updateWindows];
            return true;
        }

        [NSApp sendEvent:event];
        [NSApp updateWindows];
    }

    return false;
}
