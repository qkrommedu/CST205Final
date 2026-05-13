"""
Course: CST205 Introduction to Multimedia Design and Programming
Project: Music Piano
Abstract: Piano app using Pickle
Authors: Paulo Camacho
Date: 2026-05-08
GitHub repository: https://github.com/qkrommedu/CST205Final

File responsibilities:

Team contribution notes:

Sources:
"""

import os
import pickle
import shutil
import subprocess
import sys
import random
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from PIL import Image, ImageDraw, ImageTk

from notes import NOTE_FREQUENCIES, ensure_notes_exist


WHITE_KEYS = ["C4", "D4", "E4", "F4", "G4", "A4", "B4"]
BLACK_KEY_COLUMNS = {
    "C#4": 1,
    "D#4": 2,
    "F#4": 4,
    "G#4": 5,
    "A#4": 6,
}
KEYBOARD_BINDINGS = {
    "a": "C4",
    "w": "C#4",
    "s": "D4",
    "e": "D#4",
    "d": "E4",
    "f": "F4",
    "t": "F#4",
    "g": "G4",
    "y": "G#4",
    "h": "A4",
    "u": "A#4",
    "j": "B4",
}
NOTES_DIRECTORY = Path(__file__).resolve().parent / "notes"
PROJECT_GITHUB_URL = "https://github.com/qkrommedu/CST205Final"


