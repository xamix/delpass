import pylrc
import sys
import vlc
import signal

import _rpi_ws281x as ws
from PIL import Image, ImageDraw, ImageFont
import math

# Some predefined
TEXT = "PELPASS FESTIVAL"
TEXT_COLOR_FG  = (255,255,255)
TEXT_COLOR_BG  = (0,0,0)
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

# Define colors which will be used by the example.  Each color is an unsigned
# 32-bit value where the lower 24 bits define the red, green, blue data (each
# being 8 bits long).
DOT_COLORS = [0x200000,   # red
              0x201000,   # orange
              0x202000,   # yellow
              0x002000,   # green
              0x002020,   # lightblue
              0x000020,   # blue
              0x100010,   # purple
              0x200010]  # pink

# Devide text area into chunk to change color
COLOR_CHUNK = math.ceil(TEXT_AREA_WIDTH / len(DOT_COLORS))

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

#Load font
font = ImageFont.truetype(FONT, FONT_SIZE)

# Parse the .lrc file using pylrc
lrc_file = open("data/sound/Pantera.lrc")
lrc_string = ''.join(lrc_file.readlines())
lrc_file.close()

subs = pylrc.parse(lrc_string)
mp3_file = "data/sound/Pantera.mp3"

def SongFinished(event):
    global song_has_finished
    print("Event reports - finished")
    song_has_finished = True
    # Show the cursor
    sys.stdout.write("\033[?25h")


def getColor(x): 
    #return DOT_COLORS[int((x - TEXT_AREA_START) / COLOR_CHUNK)]
    return 0xFFFFFF

def getStripPixelIndex(x, y):
    if y % 2 == 0:
        return x + y * DISPLAY_WIDTH
    else:
        return y * DISPLAY_WIDTH + (DISPLAY_WIDTH - x - 1)

def display_text(text):

    # Measure the size of our text
    text_width, text_height = font.getsize(text)

    # Create a new PIL image big enough to fit the text
    image = Image.new('P', (TEXT_AREA_WIDTH + text_width + TEXT_AREA_WIDTH, text_height), 0)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), text, font=font, fill=255, stroke_width=0, stroke_fill=255)

    offset_x = 0
    # Loop over all the text area
    for x in range(TEXT_AREA_START, TEXT_AREA_END):
        for y in range(DISPLAY_HEIGHT):

            if image.getpixel((x + offset_x, y)) == 255:
                ws.ws2811_led_set(channel, getStripPixelIndex(x,y), getColor(x))
            else:
                ws.ws2811_led_set(channel, getStripPixelIndex(x,y), 0x000000)                            

    # Draw it
    resp = ws.ws2811_render(leds)
    if resp != ws.WS2811_SUCCESS:
        message = ws.ws2811_get_return_t_str(resp)
        raise RuntimeError('ws2811_render failed with code {0} ({1})'.format(resp, message))

# Wrap following code in a try/finally to ensure cleanup functions are called
# after library is initialized.
try:


    ##scroll_text_horizontal()

    song_has_finished = False

    # Prepare VLC
    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new_path(mp3_file) #Your audio file here
    player.set_media(media)
    events = player.event_manager()
    events.event_attach(vlc.EventType.MediaPlayerEndReached, SongFinished)

    # handle ctrl-c
    def sigint_handler(signum, frame):
        player.stop()
        # Show cursor
        sys.stdout.write("\033[?25h")
        exit(0)

    signal.signal(signal.SIGINT, sigint_handler)

    # Start playing the song
    print('Playing "' + subs.title + '" by "' + subs.artist + '"')
    player.audio_set_volume(100)
    player.play()

    # Hide the cursor
    sys.stdout.write("\033[?25l")

    line = 0
    num_lines = len(subs)
    line_printed = False

    # wait for the song to finish
    while song_has_finished == False:
        sec = player.get_time() / 1000

        # should we show the next lyrics?
        if line+1 == num_lines or sec < subs[line+1].time:
            # make sure that we only show the lyric once
            if line_printed == False:
                text = subs[line].text.rstrip()
                print("\r" + text + " " * (60 - len(subs[line].text)), end='', flush=True)
                display_text(text)

                line_printed = True
        else:
            line += 1
            line_printed = False

finally:
    # Ensure ws2811_fini is called before the program quits.
    ws.ws2811_fini(leds)
    # Example of calling delete function to clean up structure memory.  Isn't
    # strictly necessary at the end of the program execution here, but is good practice.
    ws.delete_ws2811_t(leds)