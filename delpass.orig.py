import time
import math
from enum import Enum

import _rpi_ws281x as ws
from PIL import Image, ImageDraw, ImageFont
from colorsys import hls_to_rgb

# Some predefined
FIXED_COLOR    = 0x200000
DISPLAY_WIDTH  = 150
DISPLAY_HEIGHT = 7
FONT           = "data/font/minimal5x7.ttf"
FONT_SIZE      = 16

# Display area
TEXT_AREA_START = 0
TEXT_AREA_END   = 150
TEXT_AREA_WIDTH = TEXT_AREA_END - TEXT_AREA_START

# LED configuration.
LED_CHANNEL = 0
LED_COUNT = DISPLAY_WIDTH * DISPLAY_HEIGHT  # How many LEDs to light.
LED_FREQ_HZ = 800000                        # Frequency of the LED signal.  Should be 800khz or 400khz.
LED_DMA_NUM = 10                            # DMA channel to use, can be 0-14.
LED_GPIO = 18                               # GPIO connected to the LED signal line.  Must support PWM!
LED_BRIGHTNESS = 255                        # Set to 0 for darkest and 255 for brightest
LED_INVERT = 0                              # Set to 1 to invert the LED signal, good if using NPN
                                            # transistor as a 3.3V->5V level converter.  Keep at 0
                                            # for a normal/non-inverted signal.

