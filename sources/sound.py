import pylrc
import time
import vlc
import pathlib

from tools import log

class Sound():

    # Singleton
    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.log = log.Log(__name__)
            cls.instance = super().__new__(cls)
            cls.running = False

        return cls.instance
    
    def _song_finished(self, event):
        self.log.inf("Song finished")
        self.running = False
    
    def play_sound(self, file_path, lyrics_callback):
        # First we will check if we got the sound
        s = pathlib.Path(file_path)
        l = pathlib.Path(s.parent.joinpath(s.stem + '.lrc'))

        # Now sound abort
        if not s.exists:
            raise ValueError(f"Sound {s.resolve()} not found")
        
        # Now check if we got lyrics
        if not l.exists():
            lyrics = pylrc.parse("")
            self.log.wrn(f"Lyrics for sound {s.resolve()} not found")
        else:
            with open(l.resolve()) as lrc_file:
                lyrics = pylrc.parse(''.join(lrc_file.readlines()))
                self.log.wrn(f"Lyrics found, size: {len(lyrics)}")

        # Prepare VLC
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new_path(s.resolve())
        player.set_media(media)
        events = player.event_manager()
        events.event_attach(vlc.EventType.MediaPlayerEndReached, self._song_finished)

        # By default push volume to maximum
        player.audio_set_volume(100)
        player.play()

        self.running = True

        # Now play sound
        line = 0
        num_lines = len(lyrics)
        line_printed = False
        while self.running:

            # Get current time
            sec = player.get_time() / 1000

            # Should we show the next lyrics?
            if line < num_lines and sec >= lyrics[line].time:
                # make sure that we only show the lyric once
                if line_printed == False:
                    text = lyrics[line].text.rstrip()
                    self.log.inf(f"{text}")
                    lyrics_callback(text)
                    line_printed = True
                else:
                    line += 1
                    line_printed = False
            
            time.sleep(0.005)

        self.running = False
        player.stop()

    def running_set(self, state):
        self.running = state
            



