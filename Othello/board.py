from constants import BOARD_SIZE, DIRECTIONS, SQUARE_WEIGHTS, BLACK, WHITE
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
        if not self.in_bounds(row, col):
            return False
        if not self.board[row][col].is_empty():
            return False
        opponent = self.opponent_player(player)
        for dr, dc in DIRECTIONS:
            r = row + dr
            c = col + dc
            opp_found = False
            while self.in_bounds(r, c) and self.board[r][c].get_color() == opponent:
                opp_found = True
                r += dr
                c += dc
            if opp_found and self.in_bounds(r, c) and self.board[r][c].get_color() == player:
                return True
        return False

    def get_available_moves(self, player):
        return [
            (r, c)
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if self.is_valid_move(r, c, player)
        ]

    def show_available_moves(self, player):
        moves = set(self.get_available_moves(player))
        print("Available moves marked with *:")
        print("   " + " ".join(str(c + 1) for c in range(BOARD_SIZE)))
        for r in range(BOARD_SIZE):
            print(str(r + 1) + "  ", end="")
            for c in range(BOARD_SIZE):
                if (r, c) in moves:
                    print('*', end=' ')
                else:
                    print(self.board[r][c].get_color(), end=' ')
            print()
        print()
        return moves

    def flip_direction(self, row, col, player, dr, dc):
        r = row + dr
        c = col + dc
        opponent = self.opponent_player(player)
        cells_to_flip = []
        while self.in_bounds(r, c) and self.board[r][c].get_color() == opponent:
            cells_to_flip.append((r, c))
            r += dr
            c += dc
        if self.in_bounds(r, c) and self.board[r][c].get_color() == player and cells_to_flip:
            for fr, fc in cells_to_flip:
                self.board[fr][fc].flip()

    def make_move(self, row, col, player):
        if not self.is_valid_move(row, col, player):
            return False
        self.board[row][col].set_color(player)
        for dr, dc in DIRECTIONS:
            self.flip_direction(row, col, player, dr, dc)
        return True

    def has_any_move(self, player):
        return any(
            self.is_valid_move(r, c, player)
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
        )

    def is_game_over(self):
        return not self.has_any_move(BLACK) and not self.has_any_move(WHITE)

    def get_winner(self):
        black_score = self.count_score(BLACK)
        white_score = self.count_score(WHITE)
        if black_score > white_score:
            return BLACK
        elif white_score > black_score:
            return WHITE
        return None

    def score(self, player):
        opp = self.opponent_player(player)
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = self.board[r][c].get_color()
                if color == player:
                    score += 1
                elif color == opp:
                    score -= 1
        return score

    def weighted_score(self, player):
        opp = self.opponent_player(player)
        score = 0
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                color = self.board[r][c].get_color()
                if color == player:
                    score += SQUARE_WEIGHTS[r][c][0]
                elif color == opp:
                    score -= SQUARE_WEIGHTS[r][c][0]
        return score
