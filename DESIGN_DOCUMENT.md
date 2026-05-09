# Design Document

## Project Name

Piano Practice Studio

## Course

CST205

## Project Goal

Create a simple multimedia piano application that is easy to explain in an
intro Python course while still showing clear interactivity, file handling,
graphics, and audio playback.

## Target User

A student or casual user who wants to click notes, test keyboard shortcuts,
record a short melody, and save it for later playback.

## Core Features

- Interactive piano keys for one octave.
- Audio playback for natural piano note testing.
- Recording with note timestamps.
- Playback that preserves recorded timing.
- Save and load recordings with `pickle`.
- Generated visual banner using `Pillow`.

## Why This Design Fits The Course

- `tkinter` keeps the GUI approachable and avoids advanced frameworks.
- `pickle` satisfies the course-level file-saving requirement.
- `Pillow` adds clear multimedia value without making the code too complex.
- Built-in `wave` generation removes the need for SciPy or NumPy.

## Program Structure

### `app.py`

- Builds the main window.
- Creates the piano key layout.
- Handles note playback and keyboard shortcuts.
- Tracks recordings as a list of note/timestamp dictionaries.
- Saves and loads recordings with `pickle`.

### `notes.py`

- Stores note frequencies for C4 through B4.
- Generates missing `.wav` files with sine waves.
- Makes sure the app can still run if a note file is deleted accidentally.

## Data Design

Saved recordings use a dictionary with this shape:

```python
{
    "project": "Piano Practice Studio",
    "saved_at": "2026-05-08 21:30:00",
    "events": [
        {"note": "C4", "time": 0.0},
        {"note": "E4", "time": 0.42},
        {"note": "G4", "time": 0.91},
    ],
}
```

This format is simple, readable, and easy to validate after loading.

## User Flow

1. Open the program.
2. Play notes with buttons or keyboard keys.
3. Start recording.
4. Play a melody.
5. Stop recording.
6. Replay the melody or save it to a `.pkl` file.
7. Load the file later and replay it again.

## Testing Plan

- Verify the app opens without missing-file errors.
- Verify each piano key triggers the correct note name.
- Verify recording stores note events.
- Verify playback follows the recorded order and timing.
- Verify save/load keeps the same melody data.
- Verify deleting a note file causes the app to regenerate it automatically.

## Future Improvements

- Add more octaves.
- Add a metronome.
- Add a timeline view for recorded notes.
- Add theme options or background art chosen by the user.
