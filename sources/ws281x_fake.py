WS2811_SUCCESS = 0

def new_ws2811_t():
    return None

def ws2811_fini(leds):
    pass

def delete_ws2811_t(leds):
    pass

def ws2811_channel_t_count_set(leds, count):
    pass


def ws2811_channel_get(leds, channel):
    return None

def ws2811_channel_t_count_set(channel, count):
    pass

def ws2811_channel_t_gpionum_set(channel, gpio):
    pass

def ws2811_channel_t_invert_set(channel, invert):
    pass

def ws2811_channel_t_brightness_set(channel, brighness):
    pass

def ws2811_t_freq_set(leds, freq):
    pass

def ws2811_t_dmanum_set(leds, dma):
    pass

def ws2811_init(leds):
    return WS2811_SUCCESS

def ws2811_get_return_t_str(resp):
    return None

def ws2811_led_set(leds, index, color):
    pass

def ws2811_render(leds):
    return WS2811_SUCCESS
