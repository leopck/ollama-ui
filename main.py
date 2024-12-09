import os
import sys

from PySide6.QtCore import Qt, QFileSystemWatcher
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from components.chat_widget import ChatWidget

# Set DEV_MODE to True for live update, False for no live update
DEV_MODE = True


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ollama UI")
        self.setWindowIcon(QIcon(':/icons/ai_icon.png'))
        self.setObjectName("window")
        
        # Changed to VBoxLayout since we only have one widget now
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Initialize chat widget
        self.chat = ChatWidget()
        self.chat.setAttribute(Qt.WA_StyledBackground, True)
        
        # Add chat widget to layout
        layout.addWidget(self.chat)
        self.setLayout(layout)
        self.resize(800, 600)
        
        # If the ChatWidget needs an initial page setup, you can do it here
        # self.chat.changePage("default_page")  # Uncomment and modify as needed


if __name__ == "__main__":
    app = QApplication(sys.argv)

    stylesheet_path = os.path.join(os.path.dirname(__file__), 'index.css')
    if os.path.exists(stylesheet_path):
        with open(stylesheet_path, 'r') as file:
            stylesheet = file.read()
            app.setStyleSheet(stylesheet)

    if DEV_MODE:
        watcher = QFileSystemWatcher()
        watcher.addPath('index.css')

        def update_stylesheet(path):
            new_stylesheet = open(path).read()
            app.setStyleSheet(new_stylesheet)

        watcher.fileChanged.connect(update_stylesheet)

    window = Window()
    window.show()
    sys.exit(app.exec())