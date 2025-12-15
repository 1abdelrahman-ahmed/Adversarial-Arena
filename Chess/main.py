import sys

from .board import Board
from .player import Player
from .ai import AIEngine
from .moves import MoveCodec
from .constants import WHITE, BLACK


class CliGame:
    def __init__(self, white_player, black_player):
        self.board = Board()
        self.white = white_player
        self.black = black_player

    def _player_for_side(self, side):
        return self.white if side == WHITE else self.black

    def _print_board(self):
        b = self.board
        print()
        print("  a b c d e f g h")
        for r in range(8):
            print(8 - r, end=" ")
            row = []
            for c in range(8):
                row.append(b.get_piece(r, c))
            print(" ".join(row), end=" ")
            print(8 - r)
        print("  a b c d e f g h")
        print()

    def _read_move(self):
        while True:
            txt = input("Move (e2e4, e7e8q) or 'q': ").strip()
            if txt.lower() in ('q', 'quit', 'exit'):
                return None
            mv = MoveCodec.parse_uci(txt)
            if mv is None:
                print("Invalid format.")
                continue
            return mv

    def run(self):
        engines = {
            WHITE: AIEngine(self.white.depth) if self.white.is_ai else None,
            BLACK: AIEngine(self.black.depth) if self.black.is_ai else None,
        }

        while True:
            self._print_board()
            side = self.board.side_to_move

            if self.board.is_threefold():
                print("Draw by threefold repetition.")
                return
            if self.board.is_fifty_move_rule():
                print("Draw by 50-move rule.")
                return
            if self.board.is_insufficient_material():
                print("Draw by insufficient material.")
                return

            legal = self.board.generate_legal_moves(side)
            if not legal:
                if self.board.in_check(side):
                    winner = 'WHITE' if side == BLACK else 'BLACK'
                    print("Checkmate.", winner, "wins.")
                else:
                    print("Stalemate.")
                return

            player = self._player_for_side(side)
            if player.is_ai:
                engine = engines[side]
                mv = engine.select_move(self.board)
                if mv is None:
                    print("AI claims draw or has no move.")
                    return
                print(("WHITE" if side == WHITE else "BLACK") + " plays:", MoveCodec.to_uci(mv))
                self.board.make_move(mv)
            else:
                mv = self._read_move()
                if mv is None:
                    return
                if mv not in legal:
                    print("Illegal move.")
                    continue
                self.board.make_move(mv)


def _pick_mode():
    while True:
        print("1) Human vs AI")
        print("2) Human vs Human")
        print("3) AI vs AI")
        choice = input("Choose: ").strip()
        if choice in ('1', '2', '3'):
            return choice


def main():
    choice = _pick_mode()

    if choice == '1':
        side = ''
        while side not in ('w', 'b'):
            side = input("Play as (w/b): ").strip().lower()
        depth_txt = input("AI depth (default 3): ").strip()
        depth = 3
        if depth_txt:
            try:
                depth = int(depth_txt)
            except Exception:
                depth = 3

        if side == 'w':
            white = Player(WHITE, 'human')
            black = Player(BLACK, 'ai', depth)
        else:
            white = Player(WHITE, 'ai', depth)
            black = Player(BLACK, 'human')

        CliGame(white, black).run()
        return

    if choice == '2':
        white = Player(WHITE, 'human')
        black = Player(BLACK, 'human')
        CliGame(white, black).run()
        return

    depth_w_txt = input("White AI depth (default 3): ").strip()
    depth_b_txt = input("Black AI depth (default 3): ").strip()
    dw = 3
    db = 3
    if depth_w_txt:
        try:
            dw = int(depth_w_txt)
        except Exception:
            dw = 3
    if depth_b_txt:
        try:
            db = int(depth_b_txt)
        except Exception:
            db = 3

    white = Player(WHITE, 'ai', dw)
    black = Player(BLACK, 'ai', db)
    CliGame(white, black).run()


if __name__ == '__main__':
    main()
