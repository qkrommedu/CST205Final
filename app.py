import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QSizePolicy
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtCore import QUrl

class SimplePiano(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple PySide Piano")
        self.setFixedSize(500, 250)

        # Create a horizontal layout for the keys
        layout = QHBoxLayout()
        layout.setSpacing(2) # Small gap between keys
        
        # Define our notes 
        self.notes = ["C4", "D4", "E4", "F4", "G4", "A4", "B4"]
        self.sounds = {}

        current_dir = os.path.dirname(os.path.abspath(__file__))

        for note in self.notes:
            btn = QPushButton(note)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


            sound = QSoundEffect(self)
            sound_path = os.path.join(current_dir, "notes", f"{note}.wav")
            
            sound.setSource(QUrl.fromLocalFile(sound_path))
            self.sounds[note] = sound

            
            btn.pressed.connect(lambda n=note: self.play_note(n))
            
            layout.addWidget(btn)

        self.setLayout(layout)

    def play_note(self, note):
        self.sounds[note].play()
        
        print(f"Playing note: {note}")

def main():
    app = QApplication(sys.argv)
    window = SimplePiano()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
