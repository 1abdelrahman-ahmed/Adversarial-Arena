from constants import BLACK, WHITE
from ai import AI


class Player:
    def __init__(self, color, kind="human", ai: AI | None = None, name: str | None = None):
        self.color = color
        self.kind = kind
        self.ai = ai
        if name is not None:
            self.name = name
        else:
            self.name = "Black (@)" if color == BLACK else "White (O)"

    def has_move(self, board):
        return board.has_any_move(self.color)

    def play_turn(self, board):
        if not self.has_move(board):
            print(f"{self.name} has no valid moves. Turn skipped.\n")
            return False

        if self.kind == "human":
            board.show_available_moves(self.color)
            return self._human_move(board)
        else:
            return self._ai_move(board)

    def _human_move(self, board):
        moves = board.get_available_moves(self.color)
        while True:
            raw = input("Enter move (row col) or 'q' to quit: ").strip()
            if raw.lower() == 'q':
                print("Game aborted by player.")
                raise SystemExit
            try:
                r_str, c_str = raw.split()
                r = int(r_str) - 1
                c = int(c_str) - 1
                if (r, c) in moves:
                    board.make_move(r, c, self.color)
                    return True
                print("Invalid move. Try one of the '*' squares.")
            except Exception:
                print("Invalid input format. Example: 3 4")

    def _ai_move(self, board):
        if self.ai is None:
            raise ValueError("AI instance is not set for this player.")
        move = self.ai.best_move(board, self.color)
        if move is None:
            print(f"{self.name} (AI) has no valid moves. Turn skipped.\n")
            return False
        r, c = move
        board.make_move(r, c, self.color)
        print(f"{self.name} (AI) plays: ({r + 1}, {c + 1})\n")
        return True
