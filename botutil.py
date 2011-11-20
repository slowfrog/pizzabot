# Written by Laurent Vaucher over a few days in January 2011
# with some low-level code borrowed from nibblerslitterbox
#
# The license is that you can do anything you want with the code, as long as you don't sue me
#
from __future__ import division, print_function

import math
import time
import sys
import win32api
import win32con
import Image
import ImageGrab

# First part with low level function to take screenshots and send 'synthetic' mouse events
def screenshot(x0, y0, x1, y1):
    """Take a screenshot of a part of the screen"""
    im = ImageGrab.grab((x0, y0, x1, y1))
    return im.load()

def save_screenshot(x0, y0, x1, y1, filename):
    """Take a screenshot of a part of the screen and save it to a file, mainly for debug"""
    im = screenshot(x0, y0, x1, y1)
    with open(filename, "wb") as outfile:
        im.save(outfile)

def load_opaque_png(filename):
    im = Image.open(filename)
    (w, h) = im.size
    return (im.convert("RGB").load(), w, h)
    
def move_to(x1, y1):
    """Moves the mouse pointer to a given position on screen"""
    win32api.SetCursorPos((x1, y1))
        
def slide_to(x1, y1, delta_t=1, step_t=0.05):
    """Gently slides the mouse pointer from its current position to a new destination"""
    count = int(math.floor(delta_t / step_t))
    count = 1 if count < 1 else count
    (x, y) = win32api.GetCursorPos()
    for i in xrange(count + 1):
        ratio = i / count
        xi = int(x + (x1 - x) * ratio)
        yi = int(y + (y1 - y) * ratio)
        win32api.SetCursorPos((xi, yi))
        time.sleep(step_t)

def click_at(x=None, y=None, delta_t=0.02):
    """Generates a click at a given position by sending a left-button down event, followed after a
    small delay by a left-button up event"""
    if ((x is not None) and (y is not None)):
        win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(delta_t)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)

def drag_drop(x0, y0, x1, y1, delta_t=0.1):
    """Does a drag and drop, which is essentially the same as a click, but with the mouse pointer
    changing position between the button-down and button-up event"""
    win32api.SetCursorPos((x0, y0))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(delta_t)
    win32api.SetCursorPos((x1, y1))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
    time.sleep(delta_t)

# Second part with some utility functions for things like image comparison
def rgb_dist((r0, g0, b0), (r1, g1, b1)):
    """Computes a color-distance between two RGB colors. Nothing fancy, just the sum of distances
    in R, G and B coordinates"""
    return abs(r0 - r1) + abs(g0 -g1) + abs(b0 - b1)

RGB_TOLERANCE = 6

def check_one_pixel(origin, x, y, color):
    """Checks that one pixel on screen has the expected value, accepting a little tolerance"""
    (x0, y0) = origin
    pix = screenshot(x0 + x, y0 + y, x0 + x + 1, y0 + y + 1)
    return rgb_dist(pix[0, 0], color) < RGB_TOLERANCE
    
def compare_images(im1, im2, w, h):
    """Compare two images and return an average distance over meaningful pixels. Meaningless pixels
    should be transparent, but they are in fact blue in the reference images, for easier handling"""
    count = 0
    dist = 0
    for x in xrange(w):
        for y in xrange(h):
            if (im1[x, y] != (0, 0, 255)):
                count += 1
                dist += rgb_dist(im1[x, y], im2[x, y])
    if count == 0:
        return 1000000
    else:
        return dist / count

LIGHT_GREEN = (90, 145, 62)
DARK_GREEN = (85, 137, 62)
RED = (255, 0, 0)
CYAN = (0, 255, 255)

def is_green_check(pix, x, y):
    """Verifies if a starting position matches the green checkerboard of the title page of
    the game"""
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
    """From the found position, slide to the top and left while still matching the 'green
    checkerboard' criterion"""
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
    """Function used when starting to find the offset of the game window. It tries to identify the
    green checkerboard at the top-left of the title screen."""
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


