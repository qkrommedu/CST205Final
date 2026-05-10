"""
Course: CST205 Introduction to Multimedia Design and Programming
Project: Piano Practice Studio
Abstract: Generates the WAV note files used by the piano so the app can run
without SciPy or NumPy.
Authors: Update this line with the official team member names before submission.
Date: 2026-05-08
GitHub repository: https://github.com/qkrommedu/CST205Final

File responsibilities:
- Stores the note frequencies for one octave.
- Creates any missing WAV files with Python's built-in wave module.
"""

import math
import struct
import wave
from pathlib import Path


NOTE_FREQUENCIES = {
    "C4": 261.63,
    "C#4": 277.18,
    "D4": 293.66,
    "D#4": 311.13,
    "E4": 329.63,
    "F4": 349.23,
    "F#4": 369.99,
    "G4": 392.00,
    "G#4": 415.30,
    "A4": 440.00,
    "A#4": 466.16,
    "B4": 493.88,
}

SAMPLE_RATE = 44100
DEFAULT_DURATION = 0.18
DEFAULT_VOLUME = 0.35


def generate_note_file(note_name, frequency_hz, duration_seconds=DEFAULT_DURATION):
    notes_directory = Path(__file__).resolve().parent / "notes"
    notes_directory.mkdir(exist_ok=True)

    file_path = notes_directory / f"{note_name}.wav"
    frame_total = int(SAMPLE_RATE * duration_seconds)
    fade_frames = max(1, int(SAMPLE_RATE * 0.03))

    with wave.open(str(file_path), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)

        for frame_index in range(frame_total):
            sample = math.sin(2 * math.pi * frequency_hz * frame_index / SAMPLE_RATE)
            amplitude = sample * DEFAULT_VOLUME

            # A short fade-out prevents clicks at the end of each note.
            if frame_index >= frame_total - fade_frames:
                amplitude *= (frame_total - frame_index) / fade_frames

            integer_sample = int(amplitude * 32767)
            wav_file.writeframesraw(struct.pack("<h", integer_sample))

    return file_path


def ensure_notes_exist(note_names=None, force=False):
    notes_to_check = note_names or NOTE_FREQUENCIES.keys()
    created_files = []
    notes_directory = Path(__file__).resolve().parent / "notes"
    notes_directory.mkdir(exist_ok=True)

    for note_name in notes_to_check:
        file_path = notes_directory / f"{note_name}.wav"
        if force or not file_path.exists():
            generate_note_file(note_name, NOTE_FREQUENCIES[note_name])
            created_files.append(file_path)

    return created_files


def main():
    created_files = ensure_notes_exist()

    if created_files:
        print("Created note files:")
        for file_path in created_files:
            print(f"- {file_path.name}")
    else:
        print("All note files already exist.")


if __name__ == "__main__":
    main()
