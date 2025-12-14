from constants import MIN_VALUE, MAX_VALUE, opponent


class AI:
    def __init__(self, depth=4):
        self.depth = depth

    def evaluate(self, board, player):
        return board.weighted_score(player)

    def final_value(self, board, player):
        diff = board.score(player)
        if diff < 0:
            return MIN_VALUE
        elif diff > 0:
            return MAX_VALUE
        return diff

    def _alphabeta(self, board, current_player, depth, alpha, beta, maximizing, root_player):
        if depth == 0 or board.is_game_over():
            if board.is_game_over():
                return self.final_value(board, root_player)
            return self.evaluate(board, root_player)

        moves = board.get_available_moves(current_player)
        if not moves:
            other = opponent(current_player)
            if not board.has_any_move(other):
                return self.final_value(board, root_player)
            return self._alphabeta(board, other, depth, alpha, beta, not maximizing, root_player)

        other = opponent(current_player)

        if maximizing:
            value = MIN_VALUE
            for r, c in moves:
                nb = board.copy()
                nb.make_move(r, c, current_player)
                v = self._alphabeta(nb, other, depth - 1, alpha, beta, False, root_player)
                if v > value:
                    value = v
                if value > alpha:
                    alpha = value
                if alpha >= beta:
                    break
            return value
        else:
            value = MAX_VALUE
            for r, c in moves:
                nb = board.copy()
                nb.make_move(r, c, current_player)
                v = self._alphabeta(nb, other, depth - 1, alpha, beta, True, root_player)
                if v < value:
                    value = v
                if value < beta:
                    beta = value
                if alpha >= beta:
                    break
            return value

    def best_move(self, board, player):
        moves = board.get_available_moves(player)
        if not moves:
            return None

        best_val = MIN_VALUE
        best_moves = []

        for r, c in moves:
            nb = board.copy()
            nb.make_move(r, c, player)
            v = self._alphabeta(
                nb,
                opponent(player),
                self.depth - 1,
                MIN_VALUE,
                MAX_VALUE,
                False,
                player,
            )
            if v > best_val:
                best_val = v
                best_moves = [(r, c)]
            elif v == best_val:
                best_moves.append((r, c))

        return best_moves[0] if best_moves else None
