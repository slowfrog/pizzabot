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

def drag_drop(x0, y0, x1, y1, delta_t=0.1):
    win32api.SetCursorPos((x0, y0))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(delta_t)
    win32api.SetCursorPos((x1, y1))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    time.sleep(delta_t)
    
def slide_to(x1, y1, delta_t=1, step_t=0.05):
    count = int(math.floor(delta_t / step_t))
    count = 1 if count < 1 else count
    (x, y) = win32api.GetCursorPos()
    for i in xrange(count + 1):
        ratio = i / count
        xi = int(x + (x1 - x) * ratio)
        yi = int(y + (y1 - y) * ratio)
        win32api.SetCursorPos((xi, yi))
        time.sleep(step_t)

def move_to(x1, y1):
    win32api.SetCursorPos((x1, y1))
        
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
    slide_to(x0 + 522, y0 + 439, 0.5)
    click_at()
    slide_to(x0 + 278, y0 + 360, 0.5)
    click_at()
    slide_to(x0 + 274, y0 + 288, 0.5)
    click_at()

def has_buttons(origin):
    (x0, y0) = origin
    pix = screenshot(x0 + 400, y0, x0 + 600, y0 + 50)
    return ((rgb_dist(pix[24, 16], (105, 246, 0)) < RGB_TOLERANCE) and
            (rgb_dist(pix[67, 20], (255, 253, 98)) < RGB_TOLERANCE) and
            (rgb_dist(pix[115, 21], (255, 164, 32)) < RGB_TOLERANCE) and
            (rgb_dist(pix[164, 20], (44, 137, 255)) < RGB_TOLERANCE))

def goto_order_station(origin):
    (x0, y0) = origin
    click_at(x0 + 424, y0 + 29)
    time.sleep(0.25)

def goto_topping_station(origin):
    (x0, y0) = origin
    click_at(x0 + 474, y0 + 29)
    time.sleep(0.25)
    
def goto_baking_station(origin):
    (x0, y0) = origin
    click_at(x0 + 522, y0 + 29)
    time.sleep(0.25)
    
def goto_cutting_station(origin):
    (x0, y0) = origin
    click_at(x0 + 572, y0 + 29)
    time.sleep(0.25)
    
def check_one_pixel(origin, x, y, color):
    (x0, y0) = origin
    pix = screenshot(x0 + x, y0 + y, x0 + x + 1, y0 + y + 1)
    #print(pix[0, 0])
    return rgb_dist(pix[0, 0], color) < RGB_TOLERANCE
    
def can_take_order(origin):
    return check_one_pixel(origin, 513, 386, (116, 254, 0))

def is_taking_order(origin):
    return check_one_pixel(origin, 44, 157, (0, 88, 176))

def order_finished(origin):
    return check_one_pixel(origin, 80, 250, (114, 102, 97))

def click_take_order(origin):
    (x0, y0) = origin
    click_at(x0 + 513, y0 + 386)

ORDER_ROW_Y = 166

def count_order_rows(origin):
    row = 0
    while row < 7:
        y = ORDER_ROW_Y + 25 * row
        if not check_one_pixel(origin, 537, y, (102, 102, 102)):
            break
        row += 1
    return row

def check_quarters(origin, row):
    (x0, y0) = origin
    pix = screenshot(x0 + 468, y0 + 162 + row * 25, x0 + 476, y0 + 170 + row * 25)
    d1 = rgb_dist(pix[0, 0], (130, 130, 130))
    d2 = rgb_dist(pix[6, 0], (130, 130, 130))
    d3 = rgb_dist(pix[6, 6], (130, 130, 130))
    d4 = rgb_dist(pix[0, 6], (130, 130, 130))
    q1 = rgb_dist(pix[0, 0], (130, 130, 130)) < 90
    q2 = rgb_dist(pix[6, 0], (130, 130, 130)) < 90
    q3 = rgb_dist(pix[6, 6], (130, 130, 130)) < 90
    q4 = rgb_dist(pix[0, 6], (130, 130, 130)) < 90
    print("row %d: %s %s %s %s [%d %d %d %d]" % (row, q1, q2, q3, q4, d1, d2, d3, d4))

