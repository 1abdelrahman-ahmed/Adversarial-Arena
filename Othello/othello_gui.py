import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QTimer

from constants import BLACK, WHITE, EMPTY, opponent
from board import Board
from ai import AI


BOARD_SIZE = 8


class OthelloWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Othello / Reversi - PyQt5")
        self.setMinimumSize(800, 520)

        self.board = Board()
        self.ai = AI(depth=4)
        self.current_player = BLACK

        self.black_type = "Human"
        self.white_type = "AI"

        self.buttons = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        self._init_ui()
        self.update_board_view()

    # ---------------- UI SETUP ---------------- #
    def _init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout()
        central.setLayout(main_layout)

        # Left: board
        board_widget = QWidget()
        board_layout = QGridLayout()
        board_layout.setSpacing(3)
        board_widget.setLayout(board_layout)
        board_widget.setStyleSheet(
            "background-color: #006633; padding: 6px; border-radius: 8px;"
        )

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                btn = QPushButton("")
                btn.setFixedSize(60, 60)
                btn.setFocusPolicy(Qt.NoFocus)
                btn.clicked.connect(self._make_cell_handler(r, c))
                # base style for empty cell (green board)
                btn.setStyleSheet(self._cell_base_style())
                board_layout.addWidget(btn, r, c)
                self.buttons[r][c] = btn

        main_layout.addWidget(board_widget, stretch=3)

        # Right: controls
        control_widget = QWidget()
        control_layout = QVBoxLayout()
        control_widget.setLayout(control_layout)
        control_widget.setStyleSheet("background-color: #1e1e1e; color: #f0f0f0;")
        main_layout.addWidget(control_widget, stretch=2)

        title_label = QLabel("Othello / Reversi")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 10px;")
        control_layout.addWidget(title_label)

        # Turn info
        self.turn_value_label = QLabel("Black (@)")
        self.turn_value_label.setAlignment(Qt.AlignCenter)
        self.turn_value_label.setStyleSheet("font-size: 16px; margin: 8px 0;")
        control_layout.addWidget(self.turn_value_label)

        # Player type selectors
        combo_container = QWidget()
        combo_layout = QVBoxLayout()
        combo_layout.setContentsMargins(0, 0, 0, 0)
        combo_container.setLayout(combo_layout)

        black_label = QLabel("Black (@) player type:")
        self.black_combo = QComboBox()
        self.black_combo.addItems(["Human", "AI"])
        self.black_combo.setCurrentText(self.black_type)

        white_label = QLabel("White (O) player type:")
        self.white_combo = QComboBox()
        self.white_combo.addItems(["Human", "AI"])
        self.white_combo.setCurrentText(self.white_type)

        for w in (black_label, white_label):
            w.setStyleSheet("font-size: 13px;")

        combo_layout.addWidget(black_label)
        combo_layout.addWidget(self.black_combo)
        combo_layout.addSpacing(8)
        combo_layout.addWidget(white_label)
        combo_layout.addWidget(self.white_combo)

        control_layout.addWidget(combo_container)

        # New game button
        new_game_btn = QPushButton("New Game")
        new_game_btn.clicked.connect(self.new_game)
        new_game_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #007acc;"
            "  color: white;"
            "  font-size: 14px;"
            "  padding: 6px 10px;"
            "  border-radius: 6px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #1493ff;"
            "}"
        )
        control_layout.addWidget(new_game_btn)

        # Info label
        self.info_label = QLabel("")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 12px; margin-top: 10px;")
        control_layout.addWidget(self.info_label)

        control_layout.addStretch()

        # Scores
        self.score_label = QLabel("")
        self.score_label.setAlignment(Qt.AlignCenter)
        self.score_label.setStyleSheet("font-size: 13px; margin-top: 8px;")
        control_layout.addWidget(self.score_label)

    # -------------- STYLES ---------------- #
    def _cell_base_style(self):
        return (
            "QPushButton {"
            "  background-color: #0b7a3b;"
            "  border: 1px solid #004d26;"
            "  border-radius: 6px;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #0f8f45;"
            "}"
        )

    def _cell_style_with_piece(self, piece_color: str):
        # piece_color: "black" or "white"
        text_color = "#000000" if piece_color == "black" else "#ffffff"
        return (
            "QPushButton {"
            "  background-color: #0b7a3b;"
            "  border: 1px solid #004d26;"
            "  border-radius: 6px;"
            "  font-size: 70px;"
            f"  color: {text_color};"
            "}"
            "QPushButton:pressed {"
            "  background-color: #0f8f45;"
            "}"
        )

    def _cell_style_hint(self):
        # legal move hint: highlight background slightly and show small dot
        return (
            "QPushButton {"
            "  background-color: #0f8f45;"
            "  border: 1px solid #004d26;"
            "  border-radius: 6px;"
            "  font-size: 20px;"
            "  color: #d9f7be;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #13a152;"
            "}"
        )

    # ---------------- GAME LOGIC BINDING ---------------- #
    def _make_cell_handler(self, row, col):
        def handler():
            self.handle_cell_clicked(row, col)
        return handler

    def is_human(self, color):
        if color == BLACK:
            return self.black_type == "Human"
        else:
            return self.white_type == "Human"

    def new_game(self):
        self.board = Board()
        self.current_player = BLACK
        self.black_type = self.black_combo.currentText()
        self.white_type = self.white_combo.currentText()
        self.info_label.setText("")
        self.update_board_view()
        if not self.is_human(self.current_player):
            QTimer.singleShot(300, self.maybe_ai_move)

    def update_board_view(self):
        if self.is_human(self.current_player) and self.board.has_any_move(self.current_player):
            legal_moves = set(self.board.get_available_moves(self.current_player))
        else:
            legal_moves = set()

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell = self.board.board[r][c]
                color = cell.get_color()
                btn = self.buttons[r][c]

                if color == BLACK:
                    btn.setText("●")
                    btn.setStyleSheet(self._cell_style_with_piece("black"))
                elif color == WHITE:
                    btn.setText("●")
                    btn.setStyleSheet(self._cell_style_with_piece("white"))
                elif (r, c) in legal_moves:
                    btn.setText("·")
                    btn.setStyleSheet(self._cell_style_hint())
                else:
                    btn.setText("")
                    btn.setStyleSheet(self._cell_base_style())

        # Update labels
        self.turn_value_label.setText("Black (@)" if self.current_player == BLACK else "White (O)")
        black_score = self.board.count_score(BLACK)
        white_score = self.board.count_score(WHITE)
        self.score_label.setText(f"Score  Black(@): {black_score}   |   White(O): {white_score}")

    def handle_cell_clicked(self, row, col):
        if not self.is_human(self.current_player):
            return

        moves = self.board.get_available_moves(self.current_player)
        if (row, col) not in moves:
            self.info_label.setText("Invalid move. Please click on a highlighted cell.")
            return

        self.board.make_move(row, col, self.current_player)
        self.info_label.setText("")
        self.after_move()

    def after_move(self):
        self.update_board_view()
        if self.board.is_game_over():
            self.show_game_over()
            return

        self.current_player = opponent(self.current_player)

        if not self.board.has_any_move(self.current_player):
            self.info_label.setText("No valid moves for this player. Turn skipped.")
            self.current_player = opponent(self.current_player)
            self.update_board_view()
            if self.board.is_game_over():
                self.show_game_over()
                return

        self.update_board_view()
        QTimer.singleShot(30, self.maybe_ai_move)
        # self.maybe_ai_move()


    def maybe_ai_move(self):
        if self.board.is_game_over():
            self.show_game_over()
            return

        if not self.is_human(self.current_player):
            if not self.board.has_any_move(self.current_player):
                self.info_label.setText("AI has no valid moves. Turn skipped.")
                self.current_player = opponent(self.current_player)
                self.update_board_view()
                return

            move = self.ai.best_move(self.board, self.current_player)
            if move is None:
                self.info_label.setText("AI has no valid moves. Turn skipped.")
                self.current_player = opponent(self.current_player)
                self.update_board_view()
                return

            r, c = move
            self.board.make_move(r, c, self.current_player)
            self.info_label.setText(f"AI played at ({r+1}, {c+1}).")
            self.after_move()

    def show_game_over(self):
        black_score = self.board.count_score(BLACK)
        white_score = self.board.count_score(WHITE)
        winner = self.board.get_winner()
        if winner == BLACK:
            msg = "Winner: Black (@)"
        elif winner == WHITE:
            msg = "Winner: White (O)"
        else:
            msg = "Result: Draw"

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Game Over")
        msg_box.setText(
            f"Game over!\n"
            f"Black (@): {black_score}\n"
            f"White (O): {white_score}\n\n"
            f"{msg}"
        )
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()


def run_gui():
    app = QApplication(sys.argv)
    window = OthelloWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    run_gui()

