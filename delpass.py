import pathlib
from tools import log
import time
import threading
import math
from leds import ColorMode, ColorIntensity, Leds
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
            cls.history = []
            cls.lock = threading.Lock()
            cls.mode_end_time = None
            cls.leds = Leds()

            # Create image for Space invader
            cls.imageSpaceInvaderUp   = Image.open("data/images/SpaceInvaderUP.png",   mode='r', formats=None)
            cls.imageSpaceInvaderDown = Image.open("data/images/SpaceInvaderDOWN.png", mode='r', formats=None)

            # Create image for Light
            cls.imageLight = Image.open("data/images/Light.png",   mode='r', formats=None)

            # Create image for Saucer
            cls.imageSaucer = Image.open("data/images/Saucer.png",   mode='r', formats=None)

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
        if mode != "text" and mode != "sound" and mode != "image" and mode != "status":
            raise ValueError(f"Unknow mode {mode}")
        elif mode == "text" and not params["text"]:
            raise ValueError("Text should not be empty in text mode")
        elif mode == "sound" and not params["sound"]:
            raise ValueError("Sound must be selected in sound mode")
        elif mode == "image" and not params["image"]:
            raise ValueError("Image must be selected in image mode")
        

        # Lock access
        with self.lock:
            self.mode = mode
            self.params = params
            self.history.append(params)
            
            # Stop any currently running animation
            self.leds.running_set(False)
            self.new_mode = mode

    def run(self):
        while True:
            # Depending on the mode, do the desired one

            if self.mode == MODE_TEXT:
                self._display_text(self.params)
            else:
                self._run_default_sequence()
            
    def _display_text(self, params):
        self.leds.display_text(params["text"])

    def _run_default_sequence(self):

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


        