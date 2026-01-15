#import <Cocoa/Cocoa.h>
#import <CoreFoundation/CoreFoundation.h>
#import <Foundation/Foundation.h>
#import <objc/runtime.h>
#include <string.h>

#import "cocoa_sys.h"

static int      cocoa_mouse_has_last = 0;
static int32_t  cocoa_mouse_last_x = 0;
static int32_t  cocoa_mouse_last_y = 0;

static int32_t cocoa_round_double(double v)
{
    if (v >= 0.0) {
        return (int32_t)(v + 0.5);
    }
    return (int32_t)(v - 0.5);
}

static bool cocoa_copy_path(NSString* path, char* buf, size_t buf_size)
{
    const char* fs;
    size_t      len;

    if (!path || !buf || buf_size == 0u) {
        return false;
    }

    fs = [path fileSystemRepresentation];
    if (!fs) {
        return false;
    }

    len = strlen(fs);
    if (len >= buf_size) {
        len = buf_size - 1u;
    }
    memcpy(buf, fs, len);
    buf[len] = '\0';
    return true;
}

static void cocoa_translate_mouse(NSWindow* window, NSEvent* event)
{
    NSView* view;
    NSPoint p;
    CGFloat height;
    dsys_event ev;
    int32_t x;
    int32_t y;

    view = [window contentView];
    if (!view) {
        return;
    }

    p = [view convertPoint:[event locationInWindow] fromView:nil];
    height = [view bounds].size.height;
    x = (int32_t)p.x;
    y = (int32_t)(height - p.y);

    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_MOUSE_MOVE;
    ev.payload.mouse_move.x = x;
    ev.payload.mouse_move.y = y;
    ev.payload.mouse_move.dx = 0;
    ev.payload.mouse_move.dy = 0;
    if (cocoa_mouse_has_last) {
        ev.payload.mouse_move.dx = x - cocoa_mouse_last_x;
        ev.payload.mouse_move.dy = y - cocoa_mouse_last_y;
    }
    cocoa_mouse_has_last = 1;
    cocoa_mouse_last_x = x;
    cocoa_mouse_last_y = y;
    cocoa_push_event(&ev);
}

static void cocoa_translate_event(NSEvent* event)
{
    NSUInteger type;
    dsys_event  ev;

    if (!event) {
        return;
    }

    type = [event type];
    switch (type) {
    case NSKeyDown:
    case NSKeyUp:
        memset(&ev, 0, sizeof(ev));
        ev.type = (type == NSKeyDown) ? DSYS_EVENT_KEY_DOWN : DSYS_EVENT_KEY_UP;
        ev.payload.key.key = (int32_t)[event keyCode];
        ev.payload.key.repeat = [event isARepeat] ? true : false;
        cocoa_push_event(&ev);
        break;

    case NSLeftMouseDown:
    case NSRightMouseDown:
    case NSOtherMouseDown:
    case NSLeftMouseUp:
    case NSRightMouseUp:
    case NSOtherMouseUp:
        memset(&ev, 0, sizeof(ev));
        ev.type = DSYS_EVENT_MOUSE_BUTTON;
        ev.payload.mouse_button.button = (int32_t)[event buttonNumber] + 1;
        ev.payload.mouse_button.pressed = (type == NSLeftMouseDown ||
                                           type == NSRightMouseDown ||
                                           type == NSOtherMouseDown) ? true : false;
        ev.payload.mouse_button.clicks = (int32_t)[event clickCount];
        cocoa_push_event(&ev);
        break;

    case NSMouseMoved:
    case NSLeftMouseDragged:
    case NSRightMouseDragged:
    case NSOtherMouseDragged:
        cocoa_translate_mouse([event window], event);
        break;

    case NSScrollWheel:
        memset(&ev, 0, sizeof(ev));
        ev.type = DSYS_EVENT_MOUSE_WHEEL;
        ev.payload.mouse_wheel.delta_x = cocoa_round_double([event scrollingDeltaX]);
        ev.payload.mouse_wheel.delta_y = cocoa_round_double([event scrollingDeltaY]);
        cocoa_push_event(&ev);
        break;

    default:
        break;
    }
}

@interface DominoWindowDelegate : NSObject <NSWindowDelegate>
@end

@implementation DominoWindowDelegate
- (BOOL)windowShouldClose:(id)sender
{
    dsys_event ev;
    (void)sender;
    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_QUIT;
    cocoa_push_event(&ev);
    return NO;
}

- (void)windowDidResize:(NSNotification*)notification
{
    NSWindow* nswin;
    int       w;
    int       h;
    dsys_event ev;

    nswin = (NSWindow*)[notification object];
    if (!nswin) {
        return;
    }

    w = 0;
    h = 0;
    cocoa_objc_get_window_size((__bridge void*)nswin, &w, &h);

    if (g_cocoa.main_window) {
        g_cocoa.main_window->width = w;
        g_cocoa.main_window->height = h;
    }

    memset(&ev, 0, sizeof(ev));
    ev.type = DSYS_EVENT_WINDOW_RESIZED;
    ev.payload.window.width = w;
    ev.payload.window.height = h;
    cocoa_push_event(&ev);
}
@end

@interface DominoWindow : NSWindow
@end

@implementation DominoWindow
- (void)sendEvent:(NSEvent*)event
{
    cocoa_translate_event(event);
    [super sendEvent:event];
}
@end

void cocoa_objc_init_app(void)
{
    @autoreleasepool {
        [NSApplication sharedApplication];
        [NSApp setActivationPolicy:NSApplicationActivationPolicyRegular];
        [NSApp finishLaunching];
    }
}

void cocoa_objc_shutdown(void)
{
    /* no-op for now */
}

