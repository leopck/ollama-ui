import json
import rc_icons
from PySide6.QtCore import Qt, QSize
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
        self.response_layout.setAlignment(Qt.Alignment.AlignTop)
        self.response_widget.setLayout(self.response_layout)

        self.response_scroll_area = QScrollArea()
        self.response_scroll_area.setWidgetResizable(True)
        self.response_scroll_area.setWidget(self.response_widget)

        self.layout.addWidget(self.response_scroll_area)
        self.input_widget = self.input_widget()
        self.input_widget.setEnabled(False)

    def input_widget(self):
        input_widget = QWidget()
        input_layout = QHBoxLayout()
        input_field = QLineEdit()
        input_field.setObjectName('input-field')
        input_field.setPlaceholderText("Ask a question...")
        input_field.returnPressed.connect(self.submit_button_clicked)  # Add enter key support

        self.submit_button = QPushButton("")
        icon = QIcon(":icons/send.svg")
        self.submit_button.setIcon(icon)
        self.submit_button.setObjectName('submit-button')
        self.submit_button.setCursor(Qt.PointingHandCursor)

        # Create loading spinner
        self.spinner_label = QLabel()
        self.spinner_movie = QMovie("icons/spinner.gif")
        self.spinner_movie.setScaledSize(QSize(20, 20))
        self.spinner_label.setMovie(self.spinner_movie)
        self.spinner_label.hide()  # Hide spinner initially

        self.submit_button.clicked.connect(self.submit_button_clicked)
        input_layout.addWidget(input_field)
        input_layout.addWidget(self.submit_button)
        input_layout.addWidget(self.spinner_label)
        input_widget.setLayout(input_layout)
        input_widget.setContentsMargins(0, 0, 0, 0)
        input_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        input_widget.setObjectName('input-widget')
        return input_widget

    def submit_button_clicked(self):
        input_text = self.get_input()
        
        # Show loading state
        input_widget = self.layout.itemAt(1).widget()
        input_field = input_widget.layout().itemAt(0).widget()
        input_field.setEnabled(False)
        input_field.setStyleSheet("color: gray;")
        self.submit_button.hide()
        self.spinner_label.show()
        self.spinner_movie.start()

        # Add prompt widget and create response widget as before
        prompt_layout = QHBoxLayout()
        prompt_layout.setContentsMargins(0, 0, 0, 0)
        prompt_icon = QLabel()
        icon = QIcon(':/icons/user_icon.svg')
        pixmap = icon.pixmap(20, 20)
        prompt_icon.setPixmap(pixmap)
        prompt_icon.setFixedSize(20, 20)

        prompt_label = GrowingTextEdit(input_text)
        prompt_label.setObjectName('prompt-label')
        prompt_label.setReadOnly(True)

        prompt_layout.addWidget(prompt_icon)
        prompt_layout.addWidget(prompt_label)
        prompt_layout.setAlignment(Qt.AlignTop)
        prompt_layout.setAlignment(prompt_icon, Qt.AlignTop)
        prompt_widget = QWidget()
        prompt_widget.setObjectName('prompt-widget')
        prompt_widget.setLayout(prompt_layout)
        self.response_layout.addWidget(prompt_widget)
        self.response_layout.setAlignment(prompt_widget, Qt.AlignTop)

        # Response widget creation
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
        response_layout.setAlignment(Qt.AlignTop)
        response_layout.setAlignment(response_icon, Qt.AlignTop)
        response_widget = QWidget()
        response_widget.setObjectName('response-widget')
        response_widget.setLayout(response_layout)
        self.response_layout.addWidget(response_widget)
        self.response_layout.setAlignment(response_widget, Qt.AlignTop)

        try:
            for chunk in get_response(input_text):
                lines = chunk.split('\n')
                lines[0] = lines[0].lstrip('\n')
                chunk = '\n'.join(lines)
                response_label.setText(response_label.toPlainText() + chunk)
                contents_height = response_label.document().size().height()
                response_label.setFixedHeight(contents_height+48)
                QApplication.processEvents()
            response_label.setText(response_label.toPlainText())
            contents_height = response_label.document().size().height()
            response_label.setFixedHeight(contents_height+48)
            update_chat_history(input_text, response_label.toPlainText())
        finally:
            # Restore normal state
            input_field.setEnabled(True)
            input_field.setStyleSheet("")
            self.spinner_label.hide()
            self.spinner_movie.stop()
            self.submit_button.show()
            self.clear_input()

    def clear_input(self):
        self.input_field.clear()