import sys
import os

from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QTextEdit,
    QTextBrowser,
    QFrame,
    QSizePolicy,
    QFileDialog
)

from ai_backend import analyze_screenshot
from PySide6.QtCore import Qt, QThread, QObject, Signal, Slot
from PySide6.QtGui import QPixmap
from PIL import ImageGrab
from PySide6.QtWidgets import QRubberBand


class ScreenshotSelector(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint
        )

        self.setWindowState(Qt.WindowFullScreen)
        self.setWindowOpacity(0.3)

        self.origin = None

        self.rubber_band = QRubberBand(
            QRubberBand.Rectangle,
            self
        )

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            self.origin = event.position().toPoint()

            self.rubber_band.setGeometry(
                self.origin.x(),
                self.origin.y(),
                0,
                0
            )

            self.rubber_band.show()

    def mouseMoveEvent(self, event):

        if self.origin:

            current = event.position().toPoint()

            x = min(self.origin.x(), current.x())
            y = min(self.origin.y(), current.y())

            width = abs(current.x() - self.origin.x())
            height = abs(current.y() - self.origin.y())

            self.rubber_band.setGeometry(
                x,
                y,
                width,
                height
            )

    def mouseReleaseEvent(self, event):

        if event.button() == Qt.LeftButton:

            current = event.position().toPoint()

            x = min(self.origin.x(), current.x())
            y = min(self.origin.y(), current.y())

            width = abs(current.x() - self.origin.x())
            height = abs(current.y() - self.origin.y())

            if width > 10 and height > 10:

                screenshot = ImageGrab.grab(
                    bbox=(
                        x,
                        y,
                        x + width,
                        y + height
                    )
                )

                screenshot_path = "captured_region.png"

                screenshot.save(screenshot_path)

                global selected_image
                selected_image = screenshot_path

                # Add captured screenshot to history
                history_list.insertItem(
                    0,
                    "Captured Screenshot"
                )

                pixmap = QPixmap(screenshot_path)

                scaled_pixmap = pixmap.scaled(
                    preview.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )

                preview.setPixmap(scaled_pixmap)

            self.rubber_band.hide()
            self.close()


class AIWorker(QObject):

    finished = Signal(str)
    error = Signal(str)

    def __init__(self, image_path, action, question=""):
        super().__init__()

        self.image_path = image_path
        self.action = action
        self.question = question

    def run(self):

        try:

            result = analyze_screenshot(
                self.image_path,
                self.action,
                self.question
            )

            self.finished.emit(result)

        except Exception as error:

            self.error.emit(str(error))


class AIUIHandler(QObject):

    @Slot(str)
    def handle_result(self, result):
        status_label.setText("● AI READY")

        status_label.setStyleSheet("""
            QLabel {
                color: #8b7cff;
                background: transparent;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 15px;
            }
        """)
        result_box.setMarkdown(result)

        analyze_button.setEnabled(True)
        explain_button.setEnabled(True)
        summarize_button.setEnabled(True)
        error_button.setEnabled(True)
        extract_button.setEnabled(True)
        research_button.setEnabled(True)

    @Slot(str)
    def handle_error(self, error):
        status_label.setText("● AI READY")

        status_label.setStyleSheet("""
            QLabel {
                color: #8b7cff;
                background: transparent;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 15px;
            }
        """)
        result_box.setText(
            f"Something went wrong:\n\n{error}"
        )

        analyze_button.setEnabled(True)
        explain_button.setEnabled(True)
        summarize_button.setEnabled(True)
        error_button.setEnabled(True)
        extract_button.setEnabled(True)
        research_button.setEnabled(True)


# --------------------------------------------------
# APPLICATION
# --------------------------------------------------

app = QApplication(sys.argv)

app.setStyleSheet("""
    QWidget {
        background-color: #121212;
        color: #ffffff;
        font-family: Arial;
        font-size: 14px;
    }

    QLabel {
        color: #ffffff;
    }

    QPushButton {
        background-color: #242424;
        color: #ffffff;
        border: 1px solid #3a3a3a;
        border-radius: 8px;
        padding: 10px;
    }

    QPushButton:hover {
        background-color: #333333;
    }

    QPushButton:pressed {
        background-color: #444444;
    }

    QPushButton:disabled {
        color: #777777;
        background-color: #1c1c1c;
    }

    QTextEdit {
        background-color: #1b1b1b;
        color: #ffffff;
        border: 1px solid #3a3a3a;
        border-radius: 8px;
        padding: 8px;
    }

    QFrame {
        background-color: #15151f;
    }

    #previewCard {
        background-color: #181822;
        border: 1px solid #2d2d3d;
        border-radius: 16px;
    }
""")


window = QWidget()
window.setWindowTitle("SnapperAI")
window.resize(1000, 800)

