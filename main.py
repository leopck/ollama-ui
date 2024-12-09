import os
import sys
import json

from PySide6.QtCore import Qt, QFileSystemWatcher
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
from components.chat_widget import ChatWidget

# Set DEV_MODE to True for live update, False for no live update
DEV_MODE = True


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ollama UI")
        self.setWindowIcon(QIcon(':/icons/ai_icon.png'))
        self.setObjectName("window")
        
        # Initialize chat history
        self.chat_history = []
        self.history_file = "chat_history.json"
        self.loadChatHistory()
        
        # Create main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create header with New Chat button
        header = QHBoxLayout()
        new_chat_button = QPushButton("New Chat")
        new_chat_button.setObjectName("new-chat-button")
        new_chat_button.setCursor(Qt.PointingHandCursor)
        new_chat_button.clicked.connect(self.createNewChat)
        header.addWidget(new_chat_button)
        header.addStretch()  # This pushes the button to the left
        
        # Create a widget for the header and add it to main layout
        header_widget = QWidget()
        header_widget.setLayout(header)
        layout.addWidget(header_widget)
        
        # Initialize chat widget
        self.chat = ChatWidget()
        self.chat.setAttribute(Qt.WA_StyledBackground, True)
        layout.addWidget(self.chat)
        
        self.setLayout(layout)
        self.resize(800, 600)
        
        # Create initial chat session if none exists
        if not self.chat_history:
            self.createNewChat()
        else:
            # Load the most recent chat
            self.loadMostRecentChat()

    def loadChatHistory(self):
        try:
            with open(self.history_file, 'r') as file:
                self.chat_history = json.load(file)
        except FileNotFoundError:
            self.saveChatHistory()

    def saveChatHistory(self):
        with open(self.history_file, 'w') as file:
            json.dump(self.chat_history, file)

    def createNewChat(self):
        new_chat = {
            "chat_id": len(self.chat_history) + 1,
            "message": "New Chat Session",
            "content": []
        }
        self.chat_history.append(new_chat)
        self.saveChatHistory()
        self.chat.changePage(json.dumps(new_chat))

    def loadMostRecentChat(self):
        if self.chat_history:
            most_recent_chat = self.chat_history[-1]
            self.chat.changePage(json.dumps(most_recent_chat))


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