# Functions that test the current state of the game
def has_buttons(origin):
    """See if the top four button are available."""
    (x0, y0) = origin
    pix = screenshot(x0 + 400, y0, x0 + 600, y0 + 50)
    return ((rgb_dist(pix[24, 16], (105, 246, 0)) < RGB_TOLERANCE) and
            (rgb_dist(pix[67, 20], (255, 253, 98)) < RGB_TOLERANCE) and
            (rgb_dist(pix[115, 21], (255, 164, 32)) < RGB_TOLERANCE) and
            (rgb_dist(pix[164, 20], (44, 137, 255)) < RGB_TOLERANCE))

def can_take_order(origin):
    """Is a client waiting to order?"""
    return check_one_pixel(origin, 513, 386, (116, 254, 0))

def is_taking_order(origin):
    """Are we taking the order yet?"""
    return check_one_pixel(origin, 44, 157, (0, 88, 176))

def order_finished(origin):
    """Has the customer finished ordering?"""
    return check_one_pixel(origin, 80, 250, (114, 102, 97))

def order_gone(origin):
    """Is the order ticket gone from its main position"""
    return not check_one_pixel(origin, 522, 351, (255, 255, 254))

def shop_closed(origin):
    """Is the 'Closed' panel showing?"""
    return check_one_pixel(origin, 385, 431, (153, 0, 0))

def results_displayed(origin):
    """Are we seeing the results of the day?"""
    return check_one_pixel(origin, 236, 422, (30, 187, 65))
        
def ranks_displayed(origin):
    """Are the current tips and ranks displayed"""
    return (check_one_pixel(origin, 47, 420, (255, 254, 101)) and
            check_one_pixel(origin, 438, 418, (255, 255, 102)))
    
# Functions that do some simple actions
def quit_game(origin):
    """Exit the current game, possibly in the middle"""
    (x0, y0) = origin
    slide_to(x0 + 522, y0 + 439, 0.5)
    click_at() # Click on || pause ||
    slide_to(x0 + 278, y0 + 360, 0.5)
    click_at() # Then on Quit Game
    slide_to(x0 + 274, y0 + 288, 0.5)
    click_at() # And finally on Yes

def goto_order_station(gstate):
    if gstate["station"] != "order":
        (x0, y0) = gstate["origin"]
        click_at(x0 + 424, y0 + 29)
        gstate["station"] = "order"
        time.sleep(0.25)

def goto_topping_station(gstate):
    if gstate["station"] != "topping":
        (x0, y0) = gstate["origin"]
        click_at(x0 + 474, y0 + 29)
        gstate["station"] = "topping"
        time.sleep(0.25)
    
def goto_baking_station(gstate):
    if gstate["station"] != "baking":
        (x0, y0) = gstate["origin"]
        click_at(x0 + 522, y0 + 29)
        gstate["station"] = "baking"
        time.sleep(0.5)
    
def goto_cutting_station(gstate):
    if gstate["station"] != "cutting":
        (x0, y0) = gstate["origin"]
        click_at(x0 + 572, y0 + 29)
        gstate["station"] = "cutting"
        time.sleep(0.25)
    
def click_take_order(origin):
    (x0, y0) = origin
    click_at(x0 + 513, y0 + 386)

def click_save_for_later(origin):
    (x0, y0) = origin
    click_at(x0 + 521, y0 + 417)

    
# Functions that analyze one order
ORDER_ROW_Y = 166

def count_order_rows(origin):
    """Counts the number of ordered toppings"""
    row = 0
    while row < 7:
        y = ORDER_ROW_Y + 25 * row
        if not check_one_pixel(origin, 537, y, (102, 102, 102)):
            break
        row += 1
    return row

