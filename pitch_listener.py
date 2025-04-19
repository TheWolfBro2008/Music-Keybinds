import aubio
import numpy as np
import pyaudio
from collections import deque


class PitchListener:
    def __init__(self, callback, rate=44100, buffer_size=1024, stability_threshold=3, transpose_semitones=2):
        self.rate = rate
        self.buffer_size = buffer_size
        self.callback = callback
        self.stability_threshold = stability_threshold
        self.transpose_semitones = transpose_semitones

        self.pitch_detector = aubio.pitch("default", buffer_size * 2, buffer_size, rate)
        self.pitch_detector.set_unit("Hz")
        self.pitch_detector.set_silence(-40)

        self.recent_notes = deque(maxlen=stability_threshold)
        self.last_confirmed_note = None

        self.pyaudio_instance = pyaudio.PyAudio()
        self.stream = self.pyaudio_instance.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=rate,
            input=True,
            frames_per_buffer=buffer_size,
            stream_callback=self._audio_callback
        )

        self.running = False

    def _audio_callback(self, in_data, frame_count, time_info, status):
        samples = np.frombuffer(in_data, dtype=np.float32)
        raw_pitch = self.pitch_detector(samples)[0]

        note = hz_to_note(raw_pitch, self.transpose_semitones)

        if self.running and note:
            self.recent_notes.append(note)
            if self.recent_notes.count(note) >= self.stability_threshold:
                if note != self.last_confirmed_note:
                    self.last_confirmed_note = note
                    if self.callback:
                        self.callback(note)

        return (in_data, pyaudio.paContinue)

    def set_transposition(self, semitones):
        self.transpose_semitones = semitones

    def start(self):
        self.running = True
        self.stream.start_stream()

    def stop(self):
        self.running = False
        self.stream.stop_stream()

    def close(self):
        self.stream.close()
        self.pyaudio_instance.terminate()


def hz_to_note(freq, transpose_semitones=2):
    if freq <= 0:
        return None

    A4 = 440.0
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    semitones_from_A4 = int(round(12 * np.log2(freq / A4)))
    semitones_from_A4 += transpose_semitones

    midi_note = semitones_from_A4 + 69

    # Adjust for valid range
    lowest_note = 40  # E3
    highest_note = 96  # C7

    if midi_note < lowest_note or midi_note > highest_note:
        return None

    note_index = midi_note % 12
    octave = (midi_note // 12) - 1

    return notes[note_index] + str(octave)
