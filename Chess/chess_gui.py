import os
import threading
from copy import deepcopy

from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QObject
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QDialog,
)

from board import Board
from ai import find_best_move_hybrid
from constants import PIECE_VALUES
from zobrist import init_zobrist

try:
    import pygame

    pygame.mixer.init()
    SOUND_ENABLED = True
except Exception:
    pygame = None
    SOUND_ENABLED = False


SQUARE_SIZE = 90
LIGHT_COLOR = "#f0d9b5"
DARK_COLOR = "#b58863"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_PATH = os.path.join(BASE_DIR, "assets", "images", "imgs-80px")
SOUNDS_PATH = os.path.join(BASE_DIR, "assets", "sounds")


class SoundManager:
    def __init__(self):
        self.enabled = SOUND_ENABLED
        self.sounds = {}
        if not self.enabled:
            return

        sound_files = {
            "move": "move_sound.mp3",
            "capture": "capture_sound.mp3",
            "castle": "castle_sound.mp3",
            "check": "check_sound.mp3",
            "checkmate": "checkmate_sound.mp3",
            "stalemate": "stalemate_sound.mp3",
            "start": "start_sound.mp3",
            "pop": "pop.mp3",
        }

        for key, file in sound_files.items():
            path = os.path.join(SOUNDS_PATH, file)
            if os.path.exists(path):
                try:
                    self.sounds[key] = pygame.mixer.Sound(path)
                except Exception:
                    pass

    def play(self, key):
        if not self.enabled:
            return
        snd = self.sounds.get(key)
        if snd is None:
            return
        try:
            snd.play()
        except Exception:
            pass


class WorkerSignals(QObject):
    done = pyqtSignal(object)


class AIWorker(threading.Thread):
    def __init__(self, board_snapshot, depth, signals):
        super().__init__(daemon=True)
        self.board_snapshot = board_snapshot
        self.depth = depth
        self.signals = signals

    def run(self):
        mv = find_best_move_hybrid(self.board_snapshot, self.depth)

        if mv and len(mv) == 4:
            fr, fc, tr, tc = mv
            piece = self.board_snapshot.get_piece(fr, fc)
            if (piece == "P" and tr == 0) or (piece == "p" and tr == 7):
                mv = (fr, fc, tr, tc, "Q")

        self.signals.done.emit(mv)


class PromotionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Promotion")
        self.setModal(True)
        self.setStyleSheet("background:#2b2b2b; color:white;")
        self.result_piece = "Q"

        layout = QVBoxLayout(self)
        title = QLabel("Choose piece:")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)

        btn_row = QHBoxLayout()
        layout.addLayout(btn_row)

        for piece, name in [("Q", "Queen"), ("R", "Rook"), ("B", "Bishop"), ("N", "Knight")]:
            b = QPushButton(name)
            b.setStyleSheet(
                "QPushButton{background:#b58863; color:white; padding:10px; border-radius:8px;}"
                "QPushButton:hover{background:#c89a6b;}"
            )
            b.clicked.connect(lambda _, p=piece: self._pick(p))
            btn_row.addWidget(b)

        self.setFixedSize(360, 140)

    def _pick(self, piece):
        self.result_piece = piece
        self.accept()