def check_quarters(origin, row):
    """See in which positions the toppinsg must go"""
    (x0, y0) = origin
    pix = screenshot(x0 + 468, y0 + 162 + row * 25, x0 + 476, y0 + 170 + row * 25)
    q1 = rgb_dist(pix[0, 0], (130, 130, 130)) < 90
    q2 = rgb_dist(pix[6, 0], (130, 130, 130)) < 90
    q3 = rgb_dist(pix[6, 6], (130, 130, 130)) < 90
    q4 = rgb_dist(pix[0, 6], (130, 130, 130)) < 90
    return (q1, q2, q3, q4)


def cutting_type(origin):
    """Counts the number of slices"""
    (x0, y0) = origin
    pix = screenshot(x0 + 544, y0 + 340, x0 + 550, y0 + 352)
    c4 = rgb_dist(pix[0, 11], (102, 102, 102)) < 20
    c6 = rgb_dist(pix[3, 2], (102, 102, 102)) < 20
    c8 = rgb_dist(pix[5, 0], (102, 102, 102)) < 20
    if c4:
        return 8 if c8 else 4
    elif c6:
        return 6
    else:
        # Should save image for debug
        raise Exception("Cutting type not found")

def baking_time(origin):
    """See how long it should be baked"""
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
    elif rgb_dist(pix[8, 13], (102, 102, 102)) < RGB_TOLERANCE:
        return 6
    else:
        # Should save image for debug
        raise Exception("Baking time not found")

def find_topping(origin, row):
    """Find which topping was ordered by comparing the image on screen with reference images"""
    (x0, y0) = origin
    pix = screenshot(x0 + 492, y0 + 154 + row * 25, x0 + 523, y0 + 179 + row * 25)
    mindist = None
    topping = None
    for t in TOPPING_IMAGES:
        (im, w, h) = TOPPING_IMAGES[t]
        d = compare_images(im, pix, w, h)
        if (mindist is None) or (d < mindist):
            mindist = d
            topping = t
    return topping
    
def find_count(origin, row):
    """Find the quantity of topping required by comparing the image of the number on screen with
    reference images"""
    (x0, y0) = origin
    pix = screenshot(x0 + 554, y0 + 154 + row * 25, x0 + 582, y0 + 179 + row * 25)
    mindist = None
    count = None
    for c in COUNT_IMAGES:
        (im, w, h) = COUNT_IMAGES[c]
        d = compare_images(im, pix, w, h)
        if (mindist is None) or (d < mindist):
            mindist = d
            count = c
    return count

def order_position(origin, index):
    """Utility function to know the position where the order should go on the top bar"""
    (x0, y0) = origin
    return (x0 + 32 + index * 35, y0 + 6)

def file_order(origin, index):
    """File the order, dragging it to its correct position"""
    (x0, y0) = origin
    (x1, y1) = order_position(origin, index)
    drag_drop(x0 + 537, y0 + 120, x1, y1)

def unfile_order(origin, index):
    """Unfile the order, dragging from its top position to the main position"""
    (x0, y0) = origin
    (x1, y1) = order_position(origin, index)
    drag_drop(x1, y1, x0 + 537, y0 + 120)

def quarter_string((q1, q2, q3, q4)):
    return "%s%s\n%s%s" % (("#" if q1 else "."), ("#" if q2 else "."),
                           ("#" if q4 else "."), ("#" if q3 else "."))

def print_order(o):
    for row in o["rows"]:
        print("%s    %d %s" % (quarter_string(row["quarters"]), row["count"], row["topping"]))
    print("Bake for %d, slice in %d" % (o["baketime"], o["slices"]))
    print("----------------------")

# order states: ordered, saved, baking, baked, cut, done
ORDER_ORDERED = "ordered"
ORDER_SAVED = "saved"
ORDER_BAKING = "baking"
ORDER_BAKED = "baked"
ORDER_CUT = "cut"
ORDER_DONE = "done"
    
