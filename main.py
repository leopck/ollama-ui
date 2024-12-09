import os
import sys
import json
from PySide6.QtCore import Qt, QFileSystemWatcher, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QSplitter, QSizePolicy,
                             QScrollArea)
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from components.chat_widget import ChatWidget

# Set DEV_MODE to True for live update, False for no live update
DEV_MODE = True

class PDFReader(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create button to select PDF
        self.select_button = QPushButton("Select PDF")
        self.select_button.clicked.connect(self.select_pdf)
        
        # Create PDF document and viewer
        self.pdf_document = QPdfDocument()
        self.pdf_view = QPdfView()
        self.pdf_view.setDocument(self.pdf_document)
        
        # Configure PDF viewer for all pages
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)  # Show all pages
        self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        
        # Create scroll area for PDF viewer
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.pdf_view)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Set size policy for PDF reader
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumWidth(200)
        
        # Add widgets to layout
        self.layout.addWidget(self.select_button)
        self.layout.addWidget(self.scroll_area)
        
        self.setLayout(self.layout)
        
    def select_pdf(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select PDF", "", "PDF Files (*.pdf)")
        if file_name:
            # Load PDF file into viewer
            self.pdf_document.load(file_name)
            
            # Update PDF view after loading
            self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)
            self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

class ResizableChat(ChatWidget):
    def __init__(self):
        super().__init__()
        # Set size policy and minimum width for chat
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumWidth(150)

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
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for resizable panels
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Initialize PDF reader widget
        self.pdf_reader = PDFReader()
        self.splitter.addWidget(self.pdf_reader)
        
        # Initialize chat widget with new ResizableChat class
        self.chat = ResizableChat()
        self.chat.setAttribute(Qt.WA_StyledBackground, True)
        self.splitter.addWidget(self.chat)
        
        # Set initial sizes (70% PDF reader, 30% chat)
        total_width = 1200
        self.splitter.setSizes([int(total_width * 0.7), int(total_width * 0.3)])
        
        # Enable size constraints on splitter
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        
        # Add splitter to main layout
        main_layout.addWidget(self.splitter)
        
        self.setLayout(main_layout)
        self.resize(1200, 600)
        
        # Create initial chat session if none exists
        if not self.chat_history:
            self.createInitialChat()
        else:
            # Load the most recent chat
            self.loadMostRecentChat()
            
        # Add stylesheet for splitter handle and scrollbars
        self.setStyleSheet("""
            QSplitter::handle {
                background: #cccccc;
                width: 2px;
            }
            QSplitter::handle:hover {
                background: #999999;
            }
            QScrollBar:vertical {
                width: 12px;
            }
            QScrollBar:horizontal {
                height: 12px;
            }
        """)

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