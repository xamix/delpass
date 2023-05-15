from tools import log
import time
import math
from enum import Enum
import atexit

from PIL import Image, ImageDraw, ImageFont
from colorsys import hls_to_rgb

# Make it working on other target in order to develop more easyly
try:
    import _rpi_ws281x as ws
except:
    import ws281x_fake as ws

# Some predefined
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

# Minimum delay between each call to render in order to not have race condition on writting data
# About 1ms per 100 bytes for 800kHz
RENDER_TIME_S = 0.001 * ((LED_COUNT * 3 // 100) + 1)

# Possible color mode
class ColorMode(Enum):
    FIXED = 1
    SPECTRUM = 2

# Possible color intensity
class ColorIntensity(Enum):
    FIXED = 1
    SPACIAL = 2
    TEMPORAL = 3

# Class used to control the leds
class Leds():

    # Singleton
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.log = log.Log(__name__)
            cls.instance = super().__new__(cls)
            cls._init(cls)
        return cls.instance

    def _init(self):

        self.running = False

        # Create a ws2811_t structure from the LED configuration.
        # Note that this structure will be created on the heap so you need to be careful
        # that you delete its memory by calling delete_ws2811_t when it's not needed anymore.
        self.leds = ws.new_ws2811_t()

        # Destroy created leds
        atexit.register(lambda: self._deinit(self))

        # Initialize all channels to off
        for channum in range(2):
            channel = ws.ws2811_channel_get(self.leds, channum)
            ws.ws2811_channel_t_count_set(channel, 0)
            ws.ws2811_channel_t_gpionum_set(channel, 0)
            ws.ws2811_channel_t_invert_set(channel, 0)
            ws.ws2811_channel_t_brightness_set(channel, 0)

        self.channel = ws.ws2811_channel_get(self.leds, LED_CHANNEL)

        ws.ws2811_channel_t_count_set(self.channel, LED_COUNT)
        ws.ws2811_channel_t_gpionum_set(self.channel, LED_GPIO)
        ws.ws2811_channel_t_invert_set(self.channel, LED_INVERT)
        ws.ws2811_channel_t_brightness_set(self.channel, LED_BRIGHTNESS)

        ws.ws2811_t_freq_set(self.leds, LED_FREQ_HZ)
        ws.ws2811_t_dmanum_set(self.leds, LED_DMA_NUM)

        # Initialize library with LED configuration.
        resp = ws.ws2811_init(self.leds)
        if resp != ws.WS2811_SUCCESS:
            message = ws.ws2811_get_return_t_str(resp)
            raise RuntimeError('ws2811_init failed with code {0} ({1})'.format(resp, message))

        # Load font
        self.font = ImageFont.truetype(FONT, FONT_SIZE)

        # Create Rainbow color and defult fixed color
        self.SPECTRUM_COLORS = self._generate_spectrum_colors()
        self.FIXED_COLOR = 0x200000

        # Current color mode
        self.color_mode = ColorMode.FIXED
        # Current color intensity
        self.color_intensity = ColorIntensity.FIXED

    def _deinit(self):
        # Ensure ws2811_fini is called before the program quits.
        ws.ws2811_fini(self.leds)
        # Example of calling delete function to clean up structure memory.  Isn't
        # strictly necessary at the end of the program execution here, but is good practice.
        ws.delete_ws2811_t(self.leds)

    # Generate an image from text
    def _get_text_as_image(self, text, fill):

        # Measure the size of our text
        text_width, text_height = self.font.getsize(text)
        x_offset = 0

        # Create a new PIL image size of the text  
        if fill and text_width < TEXT_AREA_WIDTH:
            x_offset = (TEXT_AREA_WIDTH - text_width) / 2
            image_w = TEXT_AREA_WIDTH
        else:
            x_offset = 0
            image_w = text_width
        
        image = Image.new('L', (image_w, text_height), 0)
        draw = ImageDraw.Draw(image)
        draw.text((x_offset, 0), text, font=self.font, fill=255, stroke_width=0, stroke_fill=255)

        return image

    def _generate_spectrum_colors(n=150, end=1):
        rgb = [ hls_to_rgb(end * i /(n-1), 0.5, 1) for i in range(n) ] 
        rgbi = [] 
        for c in rgb:
            rgbi.append((int(c[1] * 255) << 16) + (int(c[0] * 255) << 8) + int(c[2] * 255))
        return rgbi
    
    def _change_luminosity(self, c, factor):
        G = ((c >> 16) & 0xFF)
        R = ((c >> 8) & 0xFF)
        B = ((c >> 0) & 0xFF)

        G *= factor
        R *= factor
        B *= factor

        if R > 255:
            R = 255
        elif R < 0:
            R = 0

        if G > 255:
            G = 255
        elif G < 0:
            G = 0

        if B > 255:
            B = 255
        elif B < 0:
            B = 0

        color = (int(G) << 16) + (int(R) << 8) + int(B)

        return color
    
    def _get_color_brightness_temporal(self, c, loop):
        speed = 5
        l = (loop * speed) % 255 # From 0 to 255)
        factor = l / 255

        if factor > 0.5:
            factor = (1 - factor) * 2
        else:
            factor = factor * 2

        if factor < 0.02:
            factor = 0.02

        return self._change_luminosity(c, factor)
    
    def _get_color_brightness_spacial(self, c, x):
        # From 0 to Pi
        factor = x * math.pi / DISPLAY_WIDTH

        if factor < 0.02:
            factor = 0.02
        
        return self._change_luminosity(c, factor)

    def _get_color(self, x, loop):
        if self.color_mode == ColorMode.SPECTRUM:
            c = self.SPECTRUM_COLORS[x]
        else:
            c = self.FIXED_COLOR

        if self.color_intensity == ColorIntensity.TEMPORAL:
            return self._get_color_brightness_temporal(c, loop)
        if self.color_intensity == ColorIntensity.SPACIAL:
            return self._get_color_brightness_spacial(c, x)
        else:
            return c


    def _get_strip_pixel_index(self, x, y):
        if y % 2 == 0:
            return x + y * DISPLAY_WIDTH
        else:
            return y * DISPLAY_WIDTH + (DISPLAY_WIDTH - x - 1)

    def set_color_params(self, color_mode, color_intensity, color=None):
        if color:
            self.FIXED_COLOR = color

        self.color_mode = color_mode
        self.color_intensity = color_intensity

      
    def display_image(self, img1, img2=None, space=None, repeat_count=1, duration=0, end_wait=0, scroll=True):
        self.running_set(True)
        offset_x = 0
        end_time = None if duration <= 0 else time.monotonic() + duration
        last_render_time_s = time.monotonic()
        loop = 0
        img = img1 if img2 is None else img2

        if not scroll:
            offset_x = TEXT_AREA_WIDTH
            if img1.size[0] < TEXT_AREA_WIDTH:
                offset_x -= (TEXT_AREA_WIDTH - img1.size[0]) / 2

        while self.running:

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
                        ws.ws2811_led_set(self.channel, self._get_strip_pixel_index(x,y), self._get_color(x, loop))     
                    else:
                        ws.ws2811_led_set(self.channel, self._get_strip_pixel_index(x,y), 0x000000)                            

            # Draw it
            resp = ws.ws2811_render(self.leds)
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
                elif end_wait != 0 or duration != 0:
                    if duration != 0 and time.monotonic() + 5 < end_time:
                        repeat_count = 2
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
            if loop % 30 == 0 and elapsed_render_time_s > 0:
                self.log.inf(f"Render at {(1 / elapsed_render_time_s):.2f}fps")

            # We should wait to render otherwise it seem strange behavior can arrive      
            time.sleep(RENDER_TIME_S)

            loop += 1

        self.running_set(False)

    def display_text(self, text, repeat_count=1, duration=0, end_wait=0, scroll=True):

        imgText = self._get_text_as_image(text, fill = not scroll)
        self.display_image(imgText, repeat_count=repeat_count, duration=duration, end_wait=end_wait, scroll=scroll)

    def running_set(self, state):
        self.running = state
