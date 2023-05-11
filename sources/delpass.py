import pathlib
from tools import log
import time
import threading
import math
import copy
import json
from leds import ColorMode, ColorIntensity, Leds
from sound import Sound
from PIL import Image

SOUNDS_DIRECTORY = "data/sounds"
IMAGES_DIRECTORY = "data/images"

MODE_DEMO = "demo"
MODE_TEXT = "text"
MODE_SOUND = "sound"
MODE_IMAGE = "image"

class Delpass(threading.Thread):

    # Singleton
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.log = log.Log(__name__)
            cls.instance = super().__new__(cls)
            cls.mode = MODE_DEMO
            cls.params = None
            cls.new_params = False
            cls.history = []
            cls.lock = threading.Lock()
            cls.mode_end_time = None
            cls.leds = Leds()
            cls.sound = Sound()

            # Create image for Space invader
            cls.imageSpaceInvaderUp   = Image.open("data/images/SpaceInvaderUP.png",   mode='r', formats=None)
            cls.imageSpaceInvaderDown = Image.open("data/images/SpaceInvaderDOWN.png", mode='r', formats=None)

            # Create image for Light
            cls.imageLight = Image.open("data/images/Light.png",   mode='r', formats=None)

            # Create image for Saucer
            cls.imageSaucer = Image.open("data/images/Saucer.png",   mode='r', formats=None)

            # Create full white image
            cls.imageFullWhite = Image.new('L', (150, 7), 255)

        return cls.instance
    
    def list_sound(self):
        results = []

        for item in pathlib.Path(SOUNDS_DIRECTORY).rglob("*"):
            if(item.is_file() and not item.name.endswith(".lrc")):
                entry = {
                    "lyrics": pathlib.Path(item.parent.joinpath(item.stem + '.lrc')).exists(),
                    "name": item.stem,
                    "path": str(item.resolve())
                }
                results.append(entry)

        return results
    
    def status(self):
        with self.lock:

            if self.mode_end_time:
                self.end_in = math.max(self.mode_end_time - time.monotonic(), 0)
            else:
                self.end_in = None

            return {
                "mode": self.mode,
                "history": self.history[-40:]
            }
        
    def set_mode(self, params):
        self.log.wrn(f"set-mode: {params}")

        mode = params["mode"]
        if mode != MODE_TEXT and mode != MODE_SOUND and mode != MODE_IMAGE:
            raise ValueError(f"Unknow mode {mode}")
        elif mode == MODE_TEXT and not params["text"]:
            raise ValueError("Text should not be empty in text mode")
        elif mode == MODE_SOUND and not params["sound"]:
            raise ValueError("Sound must be selected in sound mode")
        elif mode == MODE_IMAGE and not params["image"]:
            raise ValueError("Image must be selected in image mode")

        # Lock access
        with self.lock:
            self.mode = mode
            self.params = params
            self.history.append(params)

            self.new_params = True
            
        # Stop any currently running animation and sound
        self.leds.running_set(False)
        self.sound.running_set(False)

    def run(self):

        # At boot, get defaut params
        mode = copy.deepcopy(self.mode)
        params = copy.deepcopy(self.params)

        while True:
            # Copy the desired mode
            with self.lock: 

                # Copy new params in case needed               
                if self.new_params:

                    self.new_params = False

                    mode = copy.deepcopy(self.mode)
                    params = copy.deepcopy(self.params)

                    colorMode = ColorMode.SPECTRUM if params["color_mode"] == 'spectrum' else ColorMode.FIXED
                    if params["color_intensity"] == 'spacial':
                        colorIntensity = ColorIntensity.SPACIAL
                    elif params["color_intensity"] == 'temporal':
                        colorIntensity = ColorIntensity.SPACIAL
                    else:
                        colorIntensity = ColorMode.FIXED

                    g = int(params["color"]["g"])
                    r = int(params["color"]["r"])
                    b = int(params["color"]["b"])
                    color = (g << 16) + (r << 8) + b

                    self.leds.set_color_params(colorMode, colorIntensity, color)

            if mode == MODE_TEXT:
                self._display_text(params)
            elif mode == MODE_SOUND:
                self._play_sound(params)
            elif mode == MODE_IMAGE:
                self._display_image(params)
            else:
                self.mode = "demo"
                self._display_default_sequence()
            
    def _display_text(self, params):

        duration = params["duration"]

        self.leds.display_text(params["text"], duration=duration)

    def _play_sound(self, params):
        sound = json.loads(params["sound"])
        self.sound.play_sound(sound["path"],
            lambda text: self.leds.display_text(text, scroll=False))

    def _display_image(self, params):

        duration = params["duration"]

        if params["image"] == "space_invader":
            self.leds.display_image(self.imageSpaceInvaderUp, self.imageSpaceInvaderDown, space=10, duration=duration)
        elif params["image"] == "light":
            self.leds.display_image(self.imageLight, space=5, duration=duration)
        elif params["image"] == "saucer":
            self.leds.display_image(self.imageSaucer, space=5, duration=duration)
        else:
            self.leds.display_image(self.imageFullWhite, duration=duration)

    def _display_default_sequence(self):

        if self.mode == MODE_DEMO:
            self.leds.set_color_params(ColorMode.SPECTRUM, ColorIntensity.SPACIAL)
            self.leds.display_text("PELPASS FESTIVAL")
        
        if self.mode == MODE_DEMO:
            self.leds.set_color_params(ColorMode.SPECTRUM, ColorIntensity.TEMPORAL, 0xFF0000)
            self.leds.display_image(self.imageLight, space=5, repeat_count=1, end_wait=5)

        if self.mode == MODE_DEMO:
            self.leds.set_color_params(ColorMode.SPECTRUM, ColorIntensity.TEMPORAL)
            self.leds.display_text("ALIEN EXIST")

        if self.mode == MODE_DEMO:
            self.leds.set_color_params(ColorMode.SPECTRUM, ColorIntensity.FIXED) 
            self.leds.display_image(self.imageSpaceInvaderDown, self.imageSpaceInvaderUp, space=10, end_wait=5)

        if self.mode == MODE_DEMO:        
            self.leds.set_color_params(ColorMode.SPECTRUM, ColorIntensity.FIXED) 
            self.leds.display_text("ALIEN ARE EVERYWHERE")

        if self.mode == MODE_DEMO:
            self.leds.set_color_params(ColorMode.SPECTRUM, ColorIntensity.FIXED) 
            self.leds.display_image(self.imageSaucer)


        