def take_order(gstate, index):
    """That's where the whole ordering happens. Wait for the order to begin, to end, and analyze it
    with all previously defined functions. Returns a dictionary with all that needs to be said about
    what order."""
    origin = gstate["origin"]
    gstate["can_take_order"] = None
    click_take_order(origin)
    wait_for(lambda : is_taking_order(origin))
    wait_for(lambda : order_finished(origin))
    # analyze order
    rowcount = count_order_rows(origin)
    rows = []
    for row in xrange(rowcount):
        quarters = check_quarters(origin, row)
        topping = find_topping(origin, row)
        count = find_count(origin, row)
        rows += [ {"quarters": quarters, "topping": topping, "count": count}]
    slices = cutting_type(origin)
    baketime = baking_time(origin)
    file_order(origin, index)
    order = { "index": index,
              "rows": rows,
              "baketime": baketime,
              "slices": slices }
    change_state(order, ORDER_ORDERED)
    print_order(order)
    return order


# The following to are simple aliases, because the buttons for these actions always appear at the
# same position on screen. They only depend on the current "station"
click_make_pizza = click_take_order
click_into_oven = click_make_pizza    

# All known toppings and their positions in the "topping station"
TOPPINGS = {
    "salami": (40, 300),
    "meat": (75, 375),
    "mushrooms": (140, 400),
    "pepperoni": (215, 415),
    "onions": (300, 400),
    "olives": (360, 375),
    "anchovies": (400, 300)
    }

# Reference topping images loaded below
TOPPING_IMAGES = {}

# All known topping quantities
COUNTS = [2, 3, 4, 5, 6, 8, 12]

# Reference quantity images
COUNT_IMAGES = {}

def load_reference_images():
    """Load reference images for toppings and topping quantities."""
    for topping in TOPPINGS:
        filename = topping + ".png"
        (img, w, h) = load_opaque_png(filename)
        TOPPING_IMAGES[topping] = (img, w, h)
    for count in COUNTS:
        filename = "count%d.png" % count
        (img, w, h) = load_opaque_png(filename)
        COUNT_IMAGES[count] = (img, w, h)

def move_topping(origin, topping, to):
    (x0, y0) = origin
    (xt, yt) = TOPPINGS[topping]
    (x1, y1) = to
    drag_drop(x0 + xt, y0 + yt, x0 + x1, y0 + y1)

QUARTERS = [
    (30, 30),
    (60, 60),
    (80, 30),
    (30, 80),
    (45, 45)
    ]

SXY = [
    (-1, -1),
    (1, -1),
    (1, 1),
    (-1, 1)
    ]

def fill_quarter(origin, which, what, how_many):
    (sx, sy) = SXY[which]
    for h in xrange(how_many):
        (qx, qy) = QUARTERS[h]
        x1 = 220 + sx * qx
        y1 = 237 + sy * qy
        move_topping(origin, what, (x1, y1))

def free_oven_slot(gstate):
    for i in xrange(4):
        if gstate["oven"][i] is None:
            return i
    return -1
        

def change_state(order, state):
    order["state"] = state
    order["last_state_change"] = time.clock()

def put_order_in_oven(gstate, order):
    origin = gstate["origin"]
    oven_slot = free_oven_slot(gstate)
    click_into_oven(origin)
    order["oven_slot"] = oven_slot
    order["bake_start"] = time.clock()
    order["bake_end"] = order["bake_start"] + 22.5 * order["baketime"] - 0 # Small adjustemnt
    change_state(order, ORDER_BAKING)
    gstate["oven"][oven_slot] = order

def make_pizza(gstate, index):
    origin = gstate["origin"]
    order = gstate["orders"][index]
    goto_topping_station(gstate)
    unfile_order(origin, order["index"])
    click_make_pizza(origin)
    time.sleep(0.75)
    for row in order["rows"]:
        topping = row["topping"]
        count = row["count"]
        quarters = row["quarters"]
        qcount = sum(1 for q in quarters if q)
        tpq = int(count / qcount)
        qi = 0
        for q in quarters:
            if q:
                fill_quarter(origin, qi, topping, tpq)
            qi += 1
    oven_slot = free_oven_slot(gstate)
    if oven_slot >= 0:
        print("Direct into oven #%d" % (1 + index))
        put_order_in_oven(gstate, order)
    else:
        print("Save for later #%d" % (1 + index))
        click_save_for_later(origin)
        change_state(order, ORDER_SAVED)
        
    file_order(origin, index)