def cutting_type(origin):
    (x0, y0) = origin
    pix = screenshot(x0 + 544, y0 + 340, x0 + 550, y0 + 352)
    c4 = rgb_dist(pix[0, 11], (102, 102, 102)) < 20
    c6 = rgb_dist(pix[3, 2], (102, 102, 102)) < 20
    c8 = rgb_dist(pix[5, 0], (102, 102, 102)) < 20
    if c4:
        return 8 if c8 else 4
    else:
        return 6 if c6 else 0

def baking_time(origin):
    (x0, y0) = origin
    pix = screenshot(x0 + 470, y0 + 340, x0 + 500, y0 + 370)
    if rgb_dist(pix[25, 4], (111, 111, 111)) < RGB_TOLERANCE:
        return 1
    elif rgb_dist(pix[28, 13], (102, 102, 102)) < RGB_TOLERANCE:
        return 2
    elif rgb_dist(pix[24, 21], (111, 111, 111)) < RGB_TOLERANCE:
        return 3
    elif rgb_dist(pix[18, 24], (102, 102, 102)) < RGB_TOLERANCE:
        return 4
    elif rgb_dist(pix[11, 21], (102, 102, 102)) < RGB_TOLERANCE:
        return 5
    else:
        return 0

def order_position(origin, index):
    (x0, y0) = origin
    return (x0 + 32 + index * 35, y0 + 6)

def file_order(origin, index):
    (x0, y0) = origin
    (x1, y1) = order_position(origin, index)
    drag_drop(x0 + 537, y0 + 120, x1, y1)

def unfile_order(origin, index):
    (x0, y0) = origin
    (x1, y1) = order_position(origin, index)
    drag_drop(x1, y1, x0 + 537, y0 + 120)
    
    
def take_order(origin, index=0):
    click_take_order(origin)
    wait_for(lambda : is_taking_order(origin))
    wait_for(lambda : order_finished(origin))
    # analyze order
    rows = count_order_rows(origin)
    print("Order has %d rows" % rows)
    for row in xrange(rows):
        check_quarters(origin, row)
    slices = cutting_type(origin)
    baketime = baking_time(origin)
    file_order(origin, index)
    print("Bake for %d, cut in %d, " % (baketime, slices))
    

click_make_pizza = click_take_order
click_into_oven = click_make_pizza    
    
TOPPINGS = {
    "salami": (40, 300),
    "meat": (75, 375),
    "mushrooms": (140, 400),
    "pepperoni": (215, 415),
    "onions": (300, 400),
    "olives": (360, 375),
    "anchovies": (400, 300)
    }

def move_topping(origin, topping, to):
    (x0, y0) = origin
    (xt, yt) = TOPPINGS[topping]
    (x1, y1) = to
    drag_drop(x0 + xt, y0 + yt, x0 + x1, y0 + y1)

def test_topping(origin):
    move_topping(origin, "anchovies", (230, 250))
    move_topping(origin, "olives", (230, 220))
    move_topping(origin, "onions", (300, 250))
    move_topping(origin, "pepperoni", (300, 140))
    move_topping(origin, "mushrooms", (120, 250))
    move_topping(origin, "meat", (120, 300))
    move_topping(origin, "salami", (180, 150))

def make_pizza(origin):
    click_make_pizza(origin)
    time.sleep(1)
    test_topping(origin)
    click_into_oven(origin)
    
def originate(f, origin):
    return lambda : f(origin)

def wait_for(f, period=0.5, timeout=30):
    start_time = time.clock()
    timeout_elapsed = timeout < 0
    round = 0
    while not (f() or timeout_elapsed):
        round += 1
        time.sleep(period)
        timeout_elapsed = ((time.clock() - start_time) > timeout > 0)
    if timeout_elapsed:
        print("Sorry")
    else:
        print("Ok after %d rounds" % round)
    
def start_game(save_number=2, debug=False):
    origin = find_screen(debug)
    f_has_buttons = originate(has_buttons, origin)
    f_can_take_order = originate(can_take_order, origin)
    f_order_finished = originate(order_finished, origin)
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
    wait_for(f_has_buttons)
    order_index = 0
    for cust in xrange(10):
        wait_for(f_can_take_order)
        take_order(origin, order_index)
        order_index += 1
    goto_topping_station(origin)
    unfile_order(origin, 3)
    make_pizza(origin)
    time.sleep(2)
    quit_game(origin)
    
    
    
    