class ChessBoardWidget(QWidget):
    squareClicked = pyqtSignal(int, int)

    def __init__(self, get_board_callable, parent=None):
        super().__init__(parent)
        self.get_board = get_board_callable
        self.setFixedSize(QSize(8 * SQUARE_SIZE, 8 * SQUARE_SIZE))

        self.piece_pix = {}
        self.highlight_pix = {}
        self.selected_square = None
        self.target_squares = []

        self._load_images()

    def _load_images(self):
        from pieces import IMAGE_NAME_BY_PIECE

        for piece, file in IMAGE_NAME_BY_PIECE.items():
            possible_paths = [
                os.path.join(IMAGE_PATH, file),
                os.path.join(BASE_DIR, "assets", "images", "imgs-80px", file),
                os.path.join(BASE_DIR, "assets", "images", file),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pm = QPixmap(path)
                    if not pm.isNull():
                        new_size = int(SQUARE_SIZE * 0.85)
                        self.piece_pix[piece] = pm.scaled(
                            new_size, new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
                        )
                    break

        hfiles = {
            "selected": os.path.join(BASE_DIR, "assets", "images", "greenhighlighter.png"),
            "move": os.path.join(BASE_DIR, "assets", "images", "circleOutline.png"),
            "capture": os.path.join(BASE_DIR, "assets", "images", "redhighlighter.png"),
            "en_passant": os.path.join(BASE_DIR, "assets", "images", "bluehighlighter.png"),
        }
        for key, path in hfiles.items():
            if os.path.exists(path):
                pm = QPixmap(path)
                if not pm.isNull():
                    self.highlight_pix[key] = pm.scaled(
                        SQUARE_SIZE, SQUARE_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )

    def setHighlights(self, selected_square, target_squares):
        self.selected_square = selected_square
        self.target_squares = list(target_squares)
        self.update()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return
        x = event.x()
        y = event.y()
        c = x // SQUARE_SIZE
        r = y // SQUARE_SIZE
        if 0 <= r < 8 and 0 <= c < 8:
            self.squareClicked.emit(int(r), int(c))

    def paintEvent(self, _event):
        board = self.get_board()
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)

        light = QColor(LIGHT_COLOR)
        dark = QColor(DARK_COLOR)

        for r in range(8):
            for c in range(8):
                x = c * SQUARE_SIZE
                y = r * SQUARE_SIZE

                is_light = (r + c) % 2 == 0
                p.fillRect(x, y, SQUARE_SIZE, SQUARE_SIZE, light if is_light else dark)

                text_color = QColor(DARK_COLOR) if is_light else QColor(LIGHT_COLOR)
                p.setPen(text_color)
                p.setFont(QFont("Arial", 12, QFont.Bold))
                if r == 7:
                    p.drawText(x + SQUARE_SIZE - 18, y + SQUARE_SIZE - 6, chr(ord("a") + c))
                if c == 0:
                    p.drawText(x + 6, y + 18, str(8 - r))

                if self.selected_square == (r, c):
                    if "selected" in self.highlight_pix:
                        p.drawPixmap(x, y, self.highlight_pix["selected"])
                    else:
                        p.fillRect(x, y, SQUARE_SIZE, SQUARE_SIZE, QColor(0, 255, 0, 60))

                if (r, c) in self.target_squares:
                    target_piece = board.get_piece(r, c)
                    is_en_passant = False

                    if self.selected_square:
                        sel_r, sel_c = self.selected_square
                        sel_piece = board.get_piece(sel_r, sel_c)
                        if sel_piece.upper() == "P":
                            if getattr(board, "en_passant", None) == (r, c) and target_piece == ".":
                                is_en_passant = True

                    if is_en_passant and "en_passant" in self.highlight_pix:
                        p.drawPixmap(x, y, self.highlight_pix["en_passant"])
                    elif target_piece != "." and "capture" in self.highlight_pix:
                        p.drawPixmap(x, y, self.highlight_pix["capture"])
                    elif "move" in self.highlight_pix:
                        p.drawPixmap(x, y, self.highlight_pix["move"])
                    else:
                        pen = QPen(QColor(255, 255, 255, 180))
                        pen.setWidth(3)
                        p.setPen(pen)
                        p.setBrush(Qt.NoBrush)
                        margin = 16 if target_piece == "." else 8
                        p.drawEllipse(
                            x + margin, y + margin, SQUARE_SIZE - 2 * margin, SQUARE_SIZE - 2 * margin
                        )

                piece = board.get_piece(r, c)
                pm = self.piece_pix.get(piece)
                if piece != "." and pm is not None:
                    px = x + (SQUARE_SIZE - pm.width()) // 2
                    py = y + (SQUARE_SIZE - pm.height()) // 2
                    p.drawPixmap(px, py, pm)

        p.end()


