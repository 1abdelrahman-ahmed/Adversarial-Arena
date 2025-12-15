from constants import BOARD_SIZE, WHITE, BLACK, EMPTY, PROMOTION_CHOICES
from pieces import color_of, normalize_promo
from zobrist import compute_zobrist, init_zobrist

class Board:

    def __init__(self):
        self.board = [
            list('rnbqkbnr'),
            list('pppppppp'),
            list('........'),
            list('........'),
            list('........'),
            list('........'),
            list('PPPPPPPP'),
            list('RNBQKBNR'),
        ]
        self.side_to_move = 'w'
        self.castling_rights = {'K': True, 'Q': True, 'k': True, 'q': True}
        self.en_passant = None
        init_zobrist()
        self.halfmove_clock = 0
        self.position_history = []
        self.position_history.append(compute_zobrist(self))
        self.promotion_callback = None

    def inside(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def get_piece(self, r, c):
        return self.board[r][c]

    def set_piece(self, r, c, v):
        self.board[r][c] = v

    def opp(self, color):
        return 'b' if color == 'w' else 'w'

    def color_of(self, p):
        if p == '.':
            return None
        return 'w' if p.isupper() else 'b'

    def make_move(self, move, promotion_piece=None):
        if len(move) == 5:
            fr, fc, tr, tc, promo = move
            promotion_piece = promo
        else:
            fr, fc, tr, tc = move
        piece = self.get_piece(fr, fc)
        captured = self.get_piece(tr, tc)
        prev_ep = self.en_passant
        prev_side = self.side_to_move
        prev_castling = self.castling_rights.copy()
        prev_halfmove_clock = self.halfmove_clock
        rook_move = None
        promoted = False
        en_passant_capture = False
        ep_captured_square = None
        ep_captured_piece = None
        if piece in ('P', 'p'):
            if self.en_passant is not None and (tr, tc) == self.en_passant and (captured == '.'):
                en_passant_capture = True
                if piece == 'P':
                    ep_r = tr + 1
                else:
                    ep_r = tr - 1
                ep_c = tc
                ep_captured_square = (ep_r, ep_c)
                ep_captured_piece = self.get_piece(ep_r, ep_c)
                captured = ep_captured_piece
        if piece in ('K', 'k') and abs(tc - fc) == 2:
            if tc > fc:
                rook_fr, rook_fc = (fr, 7)
                rook_tr, rook_tc = (fr, 5)
            else:
                rook_fr, rook_fc = (fr, 0)
                rook_tr, rook_tc = (fr, 3)
            rook_piece = self.get_piece(rook_fr, rook_fc)
            self.set_piece(fr, fc, '.')
            self.set_piece(tr, tc, piece)
            self.set_piece(rook_fr, rook_fc, '.')
            self.set_piece(rook_tr, rook_tc, rook_piece)
            rook_move = (rook_fr, rook_fc, rook_tr, rook_tc)
        else:
            self.set_piece(fr, fc, '.')
            self.set_piece(tr, tc, piece)
            if en_passant_capture:
                er, ec = ep_captured_square
                self.set_piece(er, ec, '.')
            if piece == 'P' and tr == 0:
                if promotion_piece is None:
                    if self.promotion_callback:
                        promotion_piece = self.promotion_callback('w')
                    else:
                        promotion_piece = 'Q'
                if promotion_piece.upper() not in ['Q', 'R', 'B', 'N']:
                    promotion_piece = 'Q'
                self.set_piece(tr, tc, promotion_piece.upper())
                promoted = True
            elif piece == 'p' and tr == 7:
                if promotion_piece is None:
                    if self.promotion_callback:
                        promotion_piece = self.promotion_callback('b')
                    else:
                        promotion_piece = 'q'
                if promotion_piece.upper() not in ['Q', 'R', 'B', 'N']:
                    promotion_piece = 'q'
                self.set_piece(tr, tc, promotion_piece.lower())
                promoted = True
        self.en_passant = None
        if piece in ('P', 'p') and abs(tr - fr) == 2:
            self.en_passant = ((fr + tr) // 2, fc)
        if piece == 'K':
            self.castling_rights['K'] = False
            self.castling_rights['Q'] = False
        elif piece == 'k':
            self.castling_rights['k'] = False
            self.castling_rights['q'] = False
        if piece == 'R':
            if (fr, fc) == (7, 0):
                self.castling_rights['Q'] = False
            if (fr, fc) == (7, 7):
                self.castling_rights['K'] = False
        elif piece == 'r':
            if (fr, fc) == (0, 0):
                self.castling_rights['q'] = False
            if (fr, fc) == (0, 7):
                self.castling_rights['k'] = False
        if captured == 'R':
            if (tr, tc) == (7, 0):
                self.castling_rights['Q'] = False
            if (tr, tc) == (7, 7):
                self.castling_rights['K'] = False
        elif captured == 'r':
            if (tr, tc) == (0, 0):
                self.castling_rights['q'] = False
            if (tr, tc) == (0, 7):
                self.castling_rights['k'] = False
        self.side_to_move = self.opp(self.side_to_move)
        if captured != '.' or piece.upper() == 'P':
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        key = compute_zobrist(self)
        self.position_history.append(key)
        return {
            'captured': captured,
            'piece': piece,
            'promoted': promoted,
            'prev_en_passant': prev_ep,
            'prev_side': prev_side,
            'prev_castling': prev_castling,
            'prev_halfmove_clock': prev_halfmove_clock,
            'rook_move': rook_move,
            'ep_capture': en_passant_capture,
            'ep_captured_square': ep_captured_square,
        }

    def undo_move(self, move, st):
        if len(move) == 5:
            fr, fc, tr, tc, _ = move
        else:
            fr, fc, tr, tc = move
        captured = st['captured']
        piece = st['piece']
        promoted = st['promoted']
        prev_ep = st['prev_en_passant']
        prev_side = st['prev_side']
        prev_castling = st['prev_castling']
        prev_halfmove_clock = st['prev_halfmove_clock']
        rook_move = st['rook_move']
        ep_capture = st['ep_capture']
        ep_captured_square = st['ep_captured_square']
        self.position_history.pop()
        if rook_move is not None:
            rfr, rfc, rtr, rtc = rook_move
            rook_piece = self.get_piece(rtr, rtc)
            self.set_piece(fr, fc, piece)
            self.set_piece(rfr, rfc, rook_piece)
            self.set_piece(rtr, rtc, '.')
            self.set_piece(tr, tc, '.')
        elif promoted:
            self.set_piece(fr, fc, piece)
            self.set_piece(tr, tc, captured)
        else:
            self.set_piece(fr, fc, piece)
            self.set_piece(tr, tc, captured)
        if ep_capture and ep_captured_square is not None:
            er, ec = ep_captured_square
            self.set_piece(er, ec, captured)
            self.set_piece(tr, tc, '.')
        self.en_passant = prev_ep
        self.castling_rights = prev_castling.copy()
        self.side_to_move = prev_side
        self.halfmove_clock = prev_halfmove_clock

    def is_promotion_move(self, move):
        fr, fc, tr, tc = move[:4]
        piece = self.get_piece(fr, fc)
        if piece == 'P' and tr == 0:
            return True
        if piece == 'p' and tr == 7:
            return True
        return False

    def find_king(self, color):
        king = 'K' if color == 'w' else 'k'
        for r in range(8):
            for c in range(8):
                if self.get_piece(r, c) == king:
                    return (r, c)
        return None

    def attacks(self, fr, fc, tr, tc, color):
        p = self.get_piece(fr, fc)
        if p == '.':
            return False
        P = p.upper()
        dr = tr - fr
        dc = tc - fc
        if P == 'P':
            step = -1 if color == 'w' else 1
            return dr == step and abs(dc) == 1
        if P == 'N':
            return (abs(dr), abs(dc)) in [(1, 2), (2, 1)]
        if P == 'K':
            return max(abs(dr), abs(dc)) == 1
        if P in 'BQ':
            if abs(dr) == abs(dc) and dr != 0:
                sr = 1 if dr > 0 else -1
                sc = 1 if dc > 0 else -1
                rr, cc = (fr + sr, fc + sc)
                while (rr, cc) != (tr, tc):
                    if self.get_piece(rr, cc) != '.':
                        return False
                    rr += sr
                    cc += sc
                return True
        if P in 'RQ':
            if dr == 0 and dc != 0:
                sc = 1 if dc > 0 else -1
                cc = fc + sc
                while cc != tc:
                    if self.get_piece(fr, cc) != '.':
                        return False
                    cc += sc
                return True
            if dc == 0 and dr != 0:
                sr = 1 if dr > 0 else -1
                rr = fr + sr
                while rr != tr:
                    if self.get_piece(rr, fc) != '.':
                        return False
                    rr += sr
                return True
        return False

    def square_attacked(self, tr, tc, by_color):
        for r in range(8):
            for c in range(8):
                p = self.get_piece(r, c)
                if p != '.' and self.color_of(p) == by_color:
                    if self.attacks(r, c, tr, tc, by_color):
                        return True
        return False

    def in_check(self, color):
        pos = self.find_king(color)
        if pos is None:
            return True
        return self.square_attacked(pos[0], pos[1], self.opp(color))

    def generate_pseudo_moves(self, color, captures_only=False):
        moves = []
        for r in range(8):
            for c in range(8):
                p = self.get_piece(r, c)
                if p != '.' and self.color_of(p) == color:
                    self._piece_moves_from(r, c, color, moves, captures_only)
        if not captures_only:
            self._add_castling_moves(color, moves)
        return moves

    def _piece_moves_from(self, r, c, color, moves, captures_only):
        p = self.get_piece(r, c).upper()
        if p == 'P':
            step = -1 if color == 'w' else 1
            start = 6 if color == 'w' else 1
            nr = r + step
            if not captures_only:
                if self.inside(nr, c) and self.get_piece(nr, c) == '.':
                    moves.append((r, c, nr, c))
                    nr2 = r + 2 * step
                    if r == start and self.get_piece(nr2, c) == '.':
                        moves.append((r, c, nr2, c))
            for dc in (-1, 1):
                nr, nc = (r + step, c + dc)
                if self.inside(nr, nc):
                    t = self.get_piece(nr, nc)
                    if t != '.' and self.color_of(t) != color:
                        moves.append((r, c, nr, nc))
            if self.en_passant is not None:
                ep_r, ep_c = self.en_passant
                if ep_r == r + step and abs(ep_c - c) == 1:
                    moves.append((r, c, ep_r, ep_c))
        elif p == 'N':
            for dr, dc in ((1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)):
                nr, nc = (r + dr, c + dc)
                if self.inside(nr, nc):
                    t = self.get_piece(nr, nc)
                    if t == '.' and (not captures_only):
                        moves.append((r, c, nr, nc))
                    elif t != '.' and self.color_of(t) != color:
                        moves.append((r, c, nr, nc))
        elif p in 'BRQ':
            dirs = []
            if p in 'BQ':
                dirs += [(1, 1), (1, -1), (-1, 1), (-1, -1)]
            if p in 'RQ':
                dirs += [(1, 0), (-1, 0), (0, 1), (0, -1)]
            for dr, dc in dirs:
                nr, nc = (r + dr, c + dc)
                while self.inside(nr, nc):
                    t = self.get_piece(nr, nc)
                    if t == '.':
                        if not captures_only:
                            moves.append((r, c, nr, nc))
                    else:
                        if self.color_of(t) != color:
                            moves.append((r, c, nr, nc))
                        break
                    nr += dr
                    nc += dc
        elif p == 'K':
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = (r + dr, c + dc)
                    if self.inside(nr, nc):
                        t = self.get_piece(nr, nc)
                        if t == '.' and (not captures_only):
                            moves.append((r, c, nr, nc))
                        elif t != '.' and self.color_of(t) != color:
                            moves.append((r, c, nr, nc))

    def _add_castling_moves(self, color, moves):
        """Add castling moves if legal (empty squares + no check through/into check)."""
        enemy = self.opp(color)
        if color == 'w':
            king_r, king_c = 7, 4
            # King must not be in check, and cannot pass through or land on attacked squares.
            if not self.in_check('w'):
                if self.castling_rights.get('K', False):
                    if self.get_piece(7, 5) == '.' and self.get_piece(7, 6) == '.':
                        if (not self.square_attacked(7, 5, enemy)) and (not self.square_attacked(7, 6, enemy)):
                            moves.append((7, 4, 7, 6))
                if self.castling_rights.get('Q', False):
                    if self.get_piece(7, 3) == '.' and self.get_piece(7, 2) == '.' and self.get_piece(7, 1) == '.':
                        if (not self.square_attacked(7, 3, enemy)) and (not self.square_attacked(7, 2, enemy)):
                            moves.append((7, 4, 7, 2))
        else:
            if not self.in_check('b'):
                if self.castling_rights.get('k', False):
                    if self.get_piece(0, 5) == '.' and self.get_piece(0, 6) == '.':
                        if (not self.square_attacked(0, 5, enemy)) and (not self.square_attacked(0, 6, enemy)):
                            moves.append((0, 4, 0, 6))
                if self.castling_rights.get('q', False):
                    if self.get_piece(0, 3) == '.' and self.get_piece(0, 2) == '.' and self.get_piece(0, 1) == '.':
                        if (not self.square_attacked(0, 3, enemy)) and (not self.square_attacked(0, 2, enemy)):
                            moves.append((0, 4, 0, 2))

    def generate_legal_moves(self, color, captures_only=False):
        legal = []
        pseudo = self.generate_pseudo_moves(color, captures_only)
        for mv in pseudo:
            st = self.make_move(mv)
            if not self.in_check(color):
                legal.append(mv)
            self.undo_move(mv, st)
        return legal

    def is_threefold(self):
        if not self.position_history:
            return False
        last = self.position_history[-1]
        return self.position_history.count(last) >= 3

    def is_fifty_move_rule(self):
        return self.halfmove_clock >= 100

    def is_insufficient_material(self):
        pieces = []
        for r in range(8):
            for c in range(8):
                p = self.get_piece(r, c)
                if p != '.':
                    pieces.append((p, r, c))
        if len(pieces) == 2:
            return True
        if len(pieces) == 3:
            if any((p[0].upper() in ('N', 'B') for p in pieces)):
                return True
        if len(pieces) == 4:
            bishops = [(p, r, c) for p, r, c in pieces if p.upper() == 'B']
            if len(bishops) == 2:
                colors = [(r + c) % 2 for _, r, c in bishops]
                if colors[0] == colors[1]:
                    return True
        return False

    def is_dead_position(self):
        return self.is_insufficient_material()

    def print_board(self):
        for r in range(8):
            print(' '.join(self.board[r]))
        print()