void* cocoa_objc_create_window(int width, int height, const char* title)
{
    @autoreleasepool {
        NSRect        rect;
        NSUInteger    style;
        DominoWindow* win;
        DominoWindowDelegate* delegate;
        NSString*     ns_title;
        void*         handle;

        rect = NSMakeRect(0, 0, (CGFloat)width, (CGFloat)height);
        style = NSTitledWindowMask |
                NSClosableWindowMask |
                NSMiniaturizableWindowMask |
                NSResizableWindowMask;

        win = [[DominoWindow alloc] initWithContentRect:rect
                                             styleMask:style
                                               backing:NSBackingStoreBuffered
                                                 defer:NO];
        if (!win) {
            return NULL;
        }

        if (title) {
            ns_title = [NSString stringWithUTF8String:title];
        } else {
            ns_title = @"Domino";
        }
        [win setTitle:ns_title];
        [win setAcceptsMouseMovedEvents:YES];

        delegate = [[DominoWindowDelegate alloc] init];
        [win setDelegate:delegate];
        objc_setAssociatedObject(win, "domino_delegate", delegate, OBJC_ASSOCIATION_RETAIN_NONATOMIC);

        [win makeKeyAndOrderFront:nil];
        [NSApp activateIgnoringOtherApps:YES];

        handle = (__bridge_retained void*)win;
        return handle;
    }
}

void cocoa_objc_destroy_window(void* ns_window)
{
    @autoreleasepool {
        NSWindow* win;
        if (!ns_window) {
            return;
        }
        win = (__bridge NSWindow*)ns_window;
        [win setDelegate:nil];
        [win orderOut:nil];
        [win close];
        objc_setAssociatedObject(win, "domino_delegate", nil, OBJC_ASSOCIATION_ASSIGN);
        cocoa_mouse_has_last = 0;
        CFRelease((__bridge CFTypeRef)win);
    }
}

void cocoa_objc_toggle_fullscreen(void* ns_window)
{
    @autoreleasepool {
        NSWindow* win;
        if (!ns_window) {
            return;
        }
        win = (__bridge NSWindow*)ns_window;
        [win toggleFullScreen:nil];
    }
}

void cocoa_objc_resize_window(void* ns_window, int w, int h)
{
    @autoreleasepool {
        NSWindow* win;
        if (!ns_window) {
            return;
        }
        win = (__bridge NSWindow*)ns_window;
        [win setContentSize:NSMakeSize((CGFloat)w, (CGFloat)h)];
    }
}

void cocoa_objc_get_window_size(void* ns_window, int* w, int* h)
{
    @autoreleasepool {
        NSWindow* win;
        NSRect    rect;

        if (!ns_window) {
            return;
        }
        win = (__bridge NSWindow*)ns_window;
        rect = [win contentRectForFrameRect:[win frame]];
        if (w) {
            *w = (int)rect.size.width;
        }
        if (h) {
            *h = (int)rect.size.height;
        }
    }
}

void cocoa_objc_pump_events(void)
{
    @autoreleasepool {
        for (;;) {
            NSEvent* event;
            event = [NSApp nextEventMatchingMask:NSAnyEventMask
                                       untilDate:[NSDate distantPast]
                                          inMode:NSDefaultRunLoopMode
                                         dequeue:YES];
            if (!event) {
                break;
            }
            [NSApp sendEvent:event];
            [NSApp updateWindows];
        }
    }
}

bool cocoa_objc_get_path_exec(char* buf, size_t buf_size)
{
    NSString* path;
    path = [[NSBundle mainBundle] executablePath];
    if (!path) {
        path = [[NSProcessInfo processInfo] arguments].firstObject;
    }
    if (path) {
        path = [path stringByDeletingLastPathComponent];
    }
    if (!path) {
        path = [[NSFileManager defaultManager] currentDirectoryPath];
    }
    return cocoa_copy_path(path, buf, buf_size);
}

bool cocoa_objc_get_path_home(char* buf, size_t buf_size)
{
    return cocoa_copy_path(NSHomeDirectory(), buf, buf_size);
}

static NSString* cocoa_app_support_subpath(NSString* subdir)
{
    NSArray* paths;
    NSString* base;

    paths = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory, NSUserDomainMask, YES);
    if ([paths count] == 0) {
        return nil;
    }
    base = [paths objectAtIndex:0];
    return [[base stringByAppendingPathComponent:@"dominium"] stringByAppendingPathComponent:subdir];
}

static NSString* cocoa_cache_path(void)
{
    NSArray* paths;
    NSString* base;

    paths = NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES);
    if ([paths count] == 0) {
        return nil;
    }
    base = [paths objectAtIndex:0];
    return [base stringByAppendingPathComponent:@"dominium"];
}

bool cocoa_objc_get_path_config(char* buf, size_t buf_size)
{
    NSString* path;
    path = cocoa_app_support_subpath(@"config");
    if (!path) {
        return false;
    }
    return cocoa_copy_path(path, buf, buf_size);
}

bool cocoa_objc_get_path_data(char* buf, size_t buf_size)
{
    NSString* path;
    path = cocoa_app_support_subpath(@"data");
    if (!path) {
        return false;
    }
    return cocoa_copy_path(path, buf, buf_size);
}

bool cocoa_objc_get_path_cache(char* buf, size_t buf_size)
{
    NSString* path;
    path = cocoa_cache_path();
    if (!path) {
        return false;
    }
    return cocoa_copy_path(path, buf, buf_size);
}

bool cocoa_objc_get_path_temp(char* buf, size_t buf_size)
{
    NSString* path;
    path = NSTemporaryDirectory();
    return cocoa_copy_path(path, buf, buf_size);
}
