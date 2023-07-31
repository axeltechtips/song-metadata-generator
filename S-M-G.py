import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFileDialog, QMessageBox
from PIL import Image

from pydub import AudioSegment
from mutagen.id3 import ID3, APIC, TIT2, TALB, TPE1


class MetadataGeneratorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Metadata Generator")
        self.setGeometry(200, 200, 400, 200)

        self.file_label = QLabel("Audio File:")
        self.file_input = QLineEdit()
        self.file_button = QPushButton("Browse")
        self.file_button.clicked.connect(self.browse_audio_file)

        self.song_label = QLabel("Song Name:")
        self.song_input = QLineEdit()

        self.artist_label = QLabel("Artist Name:")
        self.artist_input = QLineEdit()

        self.album_label = QLabel("Album Name:")
        self.album_input = QLineEdit()

        self.photo_label = QLabel("Song Photo:")
        self.photo_input = QLineEdit()
        self.photo_button = QPushButton("Browse")
        self.photo_button.clicked.connect(self.browse_photo)

        self.generate_button = QPushButton("Generate Metadata")
        self.generate_button.clicked.connect(self.generate_metadata)

        layout = QVBoxLayout()
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_input)
        layout.addWidget(self.file_button)

        layout.addWidget(self.song_label)
        layout.addWidget(self.song_input)

        layout.addWidget(self.artist_label)
        layout.addWidget(self.artist_input)

        layout.addWidget(self.album_label)
        layout.addWidget(self.album_input)

        layout.addWidget(self.photo_label)
        layout.addWidget(self.photo_input)
        layout.addWidget(self.photo_button)

        layout.addWidget(self.generate_button)

        self.setLayout(layout)

    def browse_audio_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Audio File", "", "Audio Files (*.mp3 *.wav *.ogg)")
        if file_path:
            self.file_input.setText(file_path)

    def browse_photo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Song Photo", "", "Image Files (*.jpg *.png *.bmp *.gif)")
        if file_path:
            self.photo_input.setText(file_path)

    def generate_metadata(self):
        audio_file = self.file_input.text().strip()
        song_name = self.song_input.text().strip()
        artist_name = self.artist_input.text().strip()
        album_name = self.album_input.text().strip()
        song_photo = self.photo_input.text().strip()

        if not os.path.exists(audio_file):
            self.show_error_message("Error: Audio file not found.")
            return

        try:
            # Load the audio file using pydub for format support
            audio = AudioSegment.from_file(audio_file)

            # Create an ID3 tag if not already present
            if not hasattr(audio, 'raw'):
                audio.export(audio_file, format='mp3', tags={'title': 'temp'})

            # Load the ID3 tag using mutagen
            audio = ID3(audio_file)

            # Set metadata fields
            audio["TIT2"] = TIT2(encoding=3, text=song_name)
            audio["TPE1"] = TPE1(encoding=3, text=artist_name)
            audio["TALB"] = TALB(encoding=3, text=album_name)

            # Save the metadata
            audio.save()

            if os.path.exists(song_photo):
                with Image.open(song_photo) as img:
                    img.thumbnail((500, 500))  # Resize the image if necessary
                    audio = ID3(audio_file)
                    audio.add(
                        APIC(
                            encoding=3,
                            mime=img.get_format_mimetype(),
                            type=3, desc=u'Cover',
                            data=img.tobytes()
                        )
                    )
                    audio.save()

            self.show_success_message("Metadata has been updated successfully.")
        except Exception as e:
            self.show_error_message(f"Error: {str(e)}")

    def show_error_message(self, message):
        QMessageBox.critical(self, "Error", message)

    def show_success_message(self, message):
        QMessageBox.information(self, "Success", message)