def bake_saved_pizza(gstate, index):
    origin = gstate["origin"]
    order = gstate["orders"][index]
    goto_topping_station(gstate)
    unfile_order(origin, index)
    time.sleep(0.5)
    click_make_pizza(origin)
    time.sleep(0.75)
    oven_slot = free_oven_slot(gstate)
    put_order_in_oven(gstate, order)
    file_order(origin, index)
        
BAKING_POSITION = [
    (140, 190),
    (300, 190),
    (140, 360),
    (300, 360)
    ]
    
def out_of_oven(gstate, index):
    (x0, y0) = origin = gstate["origin"]
    order = gstate["orders"][index]
    which = order["oven_slot"]
    goto_baking_station(gstate)
    (bx, by) = BAKING_POSITION[which]
    click_at(x0 + bx, y0 + by)
    time.sleep(1)
    gstate["oven"][which] = None
    order["oven_slot"] = None
    change_state(order, ORDER_BAKED)
    gstate["cutting"].append(order)

CUTS = {
    4: [(220, 100, 220, 450),
        (50, 270, 400, 270)],
    6: [(220, 100, 220, 450),
        (81, 190, 358, 350),
        (81, 350, 358, 190)],
    8: [(220, 100, 220, 450),
        (50, 270, 400, 270),
        (60, 110, 380, 430),
        (60, 430, 380, 110)]
    }

def cut_in(origin, slices):
    (x0, y0) = origin
    cuts = CUTS[slices]
    for cut in cuts:
        (x1, y1, x2, y2) = cut
        drag_drop(x0 + x1, y0 + y1, x0 + x2, y0 + y2)
    
def click_finish_order(origin):
    (x0, y0) = origin
    click_at(x0 + 513, y0 + 386)

def next_order_ready(gstate):
    ret = None
    now = time.clock()
    min_time = None
    for order in gstate["oven"]:
        if order is not None:
            if min_time is None or (order["bake_end"] - now < min_time):
                min_time = order["bake_end"] - now
                ret = (order, min_time)
    return ret

def order_baked(order):
    return time.clock() > order["bake_end"]

def finish_order(gstate, index):
    origin = gstate["origin"]
    goto_cutting_station(gstate)
    order = gstate["orders"][index]
    if len(gstate["cutting"]) == 0 or gstate["cutting"][0] != order:
        raise Exception("Cannot cut order %d" % index)
    unfile_order(origin, index)
    cut_in(origin, order["slices"])
    change_state(order, ORDER_CUT)
    click_finish_order(origin)
    wait_for(lambda : order_gone(origin))
    gstate["cutting"] = gstate["cutting"][1:]
    change_state(order, ORDER_DONE)
    time.sleep(0.25)
    
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
        print("Waiting failed: timeout")
        raise Exception("Waiting failed ****** %s" % f)
    #else:
    #    print("Ok after %d rounds" % round)

def waiting_priority(order):
    return (time.clock() - order["last_state_change"]) / 15
        
def what_can_do(gstate):
    actions = []
    origin = gstate["origin"]
    now = time.clock()
    
    goto_order_station(gstate)
    if len(gstate["cutting"]) > 0:
        order = gstate["cutting"][0]
        actions.append(("cut", order, 4 + waiting_priority(order)))

    for order in gstate["orders"]:
        if order["state"] == ORDER_ORDERED:
            actions.append(("make", order, 4 + (order["baketime"] / 2) + waiting_priority(order)))
        elif order["state"] == ORDER_SAVED and free_oven_slot(gstate) >= 0:
            actions.append(("oven", order, 6 + waiting_priority(order)))

    # Detect shop closing/can take order
    if gstate["closed"] != "closed":
        if gstate["closed"] is None:
            if shop_closed(origin):
                gstate["closed"] = now
        elif now > gstate["closed"] + 10:
            gstate["closed"] = "closed"

    if can_take_order(origin):
        if not "can_take_order" in gstate or gstate["can_take_order"] is None:
            gstate["can_take_order"] = now
            actions.append(("take_order", None, 4))
        else:
            actions.append(("take_order", None, 4 + (now - gstate["can_take_order"]) / 3))

    return actions

