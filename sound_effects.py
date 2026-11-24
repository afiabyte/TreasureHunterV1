"""
SoundEffects: Procedural audio synthesizer for tactical sound feedback and ambient music.

Synthesizes rich retro-pixel RPG dungeon sound effects and atmospheric background music
using Pygame's mixer and NumPy. Completely standalone: requires zero external MP3/WAV
files, preventing missing asset errors or audio licensing issues.
If audio hardware is unavailable (e.g. headless CI/test environments), it gracefully
handles failure without interrupting gameplay.
"""

import math
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

import pygame
from typing import Optional


class SoundManager:
    """
    Procedurally synthesizes and coordinates tactical sound effects and
    ambient background dungeon music on dedicated audio mixer channels.
    """

    def __init__(self) -> None:
        self.enabled: bool = False
        self._sound_enabled: bool = True
        self._music_enabled: bool = False
        self.music_volume: float = 0.45
        self.sfx_volume: float = 0.70
        self.current_track: Optional[str] = None
        self.music_channel: Optional[pygame.mixer.Channel] = None

        if not NUMPY_AVAILABLE:
            self.enabled = False
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(16)
            self.music_channel = pygame.mixer.Channel(0)
            self.enabled = True
        except Exception:
            self.enabled = False

        # Pre-rendered procedural SFX handles
        self.snd_move: Optional[pygame.mixer.Sound] = None
        self.snd_click: Optional[pygame.mixer.Sound] = None
        self.snd_key: Optional[pygame.mixer.Sound] = None
        self.snd_shift: Optional[pygame.mixer.Sound] = None
        self.snd_spawn: Optional[pygame.mixer.Sound] = None
        self.snd_door: Optional[pygame.mixer.Sound] = None
        self.snd_alert: Optional[pygame.mixer.Sound] = None
        self.snd_victory: Optional[pygame.mixer.Sound] = None
        self.snd_defeat: Optional[pygame.mixer.Sound] = None

        # Pre-rendered procedural BGM tracks
        self.bgm_menu: Optional[pygame.mixer.Sound] = None
        self.bgm_dungeon: Optional[pygame.mixer.Sound] = None

        if self.enabled:
            self._generate_sounds()
            self._generate_music_tracks()

    # =========================================================================
    # VOLUME & ENABLED PROPERTIES
    # =========================================================================
    @property
    def sound_enabled(self) -> bool:
        """Whether tactical sound effects are enabled."""
        return self._sound_enabled

    @sound_enabled.setter
    def sound_enabled(self, value: bool) -> None:
        self._sound_enabled = bool(value)

    @property
    def is_muted(self) -> bool:
        """Backward compatibility for legacy is_muted flag."""
        return not self._sound_enabled

    @is_muted.setter
    def is_muted(self, value: bool) -> None:
        self._sound_enabled = not bool(value)

    @property
    def music_enabled(self) -> bool:
        """Whether ambient background music is enabled."""
        return self._music_enabled

    @music_enabled.setter
    def music_enabled(self, value: bool) -> None:
        self._music_enabled = bool(value)
        if not self._music_enabled:
            self.stop_music()
        else:
            if self.current_track:
                self.play_music(self.current_track)
            else:
                self.play_music("menu")

    def toggle_sound(self) -> bool:
        """Toggle procedural audio mute state. Returns True if now active."""
        self._sound_enabled = not self._sound_enabled
        return self._sound_enabled

    def toggle_music(self) -> bool:
        """Toggle background music playback state. Returns True if now active."""
        self.music_enabled = not self.music_enabled
        return self.music_enabled

    def set_music_volume(self, volume: float) -> None:
        """Set background music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        if self.music_channel:
            self.music_channel.set_volume(self.music_volume)

    def set_sfx_volume(self, volume: float) -> None:
        """Set tactical sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for snd in [
            self.snd_move, self.snd_click, self.snd_key, self.snd_shift,
            self.snd_spawn, self.snd_door, self.snd_alert, self.snd_victory,
            self.snd_defeat
        ]:
            if snd:
                snd.set_volume(self.sfx_volume)

    # =========================================================================
    # PROCEDURAL SOUND EFFECTS SYNTHESIS
    # =========================================================================
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
            envelope = np.linspace(1.0, 0.0, total_samples)
            audio = (wave * envelope * volume * 32767).astype(np.int16)
            # Duplicate to 2-channel stereo
            stereo = np.column_stack([audio, audio])
            return pygame.sndarray.make_sound(stereo)
        except Exception:
            return None

    def _generate_sounds(self) -> None:
        """Pre-render tactical procedural sound effects with authentic retro RPG flavor."""
        try:
            sample_rate = 44100

            # 1. Footstep / Tile Move (Short stone tile step click + sub-thud, 0.06s)
            dur_m = 0.06
            t_m = np.linspace(0, dur_m, int(sample_rate * dur_m), endpoint=False)
            noise_m = (np.random.rand(len(t_m)) * 2.0 - 1.0) * 0.15
            tone_m = np.sin(2 * np.pi * 140.0 * t_m) * 0.35
            env_m = np.exp(-45.0 * t_m)
            snd_m_data = ((tone_m + noise_m) * env_m * 0.45 * 32767).astype(np.int16)
            self.snd_move = pygame.sndarray.make_sound(np.column_stack([snd_m_data, snd_m_data]))

            # 2. UI Click / Select (Crisp wooden button tap blip, 0.04s)
            dur_c = 0.04
            t_c = np.linspace(0, dur_c, int(sample_rate * dur_c), endpoint=False)
            wave_c = (np.sin(2 * np.pi * 750.0 * t_c) * 0.6 + np.sin(2 * np.pi * 1500.0 * t_c) * 0.4)
            env_c = np.exp(-70.0 * t_c)
            snd_c_data = (wave_c * env_c * 0.30 * 32767).astype(np.int16)
            self.snd_click = pygame.sndarray.make_sound(np.column_stack([snd_c_data, snd_c_data]))

            # 3. Relic Key Pickup (Ascending 3-tone harmonic bell chime, 0.32s)
            # D5 (587.33Hz) -> A5 (880Hz) -> D6 (1174.66Hz)
            t_k1 = np.linspace(0, 0.08, int(sample_rate * 0.08), endpoint=False)
            t_k2 = np.linspace(0, 0.10, int(sample_rate * 0.10), endpoint=False)
            t_k3 = np.linspace(0, 0.14, int(sample_rate * 0.14), endpoint=False)
            w_k1 = (np.sin(2 * np.pi * 587.33 * t_k1) + 0.3 * np.sin(2 * np.pi * 1174.66 * t_k1)) * np.linspace(1.0, 0.4, len(t_k1))
            w_k2 = (np.sin(2 * np.pi * 880.00 * t_k2) + 0.3 * np.sin(2 * np.pi * 1760.00 * t_k2)) * np.linspace(1.0, 0.3, len(t_k2))
            w_k3 = (np.sin(2 * np.pi * 1174.66 * t_k3) + 0.4 * np.sin(2 * np.pi * 2349.32 * t_k3)) * np.exp(-12.0 * t_k3)
            w_key = np.concatenate([w_k1, w_k2, w_k3])
            snd_k_data = (w_key * 0.32 * 32767).astype(np.int16)
            self.snd_key = pygame.sndarray.make_sound(np.column_stack([snd_k_data, snd_k_data]))

            # 4. Wall Shift (Low grinding stone rumble and gravel slide, 0.22s)
            dur_s = 0.22
            t_s = np.linspace(0, dur_s, int(sample_rate * dur_s), endpoint=False)
            freq_s = np.linspace(190.0, 65.0, len(t_s))
            grumble = np.sin(2 * np.pi * freq_s * t_s) * 0.6
            gravel = (np.random.rand(len(t_s)) * 2.0 - 1.0) * 0.35
            env_s = np.sin(np.pi * np.linspace(0.0, 1.0, len(t_s))) * np.exp(-2.5 * t_s)
            snd_s_data = ((grumble + gravel) * env_s * 0.40 * 32767).astype(np.int16)
            self.snd_shift = pygame.sndarray.make_sound(np.column_stack([snd_s_data, snd_s_data]))

            # 5. Hunter Spawn / Teleport (Pulsing dissonant apparition drone, 0.25s)
            dur_sp = 0.25
            t_sp = np.linspace(0, dur_sp, int(sample_rate * dur_sp), endpoint=False)
            w_sp = (np.sin(2 * np.pi * 320.0 * t_sp) * 0.5 + np.sin(2 * np.pi * 342.0 * t_sp) * 0.5)
            env_sp = np.exp(-6.0 * t_sp)
            snd_sp_data = (w_sp * env_sp * 0.35 * 32767).astype(np.int16)
            self.snd_spawn = pygame.sndarray.make_sound(np.column_stack([snd_sp_data, snd_sp_data]))

            # 6. Exit Portal / Chamber Unlocked (Shimmering ethereal chime, 0.35s)
            dur_d = 0.35
            t_d = np.linspace(0, dur_d, int(sample_rate * dur_d), endpoint=False)
            w_d = (np.sin(2 * np.pi * 659.25 * t_d) * 0.4 +
                   np.sin(2 * np.pi * 987.77 * t_d) * 0.3 +
                   np.sin(2 * np.pi * 1318.51 * t_d) * 0.3) * np.exp(-7.0 * t_d)
            snd_d_data = (w_d * 0.35 * 32767).astype(np.int16)
            self.snd_door = pygame.sndarray.make_sound(np.column_stack([snd_d_data, snd_d_data]))

            # 7. Hunter Alert / Proximity Warning (Tense double chirp blip, 0.16s)
            dur_a = 0.16
            t_a = np.linspace(0, dur_a, int(sample_rate * dur_a), endpoint=False)
            w_a = np.sin(2 * np.pi * np.linspace(520.0, 780.0, len(t_a)) * t_a) * np.exp(-14.0 * t_a)
            snd_a_data = (w_a * 0.32 * 32767).astype(np.int16)
            self.snd_alert = pygame.sndarray.make_sound(np.column_stack([snd_a_data, snd_a_data]))

            # 8. Victory Fanfare (Triumphant RPG arpeggio + sustained chord, 0.65s)
            # C5 -> E5 -> G5 -> C6 -> Major Chord
            t_v1 = np.linspace(0, 0.10, int(sample_rate * 0.10), endpoint=False)
            t_v2 = np.linspace(0, 0.10, int(sample_rate * 0.10), endpoint=False)
            t_v3 = np.linspace(0, 0.10, int(sample_rate * 0.10), endpoint=False)
            t_v4 = np.linspace(0, 0.35, int(sample_rate * 0.35), endpoint=False)

            c5 = np.sin(2 * np.pi * 523.25 * t_v1) * np.linspace(1.0, 0.6, len(t_v1))
            e5 = np.sin(2 * np.pi * 659.25 * t_v2) * np.linspace(1.0, 0.6, len(t_v2))
            g5 = np.sin(2 * np.pi * 783.99 * t_v3) * np.linspace(1.0, 0.6, len(t_v3))
            c6_chord = (np.sin(2 * np.pi * 1046.50 * t_v4) * 0.5 +
                        np.sin(2 * np.pi * 783.99 * t_v4) * 0.3 +
                        np.sin(2 * np.pi * 523.25 * t_v4) * 0.2) * np.exp(-5.0 * t_v4)

            w_vic = np.concatenate([c5, e5, g5, c6_chord])
            snd_vic_data = (w_vic * 0.40 * 32767).astype(np.int16)
            self.snd_victory = pygame.sndarray.make_sound(np.column_stack([snd_vic_data, snd_vic_data]))

            # 9. Defeat Alarm (Descending ominous dungeon casualty sweep, 0.45s)
            t_def = np.linspace(0, 0.45, int(sample_rate * 0.45), endpoint=False)
            freq_sweep = np.linspace(310.0, 75.0, len(t_def))
            w_def = (np.sin(2 * np.pi * freq_sweep * t_def) * 0.7 +
                     np.sin(2 * np.pi * (freq_sweep * 1.5) * t_def) * 0.3) * np.exp(-4.5 * t_def)
            snd_def_data = (w_def * 0.42 * 32767).astype(np.int16)
            self.snd_defeat = pygame.sndarray.make_sound(np.column_stack([snd_def_data, snd_def_data]))

            self.set_sfx_volume(self.sfx_volume)
        except Exception:
            pass

    # =========================================================================
    # PROCEDURAL BACKGROUND MUSIC SYNTHESIS
    # =========================================================================
    def _synthesize_bgm_track(self, is_dungeon: bool = False, duration: float = 16.0) -> Optional[pygame.mixer.Sound]:
        """
        Procedurally synthesize an ambient retro RPG dungeon background music loop.
        Fast (sub-0.2s generation), seamless zero-click looping, and 44.1kHz stereo quality.
        """
        try:
            sample_rate = 44100
            total_samples = int(sample_rate * duration)
            t = np.linspace(0, duration, total_samples, endpoint=False)
            audio_l = np.zeros(total_samples, dtype=np.float32)
            audio_r = np.zeros(total_samples, dtype=np.float32)

            # Chord progression (D natural minor / Dorian)
            if not is_dungeon:
                # Menu Theme: Warm, mystical, adventurous (Dm -> Bb -> C -> Am)
                chords = [
                    (146.83, [146.83, 174.61, 220.00, 293.66]),  # Dm
                    (116.54, [116.54, 146.83, 174.61, 233.08]),  # Bb
                    (130.81, [130.81, 164.81, 196.00, 261.63]),  # C
                    (110.00, [110.00, 130.81, 164.81, 220.00]),  # Am
                ]
                arp_patterns = [
                    [293.66, 349.23, 440.00, 523.25, 440.00, 349.23, 440.00, 587.33],
                    [233.08, 293.66, 349.23, 466.16, 349.23, 293.66, 349.23, 466.16],
                    [261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 392.00, 523.25],
                    [220.00, 261.63, 329.63, 440.00, 329.63, 261.63, 329.63, 440.00],
                ]
            else:
                # Dungeon Theme: Tense, stealthy, suspenseful (Dm -> Gm -> Dm -> A)
                chords = [
                    (146.83, [146.83, 174.61, 220.00]),          # Dm
                    (98.00,  [98.00, 146.83, 174.61, 196.00]),   # Gm
                    (146.83, [146.83, 174.61, 220.00, 293.66]),  # Dm
                    (110.00, [110.00, 138.59, 164.81, 220.00]),  # A
                ]
                arp_patterns = [
                    [146.83, 220.00, 293.66, 349.23, 293.66, 220.00, 293.66, 220.00],
                    [98.00,  196.00, 233.08, 293.66, 233.08, 196.00, 233.08, 196.00],
                    [146.83, 220.00, 293.66, 349.23, 293.66, 220.00, 293.66, 220.00],
                    [110.00, 220.00, 277.18, 329.63, 277.18, 220.00, 277.18, 220.00],
                ]

            chord_dur = duration / len(chords)

            # 1. Atmospheric Organ / Synth Pad Drone
            for i, (root, notes) in enumerate(chords):
                idx_start = int(i * chord_dur * sample_rate)
                idx_end = int((i + 1) * chord_dur * sample_rate)
                t_chord = t[idx_start:idx_end]
                chord_len = idx_end - idx_start

                env = np.ones(chord_len, dtype=np.float32)
                fade_len = int(sample_rate * 0.45)
                if fade_len > 0 and chord_len > 2 * fade_len:
                    env[:fade_len] = np.linspace(0.0, 1.0, fade_len)
                    env[-fade_len:] = np.linspace(1.0, 0.0, fade_len)

                pad_wave = np.zeros(chord_len, dtype=np.float32)
                for freq in notes:
                    vib = np.sin(2 * np.pi * 3.5 * t_chord) * 0.003
                    pad_wave += np.sin(2 * np.pi * freq * (1.0 + vib) * t_chord) * 0.06
                    pad_wave += np.sin(2 * np.pi * freq * 2.0 * t_chord) * 0.015

                # Low sub-bass
                bass_wave = np.sin(2 * np.pi * (root / 2.0) * t_chord) * 0.12
                pad_wave = (pad_wave + bass_wave) * env

                audio_l[idx_start:idx_end] += pad_wave * 0.85
                audio_r[idx_start:idx_end] += pad_wave * 0.85

            # 2. Fantasy Pluck / Kalimba Arpeggio
            bpm = 92 if not is_dungeon else 105
            beat_dur = 60.0 / bpm
            eighth_dur = beat_dur / 2.0
            num_notes = int(duration / eighth_dur)

            for n in range(num_notes):
                chord_idx = int((n * eighth_dur) / chord_dur) % len(chords)
                pattern = arp_patterns[chord_idx]
                note_freq = pattern[n % len(pattern)]

                note_start = int(n * eighth_dur * sample_rate)
                note_len = min(int(sample_rate * 0.45), total_samples - note_start)
                if note_len <= 0:
                    continue
                t_note = np.linspace(0, note_len / sample_rate, note_len, endpoint=False)

                decay = np.exp(-8.0 * t_note)
                pluck = (np.sin(2 * np.pi * note_freq * t_note) * 0.7 +
                         np.sin(2 * np.pi * note_freq * 2.0 * t_note) * 0.2 +
                         np.sin(2 * np.pi * note_freq * 3.0 * t_note) * 0.1) * decay * 0.09

                pan_left = 0.5 + 0.3 * np.sin(n * 0.65)
                pan_right = 1.0 - pan_left

                audio_l[note_start:note_start + note_len] += pluck * pan_left
                audio_r[note_start:note_start + note_len] += pluck * pan_right

            # 3. Soft Ambient Dungeon Drum / Pulse
            meas_dur = beat_dur * 4.0
            num_measures = int(duration / meas_dur)
            for m in range(num_measures):
                kick_start = int(m * meas_dur * sample_rate)
                kick_len = int(sample_rate * 0.32)
                if kick_start + kick_len > total_samples:
                    continue
                t_k = np.linspace(0, 0.32, kick_len, endpoint=False)
                k_freq = np.linspace(80.0, 32.0, kick_len)
                k_wave = np.sin(2 * np.pi * k_freq * t_k) * np.exp(-8.5 * t_k) * (0.18 if is_dungeon else 0.12)
                audio_l[kick_start:kick_start + kick_len] += k_wave
                audio_r[kick_start:kick_start + kick_len] += k_wave

            # 4. Smooth loop seam crossfade (last 0.25s faded into first 0.25s for click-free repeat)
            seam_len = int(sample_rate * 0.25)
            seam_curve = np.linspace(0.0, 1.0, seam_len)
            audio_l[:seam_len] = audio_l[:seam_len] * seam_curve + audio_l[-seam_len:] * (1.0 - seam_curve)
            audio_r[:seam_len] = audio_r[:seam_len] * seam_curve + audio_r[-seam_len:] * (1.0 - seam_curve)

            # Normalize to prevent distortion
            max_amp = max(np.max(np.abs(audio_l)), np.max(np.abs(audio_r)))
            if max_amp > 0.01:
                norm = 0.80 / max_amp
                audio_l *= norm
                audio_r *= norm

            # 16-bit signed stereo numpy array
            audio_stereo = np.column_stack([
                (audio_l * 32767).astype(np.int16),
                (audio_r * 32767).astype(np.int16)
            ])
            return pygame.sndarray.make_sound(audio_stereo)
        except Exception:
            return None

    def _generate_music_tracks(self) -> None:
        """Pre-render menu and dungeon background music tracks."""
        self.bgm_menu = self._synthesize_bgm_track(is_dungeon=False, duration=16.0)
        self.bgm_dungeon = self._synthesize_bgm_track(is_dungeon=True, duration=16.0)

    # =========================================================================
    # MUSIC PLAYBACK CONTROLS
    # =========================================================================
    def play_music(self, track: str = "menu") -> None:
        """
        Play looping ambient background music on the dedicated music channel.

        Args:
            track: Either 'menu' or 'dungeon'.
        """
        self.current_track = track
        if not self.enabled or not self._music_enabled or not self.music_channel:
            return

        target_snd = self.bgm_dungeon if track == "dungeon" else self.bgm_menu
        if not target_snd:
            return

        try:
            if not self.music_channel.get_busy() or getattr(self.music_channel, "_current_snd", None) != target_snd:
                self.music_channel.set_volume(self.music_volume)
                self.music_channel.play(target_snd, loops=-1)
                self.music_channel._current_snd = target_snd
        except Exception:
            pass

    def stop_music(self) -> None:
        """Stop background music playback."""
        if self.music_channel:
            try:
                self.music_channel.stop()
                self.music_channel._current_snd = None
            except Exception:
                pass

    def pause_music(self) -> None:
        """Pause background music playback."""
        if self.music_channel:
            try:
                self.music_channel.pause()
            except Exception:
                pass

    def unpause_music(self) -> None:
        """Unpause background music playback."""
        if self.music_channel and self._music_enabled:
            try:
                self.music_channel.unpause()
            except Exception:
                pass

    # =========================================================================
    # SOUND EFFECTS PLAYBACK METHODS
    # =========================================================================
    def play_move(self) -> None:
        """Play player footstep move sound."""
        if self.snd_move and self._sound_enabled:
            self.snd_move.play()

    def play_step(self) -> None:
        """Alias for UI step and navigation clicks."""
        self.play_click()

    def play_click(self) -> None:
        """Play crisp button press click."""
        if self.snd_click and self._sound_enabled:
            self.snd_click.play()
        elif self.snd_move and self._sound_enabled:
            self.snd_move.play()

    def play_key(self) -> None:
        """Play relic key pickup chime."""
        if self.snd_key and self._sound_enabled:
            self.snd_key.play()

    def play_shift(self) -> None:
        """Play stone wall shifting grind rumble."""
        if self.snd_shift and self._sound_enabled:
            self.snd_shift.play()

    def play_spawn(self) -> None:
        """Play hunter drone summoning sound."""
        if self.snd_spawn and self._sound_enabled:
            self.snd_spawn.play()

    def play_door(self) -> None:
        """Play exit portal extraction chime."""
        if self.snd_door and self._sound_enabled:
            self.snd_door.play()
        elif self.snd_key and self._sound_enabled:
            self.snd_key.play()

    def play_alert(self) -> None:
        """Play hunter proximity alert sound."""
        if self.snd_alert and self._sound_enabled:
            self.snd_alert.play()

    def play_victory(self) -> None:
        """Play triumphant RPG victory fanfare."""
        if self.snd_victory and self._sound_enabled:
            self.snd_victory.play()

    def play_defeat(self) -> None:
        """Play dark casualty defeat alarm."""
        if self.snd_defeat and self._sound_enabled:
            self.snd_defeat.play()
