import pathlib
from tools import log

SOUND_DIRECTORY = "data/sound"

class Delpass:

    # Singleton
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.log = log.Log(__name__)
            cls.instance = super().__new__(cls)
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
    
    def set_mode(self, params):
        self.log.wrn(f"set-mode: {params}")
        pass

        