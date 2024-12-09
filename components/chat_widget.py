import json
import rc_icons
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QMovie
from PySide6.QtWidgets import (QLineEdit, QPushButton, QHBoxLayout, QWidget, 
    QVBoxLayout, QLabel, QScrollArea, QApplication, QSizePolicy, QTextEdit)

from backend.main import get_response

class GrowingTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super(GrowingTextEdit, self).__init__(*args, **kwargs)
        self.setObjectName('main-label')
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setReadOnly(True)

    def resizeEvent(self, event):
        super(GrowingTextEdit, self).resizeEvent(event)
        contents_height = self.document().size().height()
        self.setFixedHeight(contents_height)

class ChatWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setObjectName('chat-widget')
        self.setMinimumWidth(500)
        self.setLayout(self.layout)

        self.response_widget = QWidget()
        self.response_widget.setObjectName('main-chat-widget')
        self.response_layout = QVBoxLayout()
        self.response_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.response_widget.setLayout(self.response_layout)

        self.response_scroll_area = QScrollArea()
        self.response_scroll_area.setWidgetResizable(True)
        self.response_scroll_area.setWidget(self.response_widget)

        self.layout.addWidget(self.response_scroll_area)
        self.input_widget = self.create_input_widget()
        self.input_widget.setEnabled(False)
        
        # Initialize loading spinner
        self.loading_movie = QMovie("icons/spinner.gif")
        self.loading_movie.setScaledSize(QSize(20, 20))  # Match the size of your submit button icon

    def create_input_widget(self):
        input_widget = QWidget()
        input_layout = QHBoxLayout()
        
        # Create input field with enter key support
        self.input_field = QLineEdit()
        self.input_field.setObjectName('input-field')
        self.input_field.setPlaceholderText("Ask a question...")
        self.input_field.returnPressed.connect(self.handle_submit)
        
        # Create submit button with icon
        self.submit_button = QPushButton("")
        self.submit_icon = QIcon(":icons/send.svg")
        self.submit_button.setIcon(self.submit_icon)
        self.submit_button.setObjectName('submit-button')
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.clicked.connect(self.handle_submit)
        
        # Create loading label (hidden by default)
        self.loading_label = QLabel()
        self.loading_label.setFixedSize(20, 20)
        self.loading_label.setMovie(self.loading_movie)
        self.loading_label.hide()
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.submit_button)
        input_layout.addWidget(self.loading_label)
        
        input_widget.setLayout(input_layout)
        input_widget.setContentsMargins(0, 0, 0, 0)
        input_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        input_widget.setObjectName('input-widget')
        
        self.layout.addWidget(input_widget)
        return input_widget

    def set_loading_state(self, is_loading):
        if is_loading:
            # Disable input and show loading state
            self.input_field.setEnabled(False)
            self.input_field.setStyleSheet("color: gray;")
            self.submit_button.hide()
            self.loading_label.show()
            self.loading_movie.start()
        else:
            # Re-enable input and restore normal state
            self.input_field.setEnabled(True)
            self.input_field.setStyleSheet("")
            self.loading_label.hide()
            self.loading_movie.stop()
            self.submit_button.show()

    def handle_submit(self):
        input_text = self.input_field.text().strip()
        if not input_text:
            return

        self.set_loading_state(True)
        
        # Add prompt widget
        self.prompt_widget(input_text)
        
        # Create and add response widget
        response_layout = QHBoxLayout()
        response_layout.setContentsMargins(0, 0, 0, 0)
        
        response_icon = QLabel()
        icon = QIcon(':/icons/ai_icon.png')
        pixmap = icon.pixmap(20, 20)
        response_icon.setPixmap(pixmap)
        response_icon.setFixedSize(20, 20)
        
        response_label = GrowingTextEdit()
        response_label.setObjectName('response-label')
        response_label.setReadOnly(True)
        
        response_layout.addWidget(response_icon)
        response_layout.addWidget(response_label)
        response_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        response_layout.setAlignment(response_icon, Qt.AlignmentFlag.AlignTop)
        
        response_widget = QWidget()
        response_widget.setObjectName('response-widget')
        response_widget.setLayout(response_layout)
        
        self.response_layout.addWidget(response_widget)
        self.response_layout.setAlignment(response_widget, Qt.AlignmentFlag.AlignTop)

        # Process response chunks
        try:
            for chunk in get_response(input_text):
                lines = chunk.split('\n')
                lines[0] = lines[0].lstrip('\n')
                chunk = '\n'.join(lines)
                response_label.setText(response_label.toPlainText() + chunk)
                contents_height = response_label.document().size().height()
                response_label.setFixedHeight(contents_height + 48)
                QApplication.processEvents()
            
            # Update chat history
            update_chat_history(input_text, response_label.toPlainText())
            
        finally:
            # Restore normal state regardless of success or failure
            self.set_loading_state(False)
            self.clear_input()

    def clear_input(self):
        self.input_field.clear()