selected_image = None


# --------------------------------------------------
# MAIN LAYOUT
# --------------------------------------------------

main_layout = QHBoxLayout()

main_layout.setContentsMargins(
    0,
    0,
    0,
    0
)

main_layout.setSpacing(0)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

sidebar = QFrame()
sidebar.setFixedWidth(210)

sidebar_layout = QVBoxLayout()

sidebar_layout.setContentsMargins(
    20,
    25,
    20,
    25
)

sidebar_layout.setSpacing(12)

sidebar.setLayout(sidebar_layout)


# Logo

logo = QLabel("⚡ SnapperAI")

logo.setStyleSheet("""
    QLabel {
        font-size: 22px;
        font-weight: bold;
        color: white;
        padding: 10px 0 25px 5px;
    }
""")

sidebar_layout.addWidget(logo)


# Navigation buttons

home_button = QPushButton("⌂   Home")
capture_nav = QPushButton("▣   Screenshot")
research_nav = QPushButton("⌕   Research")


for button in [
    home_button,
    capture_nav,
    research_nav
]:

    button.setMinimumHeight(42)

    button.setStyleSheet("""
        QPushButton {
            background-color: transparent;
            color: #8f8fa3;
            border: none;
            border-radius: 10px;
            text-align: left;
            padding-left: 12px;
            font-size: 14px;
        }

        QPushButton:hover {
            background-color: #242432;
            color: white;
        }
    """)


sidebar_layout.addWidget(home_button)
sidebar_layout.addWidget(capture_nav)
sidebar_layout.addWidget(research_nav)


# --------------------------------------------------
# HISTORY
# --------------------------------------------------

history_label = QLabel("RECENT")

history_label.setStyleSheet("""
    QLabel {
        color: #66667a;
        font-size: 11px;
        font-weight: bold;
        padding: 15px 5px 5px 5px;
    }
""")

sidebar_layout.addWidget(history_label)


history_list = QListWidget()

history_list.setMaximumHeight(150)

history_list.setStyleSheet("""
    QListWidget {
        background: transparent;
        border: none;
        color: #aaaaaa;
        font-size: 12px;
    }

    QListWidget::item {
        padding: 8px;
        border-radius: 8px;
    }

    QListWidget::item:hover {
        background-color: #242432;
        color: white;
    }

    QListWidget::item:selected {
        background-color: #29263d;
        color: white;
    }
""")

sidebar_layout.addWidget(history_list)


# Active Home button

home_button.setStyleSheet("""
    QPushButton {
        background-color: #29263d;
        color: white;
        border: 1px solid #3d385c;
        border-radius: 10px;
        text-align: left;
        padding-left: 12px;
        font-size: 14px;
        font-weight: bold;
    }
""")


sidebar_layout.addStretch()


# --------------------------------------------------
# MAIN CONTENT
# --------------------------------------------------

content = QWidget()

content_layout = QVBoxLayout()

content_layout.setContentsMargins(
    35,
    25,
    35,
    25
)

content_layout.setSpacing(15)

content.setLayout(content_layout)

main_layout.addWidget(sidebar)
main_layout.addWidget(content)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

header_layout = QHBoxLayout()


title = QLabel("SnapperAI")

title.setStyleSheet("""
    QLabel {
        font-size: 38px;
        font-weight: bold;
        color: white;
        background: transparent;
        padding: 15px;
    }
""")


status_label = QLabel("● AI READY")

status_label.setAlignment(Qt.AlignCenter)

status_label.setStyleSheet("""
    QLabel {
        color: #8b7cff;
        background: transparent;
        font-size: 14px;
        font-weight: bold;
        padding: 10px 15px;
    }
""")


header_layout.addWidget(title)
header_layout.addStretch()
header_layout.addWidget(status_label)

content_layout.addLayout(header_layout)


# Subtitle

subtitle = QLabel("Your AI Screenshot Assistant")

subtitle.setAlignment(Qt.AlignCenter)

subtitle.setStyleSheet("""
    QLabel {
        font-size: 16px;
        color: #aaaaaa;
        background: transparent;
        padding-bottom: 15px;
    }
""")

content_layout.addWidget(subtitle)


# --------------------------------------------------
# SCREENSHOT PREVIEW
# --------------------------------------------------

preview = QLabel(
    "Screenshot Preview\n\nNo screenshot selected"
)

preview.setAlignment(Qt.AlignCenter)

preview.setFixedHeight(300)

preview.setSizePolicy(
    QSizePolicy.Expanding,
    QSizePolicy.Fixed
)

preview.setStyleSheet("""
    QLabel {
        background-color: #181822;
        color: #777788;
        border: 1px solid #2d2d3d;
        border-radius: 16px;
        padding: 20px;
        font-size: 15px;
    }
""")