class SoundPlayer:
    """Plays WAV files with tools that are usually available on each platform."""

    def __init__(self):
        self.command = self._detect_command()
        self.current_process = None

    def _detect_command(self):
        if sys.platform == "darwin" and shutil.which("afplay"):
            return ["afplay"]

        if sys.platform.startswith("linux"):
            for command in ("aplay", "paplay"):
                if shutil.which(command):
                    return [command]

        return None

    def play(self, file_path):
        if os.name == "nt":
            import winsound

            winsound.PlaySound(None, 0)
            winsound.PlaySound(str(file_path), winsound.SND_FILENAME | winsound.SND_ASYNC)
            return

        if self.command:
            self.stop()
            self.current_process = subprocess.Popen(
                self.command + [str(file_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return

        raise RuntimeError("No compatible audio player was found on this computer.")

    def stop(self):
        if self.current_process and self.current_process.poll() is None:
            self.current_process.terminate()
            try:
                self.current_process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self.current_process.kill()
        self.current_process = None


class PianoPracticeStudio:
    """Main window for the piano project."""

    def __init__(self, root):
        self.root = root
        self.root.title("Piano Practice Studio")
        self.root.configure(bg="#f5efe4")
        self.root.minsize(940, 720)

        ensure_notes_exist(force=True)

        self.sound_player = SoundPlayer()
        self.note_paths = {
            note_name: NOTES_DIRECTORY / f"{note_name}.wav"
            for note_name in NOTE_FREQUENCIES
        }

        self.recorded_events = []
        self.recording_started_at = None
        self.is_recording = False
        self.is_playing_recording = False
        self.loaded_recording_name = "Unsaved recording"

        self.status_text = tk.StringVar(
            value="Ready to play. Click a key or use the keyboard shortcuts."
        )
        self.recording_text = tk.StringVar(value="0 notes recorded")
        self.song_text = tk.StringVar(value="Current song: Unsaved recording")

        self.banner_image = None

        self.build_interface()
        self.update_recording_summary()
        self.root.bind("<KeyPress>", self.handle_keypress)

    def build_interface(self):
        self.main_frame = tk.Frame(self.root, bg="#f5efe4", padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        # Added a top frame to hold title and random color background button
        top_frame = tk.Frame(self.main_frame, bg="#f5efe4")
        top_frame.pack(fill="x")

        title_label = tk.Label(
            top_frame,
            text="Piano Practice Studio",
            font=("Helvetica", 24, "bold"),
            bg="#f5efe4",
            fg="#2d1f12",
        )

        title_label.pack(side="left")

        # New added intereactive button to change the background color
        random_button = tk.Button(
            top_frame,
            text="Random Color Background",
            command=self.random_background_color,
            font=("Helvetica", 10, "bold"),
            bg="#6fa8dc",
            fg="black",
            relief="flat",
            cursor="hand2",
        )
        random_button.pack(side="right", padx=5)
        

        subtitle_label = tk.Label(
            self.main_frame,
            text=(
                "An intro-Python music project with WAV playback, Pillow visuals, "
                "and pickle save/load tools."
            ),
            font=("Helvetica", 11),
            bg="#f5efe4",
            fg="#5c4735",
        )
        subtitle_label.pack(anchor="w", pady=(4, 12))

        self.banner_image = self.create_banner_image()
        banner_label = tk.Label(
            self.main_frame,
            image=self.banner_image,
            bg="#f5efe4",
            bd=0,
        )
        banner_label.pack(fill="x", pady=(0, 16))

        controls_frame = tk.LabelFrame(
            self.main_frame,
            text="Recording Controls",
            font=("Helvetica", 12, "bold"),
            bg="#f5efe4",
            fg="#2d1f12",
            padx=12,
            pady=12,
        )
        controls_frame.pack(fill="x")

        control_buttons = [
            ("Start Recording", self.start_recording, "#3c7a4a"),
            ("Stop Recording", self.stop_recording, "#8a5d1f"),
            ("Play Recording", self.play_recording, "#375a7f"),
            ("Save Recording", self.save_recording, "#5a3d7f"),
            ("Load Recording", self.load_recording, "#3d6f73"),
            ("Clear Recording", self.clear_recording, "#8f3b2e"),
        ]

        for index, (label, command, color) in enumerate(control_buttons):
            button = tk.Button(
                controls_frame,
                text=label,
                command=command,
                font=("Helvetica", 10, "bold"),
                bg=color,
                fg="black",
                activebackground=color,
                activeforeground="white",
                padx=10,
                pady=10,
                relief="flat",
                cursor="hand2",
            )
            button.grid(row=0, column=index, padx=6, pady=6, sticky="ew")
            controls_frame.grid_columnconfigure(index, weight=1)

        info_frame = tk.Frame(self.main_frame, bg="#f5efe4")
        info_frame.pack(fill="x", pady=(14, 12))

        tk.Label(
            info_frame,
            textvariable=self.song_text,
            font=("Helvetica", 11, "bold"),
            bg="#f5efe4",
            fg="#2d1f12",
        ).pack(anchor="w")

        tk.Label(
            info_frame,
            textvariable=self.recording_text,
            font=("Helvetica", 10),
            bg="#f5efe4",
            fg="#5c4735",
        ).pack(anchor="w", pady=(4, 0))

        tk.Label(
            info_frame,
            text=(
                "Keyboard shortcuts: A W S E D F T G Y H U J"
                "  |  GitHub: " + PROJECT_GITHUB_URL
            ),
            font=("Helvetica", 10),
            bg="#f5efe4",
            fg="#5c4735",
        ).pack(anchor="w", pady=(8, 0))

        piano_frame = tk.LabelFrame(
            self.main_frame,
            text="Piano Keys",
            font=("Helvetica", 12, "bold"),
            bg="#f5efe4",
            fg="#2d1f12",
            padx=12,
            pady=12,
        )
        piano_frame.pack(fill="x")

        black_keys_frame = tk.Frame(piano_frame, bg="#d8c8b8")
        black_keys_frame.pack(fill="x", pady=(0, 8))

        white_keys_frame = tk.Frame(piano_frame, bg="#d8c8b8")
        white_keys_frame.pack(fill="x")

        for column in range(7):
            black_keys_frame.grid_columnconfigure(column, weight=1, uniform="keys")
            white_keys_frame.grid_columnconfigure(column, weight=1, uniform="keys")

        for column in range(7):
            if column in BLACK_KEY_COLUMNS.values():
                note_name = next(
                    key for key, note_column in BLACK_KEY_COLUMNS.items() if note_column == column
                )
                self.make_key_button(
                    black_keys_frame,
                    note_name,
                    column,
                    "#111111",
                    "black",
                    2,
                )
            else:
                spacer = tk.Label(
                    black_keys_frame,
                    text="",
                    bg="#d8c8b8",
                    width=10,
                )
                spacer.grid(row=0, column=column, padx=5, pady=2, sticky="nsew")

        for column, note_name in enumerate(WHITE_KEYS):
            self.make_key_button(
                white_keys_frame,
                note_name,
                column,
                "#fff9ef",
                "#2d1f12",
                4,
            )

        lower_frame = tk.Frame(self.main_frame, bg="#f5efe4")
        lower_frame.pack(fill="both", expand=True, pady=(16, 0))

        recent_notes_frame = tk.LabelFrame(
            lower_frame,
            text="Recent Notes",
            font=("Helvetica", 12, "bold"),
            bg="#f5efe4",
            fg="#2d1f12",
            padx=12,
            pady=12,
        )
        recent_notes_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.recent_notes_listbox = tk.Listbox(
            recent_notes_frame,
            font=("Courier", 11),
            height=10,
            bg="#fffdf8",
            fg="#2d1f12",
        )
        self.recent_notes_listbox.pack(fill="both", expand=True)

        status_frame = tk.LabelFrame(
            lower_frame,
            text="Status",
            font=("Helvetica", 12, "bold"),
            bg="#f5efe4",
            fg="#2d1f12",
            padx=12,
            pady=12,
        )
        status_frame.pack(side="left", fill="both", expand=True, padx=(8, 0))

        tk.Label(
            status_frame,
            textvariable=self.status_text,
            justify="left",
            wraplength=360,
            font=("Helvetica", 11),
            bg="#f5efe4",
            fg="#2d1f12",
        ).pack(anchor="nw")

    def create_banner_image(self):
        image = Image.new("RGB", (900, 150), "#2c221c")
        draw = ImageDraw.Draw(image)

        for stripe_index in range(150):
            color_value = 44 + stripe_index // 5
            draw.line(
                (0, stripe_index, 900, stripe_index),
                fill=(color_value, 34, 28),
            )

        draw.rounded_rectangle((24, 20, 876, 130), radius=24, fill="#f3e8d2")

        white_key_width = 62
        start_x = 70
        for index in range(10):
            left = start_x + index * white_key_width
            draw.rectangle((left, 42, left + white_key_width - 4, 118), fill="#fffdf8", outline="#8a7d72")

        for offset in (1, 2, 4, 5, 6, 8, 9):
            left = start_x + offset * white_key_width - 18
            draw.rectangle((left, 42, left + 30, 84), fill="#151515", outline="#151515")

        draw.ellipse((700, 44, 740, 84), fill="#d99058")
        draw.rectangle((731, 58, 742, 116), fill="#d99058")
        draw.ellipse((756, 56, 790, 90), fill="#5f7adb")
        draw.rectangle((779, 56, 789, 118), fill="#5f7adb")

        return ImageTk.PhotoImage(image)

    def make_key_button(self, parent, note_name, column, background, foreground, height):
        button = tk.Button(
            parent,
            text=f"{note_name}\n[{self.find_shortcut(note_name)}]",
            command=lambda chosen_note=note_name: self.play_note(chosen_note),
            font=("Helvetica", 12, "bold"),
            bg=background,
            fg=foreground,
            activebackground=background,
            activeforeground=foreground,
            relief="raised",
            bd=2,
            height=height,
            cursor="hand2",
        )
        button.grid(row=0, column=column, padx=5, pady=5, sticky="nsew")

    # Function for random background color, kept the ranges higher to make it more easier on the eyes(pastel colors)
    def random_background_color(self):
        r = random.randint(150, 255)
        g = random.randint(150, 255)
        b = random.randint(150, 255)

        random_color = f"#{r:02x}{g:02x}{b:02x}"

        self.root.configure(bg=random_color)
        self.main_frame.configure(bg=random_color)

    def find_shortcut(self, note_name):
        for key_name, mapped_note in KEYBOARD_BINDINGS.items():
            if mapped_note == note_name:
                return key_name.upper()
        return ""

    def handle_keypress(self, event):
        shortcut = event.keysym.lower()
        if shortcut in KEYBOARD_BINDINGS:
            self.play_note(KEYBOARD_BINDINGS[shortcut])

    def play_note(self, note_name, from_recording=False):
        note_path = self.note_paths[note_name]

        if not note_path.exists():
            ensure_notes_exist([note_name])

        try:
            self.sound_player.play(note_path)
        except RuntimeError as error:
            self.status_text.set(str(error))
            return

        self.add_recent_note(note_name)

        if self.is_recording and not from_recording:
            timestamp = round(time.time() - self.recording_started_at, 3)
            self.recorded_events.append({"note": note_name, "time": timestamp})
            self.update_recording_summary()

        if from_recording:
            self.status_text.set(f"Playback note: {note_name}")
        elif self.is_recording:
            self.status_text.set(f"Recorded note: {note_name}")
        else:
            self.status_text.set(f"Played note: {note_name}")

    def add_recent_note(self, note_name):
        clock_time = time.strftime("%H:%M:%S")
        self.recent_notes_listbox.insert(0, f"{clock_time}  {note_name}")
        while self.recent_notes_listbox.size() > 12:
            self.recent_notes_listbox.delete(12)

    def start_recording(self):
        if self.is_playing_recording:
            self.status_text.set("Wait for playback to finish before starting a new recording.")
            return

        self.recorded_events = []
        self.recording_started_at = time.time()
        self.is_recording = True
        self.loaded_recording_name = "Unsaved recording"
        self.update_recording_summary()
        self.status_text.set("Recording started. Play notes to build a melody.")

    def stop_recording(self):
        if not self.is_recording:
            self.status_text.set("Recording is already stopped.")
            return

        self.is_recording = False
        self.update_recording_summary()
        self.status_text.set("Recording stopped. You can now play, save, or clear it.")

    def play_recording(self):
        if not self.recorded_events:
            self.status_text.set("Record or load a melody before trying playback.")
            return

        if self.is_playing_recording:
            self.status_text.set("Playback is already running.")
            return

        if self.is_recording:
            self.stop_recording()

        self.is_playing_recording = True
        self.status_text.set("Playing the saved melody now.")

        playback_thread = threading.Thread(target=self.play_recording_worker, daemon=True)
        playback_thread.start()

    def play_recording_worker(self):
        previous_time = 0
        events_to_play = list(self.recorded_events)

        # This switches between playback
        for event in events_to_play:
            wait_time = max(0, event["time"] - previous_time)
            time.sleep(wait_time)
            previous_time = event["time"]
            self.root.after(
                0,
                lambda note_name=event["note"]: self.play_note(note_name, from_recording=True),
            )

        self.root.after(0, self.finish_playback)

    def finish_playback(self):
        self.is_playing_recording = False
        self.status_text.set("Finished.")

    def clear_recording(self):
        if self.is_playing_recording:
            self.status_text.set("Wait.")
            return

        self.recorded_events = []
        self.is_recording = False
        self.loaded_recording_name = "Unsaved"
        self.update_recording_summary()
        self.status_text.set("Cleared.")

    def save_recording(self):
        if self.is_playing_recording:
            self.status_text.set("Wait")
            return

        if not self.recorded_events:
            self.status_text.set("No recording yet")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save recording",
            defaultextension=".pkl",
            filetypes=[("Pickle recording", "*.pkl")],
            initialfile="piano_recording.pkl",
        )

        if not file_path:
            self.status_text.set("Save cancelled.")
            return

        recording_data = {
            "project": "Piano Practice Studio",
            "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "events": self.recorded_events,
        }

        with open(file_path, "wb") as save_file:
            pickle.dump(recording_data, save_file)

        self.loaded_recording_name = Path(file_path).stem
        self.update_recording_summary()
        self.status_text.set(f"Saved recording to {file_path}")

    def load_recording(self):
        if self.is_playing_recording:
            self.status_text.set("Wait")
            return

        file_path = filedialog.askopenfilename(
            title="Load recording",
            filetypes=[("Pickle recording", "*.pkl")],
        )

        if not file_path:
            self.status_text.set("Load cancelled.")
            return

        try:
            with open(file_path, "rb") as load_file:
                recording_data = pickle.load(load_file)
            loaded_events = self.validate_recording_data(recording_data)
        except (OSError, pickle.PickleError, ValueError) as error:
            messagebox.showerror("Load error", f"could not find:\n{error}")
            self.status_text.set("Pick valid recording")
            return

        self.recorded_events = loaded_events
        self.is_recording = False
        self.loaded_recording_name = Path(file_path).stem
        self.update_recording_summary()
        self.status_text.set(f"Loaded recording from {file_path}")

    def validate_recording_data(self, recording_data):
        if not isinstance(recording_data, dict) or "events" not in recording_data:
            raise ValueError("File is missing, try again")

        loaded_events = recording_data["events"]
        if not isinstance(loaded_events, list):
            raise ValueError("Nope")

        cleaned_events = []
        for event in loaded_events:
            if not isinstance(event, dict):
                raise ValueError("Error not in database")

            note_name = event.get("note")
            note_time = event.get("time")

            if note_name not in NOTE_FREQUENCIES:
                raise ValueError(f"Unknown: {note_name}")

            if not isinstance(note_time, (int, float)) or note_time < 0:
                raise ValueError("Non negative number")

            cleaned_events.append({"note": note_name, "time": float(note_time)})

        cleaned_events.sort(key=lambda event: event["time"])
        return cleaned_events

    def update_recording_summary(self):
        note_total = len(self.recorded_events)
        total_length = 0

        if self.recorded_events:
            total_length = round(self.recorded_events[-1]["time"], 2)

        self.recording_text.set(
            f"{note_total} notes recorded | Approximate length: {total_length} seconds"
        )
        self.song_text.set(f"Current song: {self.loaded_recording_name}")


def main():
    root = tk.Tk()
    PianoPracticeStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
