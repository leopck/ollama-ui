import os
import sys
import json
from PySide6.QtCore import Qt, QFileSystemWatcher
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QLabel)
from PySide6.QtWebEngineWidgets import QWebEngineView
from components.chat_widget import ChatWidget

# Set DEV_MODE to True for live update, False for no live update
DEV_MODE = True

class PDFReader(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        
        # Create button to select PDF
        self.select_button = QPushButton("Select PDF")
        self.select_button.clicked.connect(self.select_pdf)
        
        # Create PDF viewer using QWebEngineView
        self.pdf_view = QWebEngineView()
        
        # Add widgets to layout
        self.layout.addWidget(self.select_button)
        self.layout.addWidget(self.pdf_view)
        
        self.setLayout(self.layout)
        
    def select_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_name:
            # Load PDF file into viewer
            self.pdf_view.setUrl(f"file:///{file_name}")

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ollama UI with PDF Reader")
        self.setWindowIcon(QIcon(':/icons/ai_icon.png'))
        self.setObjectName("window")
        
        # Initialize chat history
        self.chat_history = []
        self.history_file = "chat_history.json"
        self.loadChatHistory()
        
        # Create main layout
        main_layout = QHBoxLayout()  # Changed to QHBoxLayout for side-by-side widgets
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Initialize PDF reader widget
        self.pdf_reader = PDFReader()
        main_layout.addWidget(self.pdf_reader, 1)  # Add stretch factor of 1
        
        # Initialize chat widget
        self.chat = ChatWidget()
        self.chat.setAttribute(Qt.WA_StyledBackground, True)
        main_layout.addWidget(self.chat, 2)  # Add stretch factor of 2
        
        self.setLayout(main_layout)
        self.resize(1200, 600)  # Increased default width to accommodate both widgets
        
        # Create initial chat session if none exists
        if not self.chat_history:
            self.createInitialChat()
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

    def createInitialChat(self):
        initial_chat = {
            "chat_id": 1,
            "message": "Chat Session",
            "content": []
        }
        self.chat_history.append(initial_chat)
        self.saveChatHistory()
        self.chat.changePage(json.dumps(initial_chat))

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