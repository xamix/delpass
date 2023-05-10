import pathlib
from tools import log
import time

SOUND_DIRECTORY = "data/sound"

class Delpass:

    # Singleton
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.log = log.Log(__name__)
            cls.instance = super().__new__(cls)
            cls.mode = "text"
            cls.history = []
        return cls.instance
    
    def list_sound(self):
        results = []

        for item in pathlib.Path(SOUND_DIRECTORY).rglob("*"):
            if(item.is_file() and not item.name.endswith(".lrc")):
                entry = {
                    "lyrics": pathlib.Path(item.parent.joinpath(item.stem + '.lrc')).exists(),
                    "name": item.stem,
                    "path": str(item.resolve())
                }
                results.append(entry)

        return results
    
    def status(self):
        return {
            "mode": self.mode,
            "history": self.history
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
        pass

    def _run():
        while True:
            time.sleep(1)

            # Depending on the mode, do the desired one
            
            pass

        