preview_card = QFrame()

preview_card.setObjectName(
    "previewCard"
)


preview_card_layout = QVBoxLayout()

preview_card_layout.setContentsMargins(
    0,
    0,
    0,
    0
)


preview_card_layout.addWidget(
    preview
)

preview_card.setLayout(
    preview_card_layout
)

content_layout.addWidget(
    preview_card
)


# --------------------------------------------------
# SCREENSHOT BUTTONS
# --------------------------------------------------

capture_layout = QHBoxLayout()


capture_button = QPushButton(
    "📸 Capture Screenshot"
)

select_button = QPushButton(
    "📷 Select Screenshot"
)


for button in [
    capture_button,
    select_button
]:

    button.setMinimumHeight(48)

    button.setStyleSheet("""
        QPushButton {
            background-color: #242432;
            color: #ffffff;
            border: 1px solid #38384d;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
        }

        QPushButton:hover {
            background-color: #303047;
            border: 1px solid #555577;
        }

        QPushButton:pressed {
            background-color: #3a3a55;
        }
    """)


capture_layout.addWidget(
    capture_button
)

capture_layout.addWidget(
    select_button
)

content_layout.addLayout(
    capture_layout
)


# --------------------------------------------------
# ACTION LABEL
# --------------------------------------------------

question_label = QLabel(
    "What would you like to do?"
)

question_label.setStyleSheet(
    "font-size: 18px; font-weight: bold;"
)

content_layout.addWidget(
    question_label
)


# --------------------------------------------------
# ACTION BUTTONS
# --------------------------------------------------

button_layout = QHBoxLayout()


explain_button = QPushButton("Explain")
summarize_button = QPushButton("Summarize")
error_button = QPushButton("Find Error")
extract_button = QPushButton("Extract")
research_button = QPushButton("Research")


for button in [
    explain_button,
    summarize_button,
    error_button,
    extract_button,
    research_button
]:

    button.setMinimumHeight(48)

    button.setStyleSheet("""
        QPushButton {
            background-color: #1b1b26;
            color: #d0d0dc;
            border: 1px solid #303044;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 500;
        }

        QPushButton:hover {
            background-color: #252538;
            border: 1px solid #555577;
            color: white;
        }

        QPushButton:pressed {
            background-color: #30304a;
        }
    """)


button_layout.addWidget(explain_button)
button_layout.addWidget(summarize_button)
button_layout.addWidget(error_button)
button_layout.addWidget(extract_button)
button_layout.addWidget(research_button)

content_layout.addLayout(
    button_layout
)


# --------------------------------------------------
# CUSTOM QUESTION
# --------------------------------------------------

ask_box = QTextEdit()

ask_box.setPlaceholderText(
    "Ask anything about this screenshot..."
)

ask_box.setMaximumHeight(70)

ask_box.setStyleSheet("""
    QTextEdit {
        background-color: #181822;
        color: #ffffff;
        border: 1px solid #303044;
        border-radius: 12px;
        padding: 12px;
        font-size: 14px;
    }

    QTextEdit:focus {
        border: 1px solid #555577;
    }
""")

content_layout.addWidget(
    ask_box
)


# --------------------------------------------------
# ANALYZE BUTTON
# --------------------------------------------------

analyze_button = QPushButton(
    "Analyze Screenshot"
)

analyze_button.setStyleSheet("""
    QPushButton {
        background-color: #6c5ce7;
        color: white;
        border: none;
        border-radius: 12px;
        font-size: 15px;
        font-weight: bold;
        padding: 12px;
    }

    QPushButton:hover {
        background-color: #7c6ff0;
    }

    QPushButton:pressed {
        background-color: #5a4dcc;
    }

    QPushButton:disabled {
        background-color: #29263d;
        color: #777777;
    }
""")

analyze_button.setMinimumHeight(42)

content_layout.addWidget(
    analyze_button
)


# --------------------------------------------------
# AI RESULT
# --------------------------------------------------

result_label = QLabel(
    "AI Result"
)

result_label.setStyleSheet("""
    QLabel {
        font-size: 18px;
        font-weight: bold;
        color: #dcdcec;
        padding-top: 8px;
        padding-bottom: 4px;
        border: none;
    }
""")

content_layout.addWidget(
    result_label
)


result_box = QTextBrowser()

result_box.setOpenExternalLinks(True)
result_box.setReadOnly(True)

result_box.setPlaceholderText(
    "The AI response will appear here..."
)

result_box.setMinimumHeight(150)

result_box.setStyleSheet("""
    QTextBrowser {
        background-color: #181822;
        color: #dddded;
        border: 1px solid #303044;
        border-radius: 14px;
        padding: 14px;
        font-size: 14px;
    }
""")

content_layout.addWidget(
    result_box
)


