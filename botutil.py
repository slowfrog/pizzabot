from __future__ import division, print_function

import ImageGrab

def screenshot(x0, y0, x1, y1):
    im = ImageGrab.grab((x0, y0, x1, y1))
    return im

def save_screenshot(x0, y0, x1, y1, filename):
    im = screenshot(x0, y0, x1, y1)
    with open(filename, "wb") as outfile:
        im.save(outfile)

