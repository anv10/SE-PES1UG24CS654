import array
import math
import pygame


def _tone(freqs, duration, volume=0.4):
    # Build a sound from a sequence of notes, each a fading sine wave.
    rate, _size, channels = pygame.mixer.get_init()
    samples = array.array("h")
    n = int(rate * duration)
    for freq in freqs:
        for i in range(n):
            fade = 1 - i / n
            value = int(32767 * volume * fade * math.sin(2 * math.pi * freq * i / rate))
            samples.extend([value] * channels)
    return pygame.mixer.Sound(buffer=samples.tobytes())


class Sounds:
    # Generated in code (no sound files). If audio is unavailable the
    # game keeps running silently.
    def __init__(self):
        self.eat = None
        self.game_over = None
        try:
            init = pygame.mixer.get_init()
            if init is None or init[1] != -16:
                pygame.mixer.quit()
                pygame.mixer.init(frequency=22050, size=-16, channels=1)
            self.eat = _tone([660, 990], 0.1, volume=0.8)
            self.game_over = _tone([440, 330, 220], 0.15, volume=0.7)
        except Exception:
            self.eat = None
            self.game_over = None

    def play(self, sound):
        if sound is None:
            return
        try:
            sound.play()
        except Exception:
            pass