class ChessPremiumQt(QMainWindow):
    def __init__(self):
        super().__init__()
        init_zobrist()

        self.setWindowTitle("♔ CHESS ♔")
        self.resize(1200, 850)

        self.board = Board()
        self.game_over = False
        self.selected_square = None
        self.target_squares = []
        self.move_history = []

        self.white_player_type = "Human"
        self.black_player_type = "AI"

        self.white_ai_depth = 3
        self.black_ai_depth = 3
        self.delay_ms = 600
        self.ai_thinking = False
        self.ai_vs_ai_running = False

        self.sounds = SoundManager()

        self._build_ui()
        self._apply_settings_to_mode()
        self._refresh_ui()

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        root.setStyleSheet("#root{background:#1a1a1a;}")

        outer = QHBoxLayout(root)
        outer.setContentsMargins(24, 24, 24, 24)
        outer.setSpacing(22)

        self.board_widget = ChessBoardWidget(lambda: self.board)
        self.board_widget.squareClicked.connect(self.on_square_clicked)
        outer.addWidget(self.board_widget, 0, Qt.AlignVCenter)

        panel = QFrame()
        panel.setFixedWidth(360)
        panel.setObjectName("panel")
        panel.setStyleSheet(
            "#panel{background:#1a1a1a; border-radius:18px;}"
            "QLabel{color:white; font-size:13px;}"
            "QLabel#muted{color:#d0d0d0;}"
            "QComboBox{background:#2b2b2b; color:white; border:1px solid #3a3a3a; border-radius:8px; padding:6px 10px;}"
            "QComboBox::drop-down{border:0; width:28px;}"
            "QComboBox QAbstractItemView{background:#2b2b2b; color:white; selection-background-color:#3a3a3a; border:1px solid #3a3a3a;}"
            "QSpinBox{background:#2b2b2b; color:white; border:1px solid #3a3a3a; border-radius:8px; padding:4px 8px;}"
            "QSlider::groove:horizontal{background:#3a3a3a; height:6px; border-radius:3px;}"
            "QSlider::handle:horizontal{background:#f0d9b5; width:14px; margin:-5px 0; border-radius:7px;}"
            "QPushButton#primary{background:#0b6efd; color:white; border:0; border-radius:12px; padding:12px; font-size:15px; font-weight:bold;}"
            "QPushButton#primary:hover{background:#0a58ca;}"
            "QPushButton#primary:pressed{background:#084298;}"
        )

        right = QVBoxLayout(panel)
        right.setContentsMargins(18, 18, 18, 18)
        right.setSpacing(12)

        title = QLabel("CHESS")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color:#f0d9b5;")
        right.addWidget(title)

        self.lbl_turn = QLabel("")
        self.lbl_turn.setAlignment(Qt.AlignCenter)
        self.lbl_turn.setFont(QFont("Arial", 13, QFont.Bold))
        self.lbl_turn.setStyleSheet("color:white;")
        right.addWidget(self.lbl_turn)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#333333; background:#333333;")
        sep.setFixedHeight(1)
        right.addWidget(sep)

        self.cmb_white_type = QComboBox()
        self.cmb_white_type.addItems(["Human", "AI"])
        self.cmb_white_type.setCurrentText(self.white_player_type)
        self.cmb_white_type.currentTextChanged.connect(self._on_settings_changed)

        self.spn_white_depth = QSpinBox()
        self.spn_white_depth.setRange(1, 6)
        self.spn_white_depth.setValue(self.white_ai_depth)
        self.spn_white_depth.valueChanged.connect(self._on_settings_changed)

        self.cmb_black_type = QComboBox()
        self.cmb_black_type.addItems(["Human", "AI"])
        self.cmb_black_type.setCurrentText(self.black_player_type)
        self.cmb_black_type.currentTextChanged.connect(self._on_settings_changed)

        self.spn_black_depth = QSpinBox()
        self.spn_black_depth.setRange(1, 6)
        self.spn_black_depth.setValue(self.black_ai_depth)
        self.spn_black_depth.valueChanged.connect(self._on_settings_changed)

        def block(label_txt, widget1, widget2=None):
            box = QFrame()
            box.setStyleSheet("QFrame{background:transparent;}")
            l = QVBoxLayout(box)
            l.setContentsMargins(0, 0, 0, 0)
            l.setSpacing(6)

            lbl = QLabel(label_txt)
            lbl.setFont(QFont("Arial", 11, QFont.Bold))
            lbl.setStyleSheet("color:#dddddd;")
            l.addWidget(lbl)

            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(10)
            row.addWidget(widget1, 1)

            if widget2 is not None:
                row.addWidget(widget2, 0)

            l.addLayout(row)
            return box

        self.cmb_white_type.setStyleSheet("QComboBox{padding:8px; border-radius:8px; background:#2b2b2b;}")
        self.cmb_black_type.setStyleSheet("QComboBox{padding:8px; border-radius:8px; background:#2b2b2b;}")
        self.spn_white_depth.setStyleSheet("QSpinBox{padding:8px; border-radius:8px; background:#2b2b2b;}")
        self.spn_black_depth.setStyleSheet("QSpinBox{padding:8px; border-radius:8px; background:#2b2b2b;}")

        right.addWidget(block("White player type:", self.cmb_white_type, self.spn_white_depth))
        right.addWidget(block("Black player type:", self.cmb_black_type, self.spn_black_depth))

        self.delay_slider = QSlider(Qt.Horizontal)
        self.delay_slider.setRange(0, 2000)
        self.delay_slider.setValue(self.delay_ms)
        self.delay_slider.valueChanged.connect(self._on_settings_changed)
        self.delay_value = QLabel(str(self.delay_ms))
        self.delay_value.setFixedWidth(54)
        self.delay_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.delay_value.setFont(QFont("Arial", 11, QFont.Bold))
        self.delay_value.setStyleSheet("color:#f0d9b5;")

        delay_box = QFrame()
        dl = QVBoxLayout(delay_box)
        dl.setContentsMargins(0, 0, 0, 0)
        dl.setSpacing(6)
        lbl_delay = QLabel("AI vs AI move delay (ms):")
        lbl_delay.setFont(QFont("Arial", 11, QFont.Bold))
        lbl_delay.setStyleSheet("color:#dddddd;")
        dl.addWidget(lbl_delay)

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)
        row.addWidget(self.delay_slider, 1)
        row.addWidget(self.delay_value, 0)
        dl.addLayout(row)
        right.addWidget(delay_box)

        self.btn_new = QPushButton("New Game")
        self.btn_new.setObjectName("primary")
        self.btn_new.setFixedHeight(52)
        self.btn_new.setCursor(Qt.PointingHandCursor)
        self.btn_new.setFont(QFont("Arial", 13, QFont.Bold))
        self.btn_new.clicked.connect(self.start_new_game)
        right.addWidget(self.btn_new)

        self.lbl_status = QLabel("")
        self.lbl_status.setWordWrap(True)
        self.lbl_status.setFont(QFont("Arial", 11, QFont.Bold))
        self.lbl_status.setStyleSheet("color:white;")
        right.addWidget(self.lbl_status)

        right.addStretch(1)

        self.lbl_score = QLabel("")
        self.lbl_score.setAlignment(Qt.AlignCenter)
        self.lbl_score.setFont(QFont("Arial", 11, QFont.Bold))
        self.lbl_score.setStyleSheet("color:#f0d9b5;")
        right.addWidget(self.lbl_score)

        outer.addWidget(panel)

        self.setCentralWidget(root)

    def _on_settings_changed(self, *_):
        self.white_player_type = self.cmb_white_type.currentText()
        self.black_player_type = self.cmb_black_type.currentText()
        self.white_ai_depth = int(self.spn_white_depth.value())
        self.black_ai_depth = int(self.spn_black_depth.value())
        self.delay_ms = int(self.delay_slider.value())
        self.delay_value.setText(str(self.delay_ms))
        self._apply_settings_to_mode()
        self._refresh_ui()

    def _apply_settings_to_mode(self):
        w = self.white_player_type
        b = self.black_player_type
        if w == "Human" and b == "Human":
            self.mode = "pvp"
            self.human_color = None
            self.ai_color = None
        elif w == "AI" and b == "AI":
            self.mode = "aivai"
            self.human_color = None
            self.ai_color = None
        else:
            self.mode = "pvai"
            if w == "Human":
                self.human_color = "w"
                self.ai_color = "b"
            else:
                self.human_color = "b"
                self.ai_color = "w"

        self.spn_white_depth.setEnabled(self.white_player_type == "AI")
        self.spn_black_depth.setEnabled(self.black_player_type == "AI")
        self.delay_slider.setEnabled(self.mode == "aivai")
        self.delay_value.setEnabled(self.mode == "aivai")

    def _sync_highlights(self):
        self.board_widget.setHighlights(self.selected_square, self.target_squares)

    def _material_score(self):
        white = 0
        black = 0
        for r in range(8):
            for c in range(8):
                p = self.board.get_piece(r, c)
                if p == ".":
                    continue
                val = PIECE_VALUES.get(p.upper(), 0)
                if p.isupper():
                    white += val
                else:
                    black += val
        return white, black

    def _refresh_ui(self):
        turn = "White" if self.board.side_to_move == "w" else "Black"
        self.lbl_turn.setText(f"{turn} to move")

        wmat, bmat = self._material_score()
        self.lbl_score.setText(f"Material  White: {wmat}  |  Black: {bmat}")

        if self.game_over:
            return

        if self.ai_thinking:
            return

        if self.mode == "aivai":
            self.lbl_status.setText("AI vs AI mode")
        elif self.mode == "pvp":
            self.lbl_status.setText("Multiplayer mode")
        else:
            hc = "White" if self.human_color == "w" else "Black"
            self.lbl_status.setText(f"vs Computer (Human: {hc})")

        self._sync_highlights()
        self.board_widget.update()

    def start_new_game(self):
        self.sounds.play("start")

        self.board = Board()
        self.game_over = False
        self.ai_thinking = False
        self.ai_vs_ai_running = False

        self.selected_square = None
        self.target_squares = []
        self.move_history = []

        self._apply_settings_to_mode()
        self._sync_highlights()
        self._refresh_ui()

        if self.mode == "pvai" and self.board.side_to_move == self.ai_color:
            QTimer.singleShot(350, self.ai_move_for_current_side)
        elif self.mode == "aivai":
            self.ai_vs_ai_running = True
            QTimer.singleShot(350, self.ai_move_for_current_side)

    def on_square_clicked(self, r, c):
        if self.game_over or self.mode == "aivai":
            return

        color_to_move = self.board.side_to_move

        if self.mode == "pvai" and color_to_move != self.human_color:
            return

        piece = self.board.get_piece(r, c)

        if self.selected_square is None:
            if piece == "." or self.board.color_of(piece) != color_to_move:
                return
            self.select_square(r, c)
            return

        if self.selected_square == (r, c):
            self.selected_square = None
            self.target_squares = []
            self._sync_highlights()
            return

        if self.try_move(self.selected_square, (r, c)):
            self.selected_square = None
            self.target_squares = []
            self._sync_highlights()

            if not self.game_over and self.mode == "pvai":
                QTimer.singleShot(250, self.ai_move_for_current_side)
        else:
            if piece != "." and self.board.color_of(piece) == color_to_move:
                self.select_square(r, c)

    def select_square(self, r, c):
        self.selected_square = (r, c)
        self.target_squares = []

        legal = self.board.generate_legal_moves(self.board.side_to_move)
        for mv in legal:
            fr, fc, tr, tc = mv[:4]
            if (fr, fc) == (r, c):
                self.target_squares.append((tr, tc))

        self._sync_highlights()

    def try_move(self, from_sq, to_sq):
        fr, fc = from_sq
        tr, tc = to_sq
        legal = self.board.generate_legal_moves(self.board.side_to_move)

        mv = None
        for m in legal:
            if m[:4] == (fr, fc, tr, tc):
                mv = m
                break

        if mv is None:
            return False

        if self.board.is_promotion_move(mv):
            dlg = PromotionDialog(self)
            promo = "Q"
            if dlg.exec_() == QDialog.Accepted:
                promo = dlg.result_piece
            mv = (fr, fc, tr, tc, promo)

        self.apply_move(mv)
        return True

    def apply_move(self, mv):
        if mv is None:
            return

        fr, fc, tr, tc = mv[:4]
        captured = self.board.get_piece(tr, tc)
        piece = self.board.get_piece(fr, fc)

        if piece.upper() == "K" and abs(tc - fc) == 2:
            self.sounds.play("castle")
        elif captured != ".":
            self.sounds.play("capture")
        else:
            self.sounds.play("move")

        st = self.board.make_move(mv)
        self.move_history.append((mv, st))

        self._sync_highlights()
        self.board_widget.update()

        if self.board.in_check(self.board.side_to_move):
            self.sounds.play("check")

        if self.check_draw_rules():
            self._refresh_ui()
            return

        self.check_game_end()
        self._refresh_ui()

    def check_draw_rules(self):
        if self.board.is_threefold():
            self.game_over = True
            self.sounds.play("stalemate")
            QMessageBox.information(self, "Draw", "Threefold Repetition")
            return True
        if self.board.is_fifty_move_rule():
            self.game_over = True
            self.sounds.play("stalemate")
            QMessageBox.information(self, "Draw", "50-move Rule")
            return True
        if self.board.is_insufficient_material():
            self.game_over = True
            self.sounds.play("stalemate")
            QMessageBox.information(self, "Draw", "Insufficient Material")
            return True
        return False

    def check_game_end(self):
        if self.game_over:
            return True

        moves = self.board.generate_legal_moves(self.board.side_to_move)
        if moves:
            return False

        if self.board.in_check(self.board.side_to_move):
            winner = self.board.opp(self.board.side_to_move)
            msg = f"Checkmate! {winner.upper()} wins"
            self.sounds.play("checkmate")
        else:
            msg = "Stalemate"
            self.sounds.play("stalemate")

        self.game_over = True
        self.ai_vs_ai_running = False
        QMessageBox.information(self, "Game Over", msg)
        return True

    def ai_move_for_current_side(self):
        if self.game_over:
            return

        if self.mode == "pvai" and self.board.side_to_move != self.ai_color:
            return

        if self.mode == "aivai" and not self.ai_vs_ai_running:
            return

        legal = self.board.generate_legal_moves(self.board.side_to_move)
        if not legal:
            self.check_game_end()
            self._refresh_ui()
            return

        if self.ai_thinking:
            return

        self.ai_thinking = True

        if self.mode == "aivai":
            depth = self.white_ai_depth if self.board.side_to_move == "w" else self.black_ai_depth
        else:
            depth = self.black_ai_depth if self.ai_color == "b" else self.white_ai_depth

        side = "White" if self.board.side_to_move == "w" else "Black"
        self.lbl_status.setText(f"{side} AI thinking... (Depth {depth})")

        snapshot = deepcopy(self.board)
        signals = WorkerSignals()
        signals.done.connect(self._on_ai_done)
        worker = AIWorker(snapshot, depth, signals)
        worker.start()

    def _on_ai_done(self, mv):
        if self.game_over:
            self.ai_thinking = False
            return

        self.apply_move(mv)
        self.ai_thinking = False

        if self.mode == "aivai" and self.ai_vs_ai_running and not self.game_over:
            QTimer.singleShot(self.delay_ms, self.ai_move_for_current_side)


def main():
    import sys

    app = QApplication(sys.argv)
    win = ChessPremiumQt()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