ui_handler = AIUIHandler()


# --------------------------------------------------
# SELECT SCREENSHOT
# --------------------------------------------------

def select_screenshot():

    file_path, _ = QFileDialog.getOpenFileName(
        window,
        "Select Screenshot",
        "",
        "Images (*.png *.jpg *.jpeg *.webp)"
    )

    if file_path:

        global selected_image

        selected_image = file_path

        # Add screenshot to history
        history_list.insertItem(
            0,
            file_path
        )

        pixmap = QPixmap(
            file_path
        )

        scaled_pixmap = pixmap.scaled(
            preview.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        preview.setPixmap(
            scaled_pixmap
        )


# --------------------------------------------------
# LOAD HISTORY ITEM
# --------------------------------------------------

def load_history_item(item):

    global selected_image

    file_path = item.text()

    if file_path == "Captured Screenshot":

        file_path = "captured_region.png"

    if not os.path.exists(file_path):

        result_box.setText(
            "Screenshot file no longer exists."
        )

        return

    selected_image = file_path

    pixmap = QPixmap(
        file_path
    )

    scaled_pixmap = pixmap.scaled(
        preview.size(),
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation
    )

    preview.setPixmap(
        scaled_pixmap
    )


# --------------------------------------------------
# CAPTURE SCREENSHOT
# --------------------------------------------------

def capture_screenshot():

    selector = ScreenshotSelector()

    selector.show()
    selector.raise_()
    selector.activateWindow()


# --------------------------------------------------
# CHOOSE ACTION
# --------------------------------------------------

def choose_action(action):

    if selected_image is None:

        result_box.setText(
            "Please select a screenshot first."
        )

        return

    start_ai(
        action,
        ""
    )


# --------------------------------------------------
# START AI
# --------------------------------------------------

def start_ai(action, question):

    result_box.setText(
        "🤖 Analyzing screenshot..."
    )
    status_label.setText("● AI IS WORKING")
    status_label.setStyleSheet("""
        QLabel {
            color: #f0a64b;
            background: transparent;
            font-size: 14px;
            font-weight: bold;
            padding: 10px 15px;
        }
    """)
    analyze_button.setEnabled(False)
    explain_button.setEnabled(False)
    summarize_button.setEnabled(False)
    error_button.setEnabled(False)
    extract_button.setEnabled(False)
    research_button.setEnabled(False)


    window.ai_thread = QThread()

    window.ai_worker = AIWorker(
        selected_image,
        action,
        question
    )


    window.ai_worker.moveToThread(
        window.ai_thread
    )


    window.ai_thread.started.connect(
        window.ai_worker.run
    )


    window.ai_worker.finished.connect(
        ui_handler.handle_result
    )

    window.ai_worker.error.connect(
        ui_handler.handle_error
    )


    window.ai_worker.finished.connect(
        window.ai_thread.quit
    )

    window.ai_worker.error.connect(
        window.ai_thread.quit
    )


    window.ai_thread.finished.connect(
        window.ai_worker.deleteLater
    )

    window.ai_thread.finished.connect(
        window.ai_thread.deleteLater
    )


    window.ai_thread.start()


# --------------------------------------------------
# CUSTOM ANALYZE
# --------------------------------------------------

def analyze():

    if selected_image is None:

        result_box.setText(
            "Please select a screenshot first."
        )

        return


    question = ask_box.toPlainText()


    if not question.strip():

        result_box.setText(
            "Please enter a question first."
        )

        return


    start_ai(
        "",
        question
    )


# --------------------------------------------------
# BUTTON CONNECTIONS
# --------------------------------------------------

select_button.clicked.connect(
    select_screenshot
)

capture_button.clicked.connect(
    capture_screenshot
)


analyze_button.clicked.connect(
    analyze
)


explain_button.clicked.connect(
    lambda: choose_action("Explain")
)

summarize_button.clicked.connect(
    lambda: choose_action("Summarize")
)

error_button.clicked.connect(
    lambda: choose_action("Find Error")
)

extract_button.clicked.connect(
    lambda: choose_action("Extract")
)

research_button.clicked.connect(
    lambda: choose_action("Research")
)


# --------------------------------------------------
# SIDEBAR NAVIGATION
# --------------------------------------------------

home_button.clicked.connect(
    lambda: result_box.clear()
)

capture_nav.clicked.connect(
    capture_screenshot
)

research_nav.clicked.connect(
    lambda: choose_action("Research")
)


# --------------------------------------------------
# CLICKABLE HISTORY
# --------------------------------------------------

history_list.itemClicked.connect(
    load_history_item
)


# --------------------------------------------------
# SHOW WINDOW
# --------------------------------------------------

window.setLayout(
    main_layout
)

window.show()

sys.exit(
    app.exec()
)