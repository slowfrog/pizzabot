from __future__ import division, print_function

import math
import time
import win32api
import win32con
import ImageGrab

def screenshot(x0, y0, x1, y1):
    im = ImageGrab.grab((x0, y0, x1, y1))
    return im.load()

def save_screenshot(x0, y0, x1, y1, filename):
    im = screenshot(x0, y0, x1, y1)
    with open(filename, "wb") as outfile:
        im.save(outfile)

def rgb_dist((r0, g0, b0), (r1, g1, b1)):
    return abs(r0 - r1) + abs(g0 -g1) + abs(b0 - b1)

LIGHT_GREEN = (90, 145, 62)
DARK_GREEN = (85, 137, 62)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
RGB_TOLERANCE = 3

def is_green_check(pix, x, y):
    return ((rgb_dist(pix[x, y], LIGHT_GREEN) < RGB_TOLERANCE) and
            (rgb_dist(pix[x + 100, y], LIGHT_GREEN) < RGB_TOLERANCE) and
            (rgb_dist(pix[x + 200, y], LIGHT_GREEN) < RGB_TOLERANCE) and
            (rgb_dist(pix[x + 50, y + 50], LIGHT_GREEN) < RGB_TOLERANCE) and
            (rgb_dist(pix[x + 150, y + 50], LIGHT_GREEN) < RGB_TOLERANCE) and
            (rgb_dist(pix[x, y + 50], DARK_GREEN) < RGB_TOLERANCE) and
            (rgb_dist(pix[x + 50, y], DARK_GREEN) < RGB_TOLERANCE) and
            (rgb_dist(pix[x + 100, y + 50], DARK_GREEN) < RGB_TOLERANCE) and
            (rgb_dist(pix[x + 150, y], DARK_GREEN) < RGB_TOLERANCE))

def slide_top_left(pix, x0, y0, dx, dy):
    for x in xrange(x0, x0 - dx - 1, -1):
        if not is_green_check(pix, x, y0):
            break
    x += 1
    for y in xrange(y0, y0 - dy - 1, -1):
        if not is_green_check(pix, x, y):
            break
    y += 1
    return (x, y)

def find_screen(debug=False):
    im = ImageGrab.grab()
    pix = im.load()
    (w, h) = im.size
    pos = None
    for x in xrange(0, w - 200, 5):
        if pos:
            break
        for y in xrange(0, h - 50, 5):
            if is_green_check(pix, x, y):
                pos = slide_top_left(pix, x, y, 5, 5)
                break

    if debug:
        (x0, y0) = pos
        print("Origin at %d,%d" % pos)
        for x in xrange(x0 - 10, x0 + 11):
            pix[x, y0] = RED
        for y in xrange(y0 - 10, y0 + 11):
            pix[x0, y] = RED
            
        with open("find_squares.png", "wb") as outfile:
            im.save(outfile)

    return pos


def click_at(x=None, y=None, delta_t=0.02):
    if ((x is not None) and (y is not None)):
        win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(delta_t)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

def slide_to(x1, y1, delta_t=1, step_t=0.05):
    count = math.floor(delta_t / step_t)
    count = 1 if count < 1 else count
    (x, y) = win32api.GetCursorPos()
    for i in xrange(count + 1):
        ratio = i / count
        xi = int(x + (x1 - x) * ratio)
        yi = int(y + (y1 - y) * ratio)
        win32api.SetCursorPos((xi, yi))
        time.sleep(step_t)

def cursor_shake(x0, y0, x1, y1):
    (xc, yc) = ((x0 + x1) / 2, (y0 + y1) / 2)
    slide_to(x0, y0, 0.15)
    slide_to(x1, y1, 0.30)
    slide_to(x0, y0, 0.30)
    slide_to(x1, y1, 0.30)
    slide_to(xc, yc, 0.15)
        
def cursor_yes():
    (xc, yc) = win32api.GetCursorPos();
    (x0, y0) = (xc, yc - 16)
    (x1, y1) = (xc, yc + 16)
    cursor_shake(x0, y0, x1, y1)
        
def cursor_no():
    (xc, yc) = win32api.GetCursorPos();
    (x0, y0) = (xc - 16, yc)
    (x1, y1) = (xc + 16, yc)
    cursor_shake(x0, y0, x1, y1)

def quit_game(origin):
    (x0, y0) = origin
    slide_to(x0 + 522, y0 + 439)
    click_at()
    slide_to(x0 + 278, y0 + 360)
    click_at()
    slide_to(x0 + 274, y0 + 288)
    click_at()
    
def start_game(save_number=0, debug=False):
    origin = find_screen(debug)
    if origin is None:
        raise Exception("Origin not found")
    (x0, y0) = origin
    click_at(x0, y0)
    slide_to(x0 + 250, y0 + 300)
    click_at(x0 + 250, y0 + 300)
    time.sleep(1)
    save_x = x0 + (105 + save_number * 195)
    save_y = y0 + 300
    slide_to(save_x, save_y)
    click_at()
    time.sleep(5)
    cursor_yes()
    cursor_no()
    quit_game(origin)
    
    
    
    
