

import wave
from pathlib import Path

import notes


def test_all_twelve_notes_present():
    """The frequency table must contain all 12 notes in one octave."""
    expected = {"C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4"}
    assert set(notes.NOTE_FREQUENCIES.keys()) == expected


def test_standard_a4_frequency():
    """A4 must be 440.00 Hz — the universal tuning reference."""
    assert notes.NOTE_FREQUENCIES["A4"] == 440.00


def test_c4_frequency():
    """C4 (middle C) must be 261.63 Hz."""
    assert notes.NOTE_FREQUENCIES["C4"] == 261.63


def test_frequencies_increase_with_pitch():
    """Each note in the octave must be higher in frequency than the one before it."""
    note_order = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4"]
    frequencies = [notes.NOTE_FREQUENCIES[n] for n in note_order]
    for i in range(len(frequencies) - 1):
        assert frequencies[i] < frequencies[i + 1], (
            f"{note_order[i]} ({frequencies[i]} Hz) should be lower than "
            f"{note_order[i+1]} ({frequencies[i+1]} Hz)"
        )


def test_generate_note_file_creates_file(tmp_path, monkeypatch):
    """generate_note_file should create a WAV file at the expected path."""
    monkeypatch.setattr(notes, "__file__", str(tmp_path / "notes.py"))
    file_path = notes.generate_note_file("C4", 261.63, duration_seconds=0.05)
    assert file_path.exists(), "WAV file was not created"


def test_generated_wav_is_valid(tmp_path, monkeypatch):
    """The generated WAV file should be readable and have correct parameters."""
    monkeypatch.setattr(notes, "__file__", str(tmp_path / "notes.py"))
    file_path = notes.generate_note_file("A4", 440.0, duration_seconds=0.05)

    with wave.open(str(file_path), "rb") as wav_file:
        assert wav_file.getnchannels() == 1,   "Expected mono audio"
        assert wav_file.getsampwidth() == 2,   "Expected 16-bit samples"
        assert wav_file.getframerate() == 44100, "Expected 44100 Hz sample rate"
        assert wav_file.getnframes() > 0,      "Expected at least one audio frame"


def test_generated_wav_correct_duration(tmp_path, monkeypatch):
    """The WAV file duration should match the requested duration."""
    monkeypatch.setattr(notes, "__file__", str(tmp_path / "notes.py"))
    duration = 0.10
    file_path = notes.generate_note_file("E4", 329.63, duration_seconds=duration)

    with wave.open(str(file_path), "rb") as wav_file:
        expected_frames = int(44100 * duration)
        actual_frames = wav_file.getnframes()
        assert actual_frames == expected_frames, (
            f"Expected {expected_frames} frames, got {actual_frames}"
        )

# ensure_notes_exist tests
def test_ensure_notes_exist_creates_missing_files(tmp_path, monkeypatch):
    """ensure_notes_exist should create WAV files that do not already exist."""
    monkeypatch.setattr(notes, "__file__", str(tmp_path / "notes.py"))
    created = notes.ensure_notes_exist()
    notes_dir = tmp_path / "notes"
    assert notes_dir.exists(), "notes/ directory was not created"
    assert len(created) == 12, f"Expected 12 files created, got {len(created)}"


def test_ensure_notes_exist_skips_existing_files(tmp_path, monkeypatch):
    """ensure_notes_exist should not recreate files that already exist."""
    monkeypatch.setattr(notes, "__file__", str(tmp_path / "notes.py"))
    notes.ensure_notes_exist()           # First pass: create all files
    created_second = notes.ensure_notes_exist()  # Second pass: nothing to do
    assert created_second == [], "Expected no files created on second pass"


def test_regenerate_deleted_note_file(tmp_path, monkeypatch):
    """Deleting a WAV file and calling ensure_notes_exist should recreate it."""
    monkeypatch.setattr(notes, "__file__", str(tmp_path / "notes.py"))
    notes.ensure_notes_exist()

    deleted_file = tmp_path / "notes" / "C4.wav"
    deleted_file.unlink()
    assert not deleted_file.exists(), "Setup: file should be deleted"

    notes.ensure_notes_exist(note_names=["C4"])
    assert deleted_file.exists(), "C4.wav was not regenerated after deletion"

if __name__ == "__main__":
    import sys
    import traceback

    test_functions = [
        test_all_twelve_notes_present,
        test_standard_a4_frequency,
        test_c4_frequency,
        test_frequencies_increase_with_pitch,
    ]

    passed = 0
    failed = 0

    print("Running basic tests (no pytest)...\n")
    for test_fn in test_functions:
        try:
            test_fn()
            print(f"  PASS  {test_fn.__name__}")
            passed += 1
        except AssertionError as error:
            print(f"  FAIL  {test_fn.__name__}: {error}")
            failed += 1
        except Exception:
            print(f"  ERROR {test_fn.__name__}:")
            traceback.print_exc()
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)