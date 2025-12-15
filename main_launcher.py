import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

from Chess.chess_gui import ChessPremiumQt
from Othello.othello_gui import OthelloWindow


class ClickableCard(QFrame):
    def __init__(self, title: str, image_path: str, on_click):
        super().__init__()
        self._on_click = on_click

        self.setObjectName("card")
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        pix = QPixmap(image_path)
        if not pix.isNull():
            img.setPixmap(pix.scaled(240, 240, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            img.setText("Image not found")
            img.setStyleSheet("color:#ff6b6b; font-size:14px;")
        layout.addWidget(img, stretch=1)

        name = QLabel(title)
        name.setAlignment(Qt.AlignCenter)
        name.setObjectName("cardTitle")
        layout.addWidget(name)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setXOffset(0)
        shadow.setYOffset(10)
        shadow.setColor(Qt.black)
        self.setGraphicsEffect(shadow)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._on_click()
        super().mousePressEvent(event)


class GameLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Adversarial-Arena")
        self.setMinimumSize(980, 560)

        self._opened_windows = []

        root = QWidget()
        self.setCentralWidget(root)

        main = QVBoxLayout(root)
        main.setContentsMargins(28, 28, 28, 28)
        main.setSpacing(18)

        title = QLabel("Adversarial-Arena")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setObjectName("header")
        main.addWidget(title)

        subtitle = QLabel("Choose a game to launch")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("subheader")
        main.addWidget(subtitle)

        row = QHBoxLayout()
        row.setSpacing(18)

        othello_card = ClickableCard(
            title="Othello",
            image_path="images\othello_logo.png",
            on_click=self.open_othello
        )
        chess_card = ClickableCard(
            title="Chess",
            image_path="images\chess_logo.png",
            on_click=self.open_chess
        )

        row.addStretch(1)
        row.addWidget(othello_card, stretch=0)
        row.addWidget(chess_card, stretch=0)
        row.addStretch(1)

        main.addLayout(row, stretch=1)

        footer = QLabel("Tip: click a card to launch")
        footer.setAlignment(Qt.AlignCenter)
        footer.setObjectName("footer")
        main.addWidget(footer)

        self.apply_style()

    def apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background: #0b0f19;
                color: #e6e8ee;
                font-family: "Segoe UI";
            }

            QLabel#header {
                color: #ffffff;
                letter-spacing: 0.5px;
            }

            QLabel#subheader {
                color: #a7afc2;
                font-size: 14px;
                margin-bottom: 6px;
            }

            QLabel#footer {
                color: #7f8aa3;
                font-size: 12px;
                margin-top: 10px;
            }

            QFrame#card {
                background: rgba(255, 255, 255, 0.06);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 18px;
                min-width: 320px;
                min-height: 360px;
            }

            QFrame#card:hover {
                background: rgba(255, 255, 255, 0.10);
                border: 1px solid rgba(255, 255, 255, 0.22);
            }

            QLabel#cardTitle {
                font-size: 16px;
                font-weight: 700;
                color: #ffffff;
                padding-top: 6px;
            }
        """)

    def open_chess(self):
        w = ChessPremiumQt()
        w.show()
        self._opened_windows.append(w)

    def open_othello(self):
        w = OthelloWindow()
        w.show()
        self._opened_windows.append(w)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = GameLauncher()
    win.show()
    sys.exit(app.exec_())