# Minimum delay between each call to render in order to not have race condition on writtting data
# About 1ms per 100 bytes for 800kHz
RENDER_TIME_S = 0.001 * ((LED_COUNT * 3 // 100) + 1)

# Define colors which will be used by the example.  Each color is an unsigned
# 32-bit value where the lower 24 bits define the red, green, blue data (each
# being 8 bits long).
DOT_COLORS = [0xFF0000,   # red
              0xFF7F00,   # orange
              0xFFFF00,   # yellow
              0x00FF00,   # green
              0x00FFFF,   # lightblue
              0x0000FF,   # blue
              0x7F007F,   # purple
              0xFF007F]   # pink

# Devide text area into chunk to change color
COLOR_CHUNK = math.ceil(TEXT_AREA_WIDTH / len(DOT_COLORS))

# Possible color mode
class ColorMode(Enum):
    SPECTRUM = 1
    FIXED = 2

# Possible color intensity
class ColorIntensity(Enum):
    VARYING = 1
    FIXED = 2

# Current color mode
COLOR_MODE = ColorMode.FIXED
# Current color intensity
COLOR_INTENSITY = ColorIntensity.FIXED

# Create a ws2811_t structure from the LED configuration.
# Note that this structure will be created on the heap so you need to be careful
# that you delete its memory by calling delete_ws2811_t when it's not needed.
leds = ws.new_ws2811_t()

# Initialize all channels to off
for channum in range(2):
    channel = ws.ws2811_channel_get(leds, channum)
    ws.ws2811_channel_t_count_set(channel, 0)
    ws.ws2811_channel_t_gpionum_set(channel, 0)
    ws.ws2811_channel_t_invert_set(channel, 0)
    ws.ws2811_channel_t_brightness_set(channel, 0)

channel = ws.ws2811_channel_get(leds, LED_CHANNEL)

ws.ws2811_channel_t_count_set(channel, LED_COUNT)
ws.ws2811_channel_t_gpionum_set(channel, LED_GPIO)
ws.ws2811_channel_t_invert_set(channel, LED_INVERT)
ws.ws2811_channel_t_brightness_set(channel, LED_BRIGHTNESS)

ws.ws2811_t_freq_set(leds, LED_FREQ_HZ)
ws.ws2811_t_dmanum_set(leds, LED_DMA_NUM)

# Initialize library with LED configuration.
resp = ws.ws2811_init(leds)
if resp != ws.WS2811_SUCCESS:
    message = ws.ws2811_get_return_t_str(resp)
    raise RuntimeError('ws2811_init failed with code {0} ({1})'.format(resp, message))

# Load font
font = ImageFont.truetype(FONT, FONT_SIZE)

# Create image for Space invader
imageSpaceInvaderUp   = Image.open("data/images/SpaceInvaderUP.png",   mode='r', formats=None)
imageSpaceInvaderDown = Image.open("data/images/SpaceInvaderDOWN.png", mode='r', formats=None)

# Create image for Light
imageLight = Image.open("data/images/Light.png",   mode='r', formats=None)

def generateTextImage(text):

    # Measure the size of our text
    text_width, text_height = font.getsize(text)
    print(f"Text width will be {text_width}x{text_height} pixels")

    # Create a new PIL image size of the text   
    image = Image.new('L', (text_width, text_height), 0)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font, fill=255, stroke_width=0, stroke_fill=255)

    return image

def rainbow_color_generate(n=150, end=1):
    rgb = [ hls_to_rgb(end * i /(n-1), 0.5, 1) for i in range(n) ] 
    rgbi = [] 
    for c in rgb:
       rgbi.append((int(c[1] * 255) << 16) + (int(c[0] * 255) << 8) + int(c[2] * 255))
    return rgbi

RAINBOW_COLOR = rainbow_color_generate()

def getColorBrightness(c, loop):
    speed = 5
    l = (loop * speed) % 255 # From 0 to 255)
    p = l / 255

    if p > 0.5:
        p = (1 - p) * 2
    else:
        p = p * 2

    if p < 0.02:
        p = 0.02

    G = (c >> 16) & 0xFF
    R = (c >> 8) & 0xFF
    B = (c >> 0) & 0xFF

    G *= p
    R *= p
    B *= p

    return (int(G) << 16) + (int(R) << 8) + int(B)

def getColor(x, loop):
    if COLOR_MODE == ColorMode.SPECTRUM:
        c = RAINBOW_COLOR[x]
    # elif COLOR_MODE == ColorMode.PALET:
    #     c = DOT_COLORS[int((x - TEXT_AREA_START) / COLOR_CHUNK)]
    else:
        c = FIXED_COLOR

    if COLOR_INTENSITY == ColorIntensity.FIXED:
        return c
    else:
        return getColorBrightness(c, loop)


def getStripPixelIndex(x, y):
    if y % 2 == 0:
        return x + y * DISPLAY_WIDTH
    else:
        return y * DISPLAY_WIDTH + (DISPLAY_WIDTH - x - 1)
    
def calibrate_fps():
    print(f"Estimated render time is {RENDER_TIME_S:.4f} seconds which is {(1 / RENDER_TIME_S):.2f}fps")
    print("Calibrate render time...")
          
    # Warmup
    for i in range(10):
        ws.ws2811_render(leds)

    # Compute
    cal_start_time_s = time.monotonic()
    for i in range(10):
        ws.ws2811_render(leds)
    cal_stop_time_s = time.monotonic()

    # Store result
    CALIBRATED_RENDER_TIME_S = (cal_stop_time_s - cal_start_time_s) / 10

    # Display result
    print(f"Calibrated render time is {CALIBRATED_RENDER_TIME_S:.4f} seconds which is {(1 / CALIBRATED_RENDER_TIME_S):.2f}fps")

def display_image(img1, img2=None, space=None, repeat_count=1, end_wait=0, scroll=True):
    offset_x = 0
    end_time = None
    last_render_time_s = time.monotonic()
    loop = 0
    img = img1 if img2 is None else img2

    if not scroll:
        offset_x = TEXT_AREA_WIDTH
        if img1.size[0] < TEXT_AREA_WIDTH:
            offset_x -= (TEXT_AREA_WIDTH - img1.size[0]) / 2

    while True:

        # Change image
        if img2 is not None and loop % 6 == 0:
            img = img1 if img != img1 else img2

        # Loop over all the text area
        for x in range(TEXT_AREA_START, TEXT_AREA_END):
            for y in range(DISPLAY_HEIGHT):
                if space is not None:
                    iw = max(min(img.size[0], offset_x), 0)
                    ix = x - (TEXT_AREA_END - offset_x)
                    if ix >= 0:
                        ix %= img.size[0] + space
                else:
                    iw = max(min(img.size[0], offset_x), 0)
                    ix = x - (TEXT_AREA_END - offset_x)
                    
                if ix >= 0 and ix < iw and img.getpixel((ix, y)) == 255:
                    ws.ws2811_led_set(channel, getStripPixelIndex(x,y), getColor(x, loop))     
                else:
                    ws.ws2811_led_set(channel, getStripPixelIndex(x,y), 0x000000)                            

        # Draw it
        resp = ws.ws2811_render(leds)
        if resp != ws.WS2811_SUCCESS:
            message = ws.ws2811_get_return_t_str(resp)
            raise RuntimeError('ws2811_render failed with code {0} ({1})'.format(resp, message))
        
        stop = offset_x >= DISPLAY_WIDTH + img.size[0]
        stop |= repeat_count <= 1 and end_wait != 0 and offset_x >= DISPLAY_WIDTH
        stop |= not scroll
        stop &= offset_x >= img.size[0]
        if stop:
            if repeat_count > 1:
                repeat_count -= 1
                offset_x = 0
            elif end_wait != 0:
                if end_time is None:
                    end_time = time.monotonic() + end_wait

                if time.monotonic() >= end_time:
                    break
            else:
                break
        else:
            offset_x += 1
        
        render_time_s = time.monotonic()
        elapsed_render_time_s = render_time_s - last_render_time_s
        last_render_time_s = render_time_s
        if loop % 30 == 0 :
            print(f"Render at {(1 / elapsed_render_time_s):.2f}fps")

        # We should wait to render otherwise it seem strange behavior can arrive      
        time.sleep(RENDER_TIME_S)

        loop += 1

def display_text(text, repeat_count=1, end_wait=0, scroll=False):

    imgText = generateTextImage(text)
    #imgText.save("text.png", "PNG")
    display_image(imgText, repeat_count=repeat_count, end_wait=end_wait, scroll=scroll)

# Wrap following code in a try/finally to ensure cleanup functions are called
# after library is initialized.
try:

    calibrate_fps()

    while True:
        for color_mode in ColorMode:
            for color_intensity in ColorIntensity:
                COLOR_MODE = color_mode
                COLOR_INTENSITY = color_intensity

                text_end_wait = 5 if color_mode == ColorMode.FIXED else 0
                text_scroll = True if color_mode != ColorMode.FIXED else False
                display_text("ALIEN EXIST", end_wait=text_end_wait, scroll=text_scroll)
                display_image(imageLight, space=5, repeat_count=1, end_wait=3)
                display_text("ALIEN ARE EVERYWHERE", end_wait=text_end_wait, scroll=text_scroll)
                display_image(imageSpaceInvaderDown, imageSpaceInvaderUp, space=10, end_wait=3)
                display_text("PELPASS FESTIVAL", end_wait=text_end_wait, scroll=text_scroll)

finally:
    # Ensure ws2811_fini is called before the program quits.
    ws.ws2811_fini(leds)
    # Example of calling delete function to clean up structure memory.  Isn't
    # strictly necessary at the end of the program execution here, but is good practice.
    ws.delete_ws2811_t(leds)
