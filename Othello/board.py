from constants import BOARD_SIZE, BLACK, WHITE
from cell import Cell


class Board:
    def __init__(self):
        self.board = [[Cell() for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.board[3][3].set_color(WHITE)
        self.board[3][4].set_color(BLACK)
        self.board[4][3].set_color(BLACK)
        self.board[4][4].set_color(WHITE)

    def display(self):
        print("   " + " ".join(str(c + 1) for c in range(BOARD_SIZE)))
        for i in range(BOARD_SIZE):
            print(str(i + 1) + "  ", end="")
            for j in range(BOARD_SIZE):
                print(self.board[i][j].get_color(), end=' ')
            print()
        print()

    def copy(self):
        new_board = Board()
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                new_board.board[i][j].set_color(self.board[i][j].get_color())
        return new_board

    def count_score(self, player):
        return sum(
            1
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if self.board[r][c].get_color() == player
        )

    def opponent_player(self, player):
        return BLACK if player == WHITE else WHITE

    def in_bounds(self, row, col):
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def is_valid_move(self, row, col, player):
        pass

    def get_available_moves(self, player):
        pass

    def show_available_moves(self, player):
        pass

    def flip_direction(self, row, col, player, dr, dc):
        pass

    def make_move(self, row, col, player):
        pass

    def has_any_move(self, player):
        pass

    def is_game_over(self):
        pass

    def get_winner(self):
        pass

    def score(self, player):
        pass

    def weighted_score(self, player):
        pass
