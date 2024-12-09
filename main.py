import os
import sys

from PySide6.QtCore import Qt, QFileSystemWatcher
from PySide6.QtGui import QIcon, QKeyEvent
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout
from components.chat_widget import ChatWidget
from components.sidebar import Sidebar

# Set DEV_MODE to True for live update, False for no live update
DEV_MODE = True


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ollama UI")
        self.setWindowIcon(QIcon(':/icons/ai_icon.png'))
        self.setObjectName("window")
        self.messages_visible = True  # Track visibility state
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        sidebar = Sidebar()
        sidebar.setAttribute(Qt.WA_StyledBackground, True)
        self.chat = ChatWidget()
        self.chat.setAttribute(Qt.WA_StyledBackground, True)

        layout.addWidget(sidebar, stretch=1)
        layout.addWidget(self.chat)
        self.setLayout(layout)
        self.resize(800, 600)
        sidebar.page_content.connect(self.chat.changePage)

        # Enable key event handling
        self.setFocusPolicy(Qt.StrongFocus)

    def keyPressEvent(self, event: QKeyEvent):
        # Check for Ctrl+H
        if event.key() == Qt.Key_H and event.modifiers() == Qt.ControlModifier:
            self.toggleMessagesVisibility()
        else:
            super().keyPressEvent(event)

    def toggleMessagesVisibility(self):
        self.messages_visible = not self.messages_visible
        # Assuming ChatWidget has a method to show/hide messages
        if hasattr(self.chat, 'setMessagesVisible'):
            self.chat.setMessagesVisible(self.messages_visible)
        # Print current state (you can remove this in production)
        print(f"Messages {'visible' if self.messages_visible else 'hidden'}")


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