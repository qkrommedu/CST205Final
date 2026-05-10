# Piano Practice Studio

Course: `CST205`

Date: `2026-05-08`

GitHub Repository: <https://github.com/qkrommedu/CST205Final>

Team Members: Update this section with the official team member names before submission.

## Project Overview

Piano Practice Studio is a beginner-friendly multimedia project built with
`tkinter`, `Pillow`, and `pickle`. The app lets a user play piano notes,
record a melody, save the melody to a pickle file, load it later, and replay it.

This version was refactored to stay close to intro Python tools. It avoids
heavy GUI or audio dependencies and can regenerate missing note files with
Python's built-in `wave` module.

## Features

- Play 12 piano notes from one octave, including sharp notes.
- Use mouse clicks or keyboard shortcuts to trigger notes.
- Record a melody with timing data.
- Replay the melody using the recorded rhythm.
- Save recordings to `.pkl` files with `pickle`.
- Load saved recordings back into the app.
- Display recent notes and project status inside the window.
- Show a generated Pillow banner for a stronger multimedia presentation.

## How To Run

1. Make sure Python 3 and Pillow are installed.
2. Open the project folder in a terminal.
3. Run `python3 app.py`
4. Click piano keys or use the keyboard shortcuts:
   `A W S E D F T G Y H U J`

If any WAV note files are missing, the program creates them automatically.

## File Guide

- `app.py`: Main Tkinter application and recording logic.
- `notes.py`: WAV note generator using built-in Python modules.
- `notes/`: Audio files used by the piano keys.
- `DESIGN_DOCUMENT.md`: High-level design choices and project structure.
- `SUBMISSION_CHECKLIST.md`: Rubric-focused checklist for final submission prep.

## Contribution Notes

Update this section before submission with who worked on which files, functions,
or classes. The rubric asks for that information specifically.

Example format:

- `Student Name`: Tkinter layout, note playback, and recording controls.
- `Student Name`: Save/load system, testing, and documentation updates.

## Future Work

- Add multiple octaves.
- Add tempo controls for playback.
- Add album-art style custom themes with more Pillow graphics.
- Add a visual sheet-music or note-timeline display.
- Export recordings to a text or CSV summary for practice logs.