def play_best_action(gstate, actions):
    origin = gstate["origin"]
    actions.sort(key=(lambda action: action[2]), reverse=True)
    (action, order, _) = actions[0]
    if action == "take_order":
        print("Taking order #%d" % (1 + len(gstate["orders"])))
        order = take_order(gstate, len(gstate["orders"]))
        gstate["orders"].append(order)
    elif action == "make":
        print("Making pizza #%d" % (1 + order["index"]))
        make_pizza(gstate, order["index"])
    elif action == "oven":
        print("Into oven #%d" % (1 + order["index"]))
        bake_saved_pizza(gstate, order["index"])
    elif action == "cut":
        print("Cutting and serving #%d" % (1 + order["index"]))
        finish_order(gstate, order["index"])
        
def one_round(origin):
    gstate = {
        "origin": origin,
        "oven": [ None, None, None, None ],
        "cutting": [],
        "orders": [],
        "closed": None,
        "station": None
        }
    while True:
        actions = what_can_do(gstate)
        ready = next_order_ready(gstate)
        if ready is not None:
            (order, time_left) = ready
        else:
            time_left = 100
        if time_left < 7:
            goto_baking_station(gstate)
            print("Out of oven #%d" % (1 + order["index"]))
            wait_for(lambda: order_baked(order))
            out_of_oven(gstate, order["index"])
        elif len(actions) > 0:
            play_best_action(gstate, actions)
        
        if gstate["closed"] == "closed" and len(actions) == 0 and ready is None:
            break;

def pass_results(origin):
    (x0, y0) = origin
    wait_for(lambda: results_displayed(origin))
    print("Will pass results in 5 seconds")
    time.sleep(5)
    click_at(x0 + 236, y0 + 422)

def pass_rank_quit(origin):
    (x0, y0) = origin
    wait_for(lambda: ranks_displayed(origin))
    print("Will pass ranks quitting in 5 seconds")
    time.sleep(5)
    click_at(x0 + 47, y0 + 420)
    
def pass_rank_continue(origin):
    (x0, y0) = origin
    wait_for(lambda: ranks_displayed(origin))
    print("Will pass ranks continuing in 5 seconds")
    time.sleep(5)
    click_at(x0 + 438, y0 + 418)


def do_rounds(origin, count):
    f_has_buttons = originate(has_buttons, origin)
    for r in xrange(count):
        try:
            print("##################################")
            print(" Playing round %d/%d" % (r + 1, count))
            print("##################################")
            wait_for(f_has_buttons)
            one_round(origin)
            pass_results(origin)
            if r < count - 1:
                pass_rank_continue(origin)
            else:
                pass_rank_quit(origin)
        except Exception, e:
            print("@*@*!@#!*@!#*@#*@!#*@*************************************!!!!!!!")
            print("ERROR %s" % e)
            print("Aborting game in 10 seconds")
            time.sleep(10)
            quit_game(origin)
            
        
def start_game(save_number=2, rounds=1, debug=False):
    load_reference_images()
    origin = find_screen(debug)
    print("Origin: (%d, %d)" % origin)
    f_can_take_order = originate(can_take_order, origin)
    f_order_finished = originate(order_finished, origin)
    f_order_gone = originate(order_gone, origin)
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
    
    do_rounds(origin, rounds)
    
    
def main():
    save_number = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    start_game(save_number, rounds)

if __name__ == "__main__":
    main()
