import sys, os, json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QTextEdit, QShortcut, QFileDialog, QPushButton, QScrollArea, QMenu
)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QKeySequence

class SimpleNotes(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SimpleNotes")
        self.setGeometry(300, 100, 900, 600)
        self.load_settings()
        self.set_stylesheet(self.theme)

        self.notes = {}  # {title: content}
        self.current_note_title = None

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Sidebar container with scroll
        self.sidebar_container = QWidget()
        self.sidebar_container.setStyleSheet("background-color: #202326;")  # Match main window
        self.sidebar_layout = QVBoxLayout(self.sidebar_container)
        self.sidebar_layout.setAlignment(Qt.AlignTop)
        self.sidebar_scroll = QScrollArea()
        self.sidebar_scroll.setWidgetResizable(True)
        self.sidebar_scroll.setWidget(self.sidebar_container)
        self.sidebar_scroll.setFixedWidth(250)
        layout.addWidget(self.sidebar_scroll)

        # Editor area
        editor_layout = QVBoxLayout()
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Note title")
        self.title_edit.setFixedHeight(55)  # Make title bigger
        self.title_edit.setStyleSheet("font-size: 20px; padding: 10px;")
        editor_layout.addWidget(self.title_edit)
        self.editor = QTextEdit()
        self.editor.setStyleSheet("font-size: 14px; padding: 10px;")
        editor_layout.addWidget(self.editor)
        layout.addLayout(editor_layout)

        # Shortcuts
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_note)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self.export_note)
        QShortcut(QKeySequence("Ctrl+N"), self).activated.connect(self.new_note)

        # Load saved notes
        self.notes_file = os.path.join(os.path.expanduser("~"), "simplenotes.json")
        self.load_notes()

    def set_stylesheet(self, theme):
        style_dark = """
            *{font-family: hack, arial;}
            QMainWindow { background-color: #202326; color: #ffffff; }
            QPushButton.noteButton {
                background-color: #292c30; 
                color: #ffffff; 
                border: 1px solid #414346; 
                padding: 10px;
                border-radius: 6px;
                text-align: left;
            }
            QPushButton.noteButton:hover {
                border: 1px solid #0a6cff;
            }
            QLineEdit, QTextEdit { background-color: #292c30; color: #ffffff; border: 1px solid #414346; padding: 6px; }
        """
        self.setStyleSheet(style_dark)

    def save_note(self):
        title = self.title_edit.text().strip()
        if not title:
            return
        content = self.editor.toPlainText()
        self.notes[title] = content
        self.current_note_title = title
        self.update_sidebar()
        self.save_notes_to_file()

    def new_note(self):
        self.current_note_title = None
        self.title_edit.clear()
        self.editor.clear()

    def load_note(self, title):
        self.current_note_title = title
        self.title_edit.setText(title)
        self.editor.setText(self.notes.get(title, ""))

    def export_note(self):
        if not self.current_note_title:
            return
        content = self.editor.toPlainText()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export Note", f"{self.current_note_title}.txt", "Text Files (*.txt)"
        )
        if file_path:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

    def update_sidebar(self):
        # Clear existing buttons
        for i in reversed(range(self.sidebar_layout.count())):
            widget = self.sidebar_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add buttons for notes
        for title in self.notes.keys():
            btn = QPushButton(title)
            btn.setObjectName("noteButton")
            btn.setProperty("class", "noteButton")
            btn.clicked.connect(lambda checked, t=title: self.load_note(t))
            btn.setContextMenuPolicy(Qt.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, t=title, b=btn: self.show_button_menu(pos, t, b))
            self.sidebar_layout.addWidget(btn)

    def show_button_menu(self, position, title, button):
        menu = QMenu()
        delete_action = menu.addAction("Delete Note")
        action = menu.exec_(button.mapToGlobal(position))
        if action == delete_action:
            if title in self.notes:
                del self.notes[title]
                self.update_sidebar()
                if self.current_note_title == title:
                    self.new_note()
                self.save_notes_to_file()

    def save_notes_to_file(self):
        try:
            with open(self.notes_file, "w", encoding="utf-8") as f:
                json.dump(self.notes, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("Error saving notes:", e)

    def load_notes(self):
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, "r", encoding="utf-8") as f:
                    self.notes = json.load(f)
                self.update_sidebar()
            except Exception as e:
                print("Failed to load notes:", e)

    def load_settings(self):
        settings = QSettings("Tudify", "SimpleNotes")
        self.theme = "dark"  # Force theme to dark

    def save_settings(self):
        settings = QSettings("Tudify", "SimpleNotes")
        settings.setValue("theme", self.theme)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleNotes()
    window.show()
    sys.exit(app.exec_())