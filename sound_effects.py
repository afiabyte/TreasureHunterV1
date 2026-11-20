"""
SoundEffects: Procedural audio synthesizer for tactical sound feedback.

Synthesizes short retro-futuristic tactical audio cues using Pygame's mixer
and NumPy. If audio hardware is unavailable, it gracefully handles failure
without interrupting gameplay.
"""

import math
import numpy as np
import pygame
from typing import Optional


class SoundManager:
    """Procedurally synthesizes and plays tactical sound effects."""

    def __init__(self) -> None:
        self.enabled = False
        self.is_muted = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            self.enabled = True
        except Exception:
            self.enabled = False

        self.snd_move: Optional[pygame.mixer.Sound] = None
        self.snd_key: Optional[pygame.mixer.Sound] = None
        self.snd_shift: Optional[pygame.mixer.Sound] = None
        self.snd_spawn: Optional[pygame.mixer.Sound] = None
        self.snd_victory: Optional[pygame.mixer.Sound] = None
        self.snd_defeat: Optional[pygame.mixer.Sound] = None

        if self.enabled:
            self._generate_sounds()

    def toggle_sound(self) -> bool:
        """
        Toggle procedural audio mute state.
        Returns:
            True if audio is now unmuted/active, False if muted.
        """
        self.is_muted = not self.is_muted
        return not self.is_muted

    def _generate_tone(self, freq: float, duration: float, volume: float = 0.25) -> Optional[pygame.mixer.Sound]:
        """Synthesize a pure sine wave tone with linear envelope decay."""
        if not self.enabled:
            return None
        try:
            sample_rate = 44100
            total_samples = int(sample_rate * duration)
            if total_samples <= 0:
                return None
            t = np.linspace(0, duration, total_samples, endpoint=False)
            wave = np.sin(2 * np.pi * freq * t)
            # Apply fade out envelope
            envelope = np.linspace(1.0, 0.0, total_samples)
            audio = (wave * envelope * volume * 32767).astype(np.int16)
            return pygame.sndarray.make_sound(audio)
        except Exception:
            return None

    def _generate_sounds(self) -> None:
        """Pre-render procedural sounds into memory."""
        try:
            self.snd_move = self._generate_tone(440.0, 0.04, 0.12)
            self.snd_shift = self._generate_tone(180.0, 0.12, 0.20)
            self.snd_spawn = self._generate_tone(320.0, 0.15, 0.18)

            # Key pickup: rising two-tone chime
            sample_rate = 44100
            t1 = np.linspace(0, 0.08, int(sample_rate * 0.08), endpoint=False)
            t2 = np.linspace(0, 0.14, int(sample_rate * 0.14), endpoint=False)
            w1 = np.sin(2 * np.pi * 587.33 * t1)  # D5
            w2 = np.sin(2 * np.pi * 880.0 * t2)   # A5
            w = np.concatenate([w1, w2])
            env = np.linspace(1.0, 0.0, len(w))
            self.snd_key = pygame.sndarray.make_sound((w * env * 0.22 * 32767).astype(np.int16))

            # Victory Fanfare: chord arpeggio
            dur = 0.09
            t = np.linspace(0, dur, int(sample_rate * dur), endpoint=False)
            freqs = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
            waves = [np.sin(2 * np.pi * f * t) for f in freqs]
            w_vic = np.concatenate(waves)
            env_vic = np.linspace(1.0, 0.0, len(w_vic))
            self.snd_victory = pygame.sndarray.make_sound((w_vic * env_vic * 0.28 * 32767).astype(np.int16))

            # Defeat Alarm: descending low pitch
            t_def = np.linspace(0, 0.35, int(sample_rate * 0.35), endpoint=False)
            freq_sweep = np.linspace(280.0, 90.0, len(t_def))
            w_def = np.sin(2 * np.pi * freq_sweep * t_def)
            env_def = np.linspace(1.0, 0.0, len(w_def))
            self.snd_defeat = pygame.sndarray.make_sound((w_def * env_def * 0.30 * 32767).astype(np.int16))
        except Exception:
            pass

    def play_move(self) -> None:
        if self.snd_move and not self.is_muted:
            self.snd_move.play()

    def play_key(self) -> None:
        if self.snd_key and not self.is_muted:
            self.snd_key.play()

    def play_shift(self) -> None:
        if self.snd_shift and not self.is_muted:
            self.snd_shift.play()

    def play_spawn(self) -> None:
        if self.snd_spawn and not self.is_muted:
            self.snd_spawn.play()

    def play_victory(self) -> None:
        if self.snd_victory and not self.is_muted:
            self.snd_victory.play()

    def play_defeat(self) -> None:
        if self.snd_defeat and not self.is_muted:
            self.snd_defeat.play()
