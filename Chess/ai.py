import math
import random

from board import Board
from constants import PIECE_VALUES, PAWN_TABLE, KNIGHT_TABLE, BISHOP_TABLE, ROOK_TABLE, QUEEN_TABLE, KING_TABLE
from zobrist import compute_zobrist


def psq_value(p, r, c):
    idx = r*8 + c
    if p.upper() == 'P':
        tbl = PAWN_TABLE
    elif p.upper() == 'N':
        tbl = KNIGHT_TABLE
    elif p.upper() == 'B':
        tbl = BISHOP_TABLE
    elif p.upper() == 'R':
        tbl = ROOK_TABLE
    elif p.upper() == 'Q':
        tbl = QUEEN_TABLE
    elif p.upper() == 'K':
        tbl = KING_TABLE
    else:
        return 0

    if p.isupper():  
        return tbl[idx]
    else:  
        mirror_idx = (7-r)*8 + c
        return -tbl[mirror_idx]


def evaluate(board: Board):
    score = 0
    white_bishops = 0
    black_bishops = 0
    white_knights = 0
    black_knights = 0
    white_rooks = 0
    black_rooks = 0
    
    white_king_pos = None
    black_king_pos = None
    
    for r in range(8):
        for c in range(8):
            p = board.get_piece(r, c)
            if p == '.':
                continue
            
            base = PIECE_VALUES[p.upper()]
            if p.isupper():
                score += base
            else:
                score -= base
            
            psq = psq_value(p, r, c)
            score += psq
            
            if p == 'B': 
                white_bishops += 1
            elif p == 'b': 
                black_bishops += 1
            elif p == 'N':
                white_knights += 1
            elif p == 'n':
                black_knights += 1
            elif p == 'R':
                white_rooks += 1
            elif p == 'r':
                black_rooks += 1
            elif p == 'K':
                white_king_pos = (r, c)
            elif p == 'k':
                black_king_pos = (r, c)

    if white_bishops >= 2: 
        score += 50
    if black_bishops >= 2: 
        score -= 50
    
    for c in range(8):
        white_pawns = sum(1 for r in range(8) if board.get_piece(r, c) == 'P')
        black_pawns = sum(1 for r in range(8) if board.get_piece(r, c) == 'p')
        
        if white_pawns == 0:
            for r in range(8):
                if board.get_piece(r, c) == 'R':
                    score += 20 if black_pawns == 0 else 10
        
        if black_pawns == 0:
            for r in range(8):
                if board.get_piece(r, c) == 'r':
                    score -= 20 if white_pawns == 0 else 10
    
    total_material = (white_knights + black_knights) * 320 + (white_bishops + black_bishops) * 330 + (white_rooks + black_rooks) * 500
    is_endgame = total_material < 2500
    
    if not is_endgame:
        if white_king_pos:
            kr, kc = white_king_pos
            if kr >= 2 and kr <= 5 and kc >= 2 and kc <= 5:
                score -= 30
            if kr == 7 and (kc <= 2 or kc >= 5):
                score += 20
        
        if black_king_pos:
            kr, kc = black_king_pos
            if kr >= 2 and kr <= 5 and kc >= 2 and kc <= 5:
                score += 30
            if kr == 0 and (kc <= 2 or kc >= 5):
                score -= 20
    
    for c in range(8):
        white_pawns_col = [(r, c) for r in range(8) if board.get_piece(r, c) == 'P']
        black_pawns_col = [(r, c) for r in range(8) if board.get_piece(r, c) == 'p']
        
        if len(white_pawns_col) > 1:
            score -= 10 * (len(white_pawns_col) - 1)
        if len(black_pawns_col) > 1:
            score += 10 * (len(black_pawns_col) - 1)
        
        for r, _ in white_pawns_col:
            is_passed = True
            for check_c in [c-1, c, c+1]:
                if 0 <= check_c < 8:
                    if any(board.get_piece(check_r, check_c) == 'p' for check_r in range(r)):
                        is_passed = False
                        break
            if is_passed:
                score += 20 + (7 - r) * 5
        
        for r, _ in black_pawns_col:
            is_passed = True
            for check_c in [c-1, c, c+1]:
                if 0 <= check_c < 8:
                    if any(board.get_piece(check_r, check_c) == 'P' for check_r in range(r+1, 8)):
                        is_passed = False
                        break
            if is_passed:
                score -= 20 + r * 5

    white_moves = len(board.generate_pseudo_moves('w'))
    black_moves = len(board.generate_pseudo_moves('b'))
    score += (white_moves - black_moves) * 2

    current_hash = compute_zobrist(board)
    repetition_count = board.position_history.count(current_hash)
    if repetition_count >= 1:
        score -= 50 * repetition_count

    return score


TTABLE = {}
TT_EXACT, TT_ALPHA, TT_BETA = 0,1,2
MATE_VALUE = 100000

killer_moves = [[None, None] for _ in range(20)]
history_scores = {}


def order_moves(board, moves, depth=0, tt_move=None):
    ordered = []
    
    for mv in moves:
        score = 0
        fr, fc, tr, tc = mv[:4]
        target = board.get_piece(tr, tc)
        attacker = board.get_piece(fr, fc)
        
        if tt_move and mv[:4] == tt_move[:4]:
            score = 1000000
        
        elif target != '.':
            victim_value = PIECE_VALUES[target.upper()]
            attacker_value = PIECE_VALUES[attacker.upper()]
            score = 10000 + victim_value - attacker_value // 100
        
        elif depth < 20:
            if killer_moves[depth][0] and mv[:4] == killer_moves[depth][0][:4]:
                score = 9000
            elif killer_moves[depth][1] and mv[:4] == killer_moves[depth][1][:4]:
                score = 8000
        
        if score < 9000:
            move_key = (mv[:4], board.side_to_move)
            score += history_scores.get(move_key, 0)
        
        if score < 100:
            st = board.make_move(mv)
            new_hash = compute_zobrist(board)
            rep_count = board.position_history.count(new_hash)
            if rep_count >= 2:
                score -= 500
            elif rep_count == 1:
                score -= 100
            board.undo_move(mv, st)
        
        ordered.append((score, mv))
    
    ordered.sort(reverse=True, key=lambda x: x[0])
    return [m for _, m in ordered]


def qsearch(board, alpha, beta, color_sign):
    stand_pat = color_sign * evaluate(board)

    if stand_pat >= beta:
        return beta
    
    BIG_DELTA = 975
    if stand_pat < alpha - BIG_DELTA:
        return alpha
    
    if alpha < stand_pat:
        alpha = stand_pat

    moves = board.generate_legal_moves(board.side_to_move, captures_only=True)
    if not moves:
        return stand_pat

    cap_scores = []
    for mv in moves:
        fr, fc, tr, tc = mv[:4]
        victim = board.get_piece(tr, tc)
        attacker = board.get_piece(fr, fc)
        if victim != '.':
            score = PIECE_VALUES[victim.upper()] * 10 - PIECE_VALUES[attacker.upper()]
            cap_scores.append((score, mv))
    
    cap_scores.sort(reverse=True, key=lambda x: x[0])
    moves = [m for _, m in cap_scores]

    for mv in moves:
        fr, fc, tr, tc = mv[:4]
        victim = board.get_piece(tr, tc)
        attacker = board.get_piece(fr, fc)
        if victim != '.' and PIECE_VALUES[victim.upper()] + 200 < PIECE_VALUES[attacker.upper()]:
            continue
        
        st = board.make_move(mv)
        score = -qsearch(board, -beta, -alpha, -color_sign)
        board.undo_move(mv, st)

        if score >= beta:
            return beta
        if score > alpha:
            alpha = score
    
    return alpha


def negamax(board, depth, alpha, beta, color_sign, ply=0, do_null=True):
    global TTABLE
    
    alpha_orig = alpha
    key = compute_zobrist(board)

    rep_count = board.position_history.count(key)
    if rep_count >= 2 and ply > 0:
        return 0

    tt_entry = TTABLE.get(key)
    tt_move = None
    if tt_entry is not None:
        tt_depth, tt_value, tt_flag, tt_move = tt_entry
        if tt_depth >= depth:
            if tt_flag == TT_EXACT:
                return tt_value
            elif tt_flag == TT_ALPHA and tt_value <= alpha:
                return tt_value
            elif tt_flag == TT_BETA and tt_value >= beta:
                return tt_value

    if depth <= 0:
        return qsearch(board, alpha, beta, color_sign)

    in_check = board.in_check(board.side_to_move)
    if in_check:
        depth += 1

    legal_moves = board.generate_legal_moves(board.side_to_move)
    if not legal_moves:
        if in_check:
            return -MATE_VALUE + ply
        else:
            return 0

    if (do_null and not in_check and depth >= 4 and ply > 0 and beta - alpha == 1):
        has_material = False
        for r in range(8):
            for c in range(8):
                p = board.get_piece(r, c)
                if p != '.' and board.color_of(p) == board.side_to_move:
                    if p.upper() not in 'PK':
                        has_material = True
                        break
            if has_material:
                break
        
        if has_material:
            R = 3 if depth >= 6 else 2
            board.side_to_move = board.opp(board.side_to_move)
            null_score = -negamax(board, depth - 1 - R, -beta, -beta + 1, -color_sign, ply + 1, False)
            board.side_to_move = board.opp(board.side_to_move)
            if null_score >= beta:
                if depth < 8:
                    return beta
                verify = negamax(board, depth - 4, beta - 1, beta, color_sign, ply, False)
                if verify >= beta:
                    return beta

    legal_moves = order_moves(board, legal_moves, ply, tt_move)

    best_value = -math.inf
    best_move = None
    moves_searched = 0
    
    capture_count = sum(1 for mv in legal_moves if board.get_piece(mv[2], mv[3]) != '.')

    for i, mv in enumerate(legal_moves):
        fr, fc, tr, tc = mv[:4]
        is_capture = board.get_piece(tr, tc) != '.'
        is_killer = (ply < 20 and (mv == killer_moves[ply][0] or mv == killer_moves[ply][1]))
        
        st = board.make_move(mv)
        
        reduction = 0
        if (moves_searched >= 6 and depth >= 3 and not in_check and 
            not is_capture and not is_killer and i >= capture_count):
            
            move_key = (mv[:4], board.side_to_move)
            hist = history_scores.get(move_key, 0)
            
            if moves_searched >= 12 and hist < 100:
                reduction = 2
            elif moves_searched >= 8 and hist < 50:
                reduction = 1
        
        if reduction > 0:
            score = -negamax(board, depth - 1 - reduction, -alpha - 1, -alpha, -color_sign, ply + 1, True)
            if score > alpha:
                score = -negamax(board, depth - 1, -beta, -alpha, -color_sign, ply + 1, True)
        else:
            if moves_searched == 0:
                score = -negamax(board, depth - 1, -beta, -alpha, -color_sign, ply + 1, True)
            else:
                score = -negamax(board, depth - 1, -alpha - 1, -alpha, -color_sign, ply + 1, True)
                if alpha < score < beta:
                    score = -negamax(board, depth - 1, -beta, -alpha, -color_sign, ply + 1, True)
        
        board.undo_move(mv, st)
        moves_searched += 1

        if score > best_value:
            best_value = score
            best_move = mv
        
        if score > alpha:
            alpha = score
        
        if alpha >= beta:
            if ply < 20 and not is_capture:
                if killer_moves[ply][0] != mv:
                    killer_moves[ply][1] = killer_moves[ply][0]
                    killer_moves[ply][0] = mv
            
            if not is_capture:
                move_key = (mv[:4], board.side_to_move)
                history_scores[move_key] = history_scores.get(move_key, 0) + depth * depth
            break

    flag = TT_EXACT
    if best_value <= alpha_orig:
        flag = TT_ALPHA
    elif best_value >= beta:
        flag = TT_BETA

    TTABLE[key] = (depth, best_value, flag, best_move)

    return best_value


def static_eval_for_color(board, maximizing_color):
    base = evaluate(board)
    return base if maximizing_color == 'w' else -base


def find_best_move_hybrid(board, max_depth):
    global killer_moves, history_scores, TTABLE
    
    best_move = None
    
    current_hash = compute_zobrist(board)
    if board.position_history.count(current_hash) >= 2:
        print("[INFO] Position already repeated twice - claiming draw")
        return None

    killer_moves = [[None, None] for _ in range(20)]
    
    legal = board.generate_legal_moves(board.side_to_move)
    if not legal:
        return None
    
    if len(legal) == 1:
        print(f"[INFO] Only one legal move: {move_to_str(legal[0])}")
        return legal[0]
    
    color_sign = 1 if board.side_to_move == 'w' else -1
    prev_score = 0
    
    for depth in range(1, max_depth + 1):
        alpha = -math.inf
        beta = math.inf
        
        if depth >= 5:
            window = 75
            alpha = prev_score - window
            beta = prev_score + window
        
        key = compute_zobrist(board)
        tt_entry = TTABLE.get(key)
        tt_move = tt_entry[3] if tt_entry else None
        
        legal_ordered = order_moves(board, legal, 0, tt_move)
        
        local_best = None
        local_best_val = -math.inf
        search_failed = False
        
        for mv in legal_ordered:
            st = board.make_move(mv)
            score = -negamax(board, depth - 1, -beta, -alpha, -color_sign, 1, True)
            board.undo_move(mv, st)
            
            if score <= alpha or score >= beta:
                if depth >= 5:
                    search_failed = True
                    break
            
            if score > local_best_val:
                local_best_val = score
                local_best = mv
                
            if score > alpha:
                alpha = score

        if search_failed:
            print(f"[INFO] Re-searching depth {depth} with full window")
            alpha = -math.inf
            beta = math.inf
            local_best = None
            local_best_val = -math.inf
            
            for mv in legal_ordered:
                st = board.make_move(mv)
                score = -negamax(board, depth - 1, -beta, -alpha, -color_sign, 1, True)
                board.undo_move(mv, st)
                
                if score > local_best_val:
                    local_best_val = score
                    local_best = mv
                    
                if score > alpha:
                    alpha = score
        
        if local_best is not None:
            best_move = local_best
            prev_score = local_best_val
            
            side = "White" if board.side_to_move == 'w' else "Black"
            print(f"[Depth {depth}/{max_depth}] {side} best: {move_to_str(best_move)} (eval: {local_best_val/100:.2f})")
        
        if abs(local_best_val) > MATE_VALUE - 100:
            mate_in = (MATE_VALUE - abs(local_best_val)) // 2
            print(f"[INFO] Found mate in {mate_in}")
            break

    if best_move:
        st = board.make_move(best_move)
        new_hash = compute_zobrist(board)
        rep_count = board.position_history.count(new_hash)
        board.undo_move(best_move, st)
        
        if rep_count >= 2:
            non_rep = []
            for mv in legal:
                st = board.make_move(mv)
                h = compute_zobrist(board)
                if board.position_history.count(h) < 2:
                    non_rep.append(mv)
                board.undo_move(mv, st)
            
            if non_rep:
                best_non_rep = None
                best_non_rep_score = -math.inf
                
                for mv in non_rep:
                    st = board.make_move(mv)
                    score = -negamax(board, max(2, max_depth - 2), -math.inf, math.inf, -color_sign, 1, True)
                    board.undo_move(mv, st)
                    
                    if score > best_non_rep_score:
                        best_non_rep_score = score
                        best_non_rep = mv
                
                if best_non_rep:
                    best_move = best_non_rep
                    print(f"[INFO] Avoiding repetition - chose {move_to_str(best_move)}")
            else:
                print("[INFO] All moves lead to repetition")

    return best_move


class AIEngine:
    def __init__(self, depth=3):
        self.depth = depth
    
    def select_move(self, board):
        global TTABLE
        if len(TTABLE) > 500000:
            TTABLE.clear()
            print("[INFO] Cleared transposition table")
        
        return find_best_move_hybrid(board, self.depth)


def square_to_idx(s):
    if len(s)!=2:
        return None
    file, rank = s[0], s[1]
    if file < 'a' or file > 'h': return None
    if rank < '1' or rank > '8': return None
    c = ord(file) - ord('a')
    r = 8 - int(rank)
    return (r,c)


def parse_move(txt):
    txt = txt.strip().lower()
    if len(txt) != 4:
        return None
    f = square_to_idx(txt[:2])
    t = square_to_idx(txt[2:])
    if not f or not t:
        return None
    return (f[0], f[1], t[0], t[1])


def idx_to_square(r,c):
    return chr(ord('a')+c) + str(8-r)


def move_to_str(mv):
    if mv is None:
        return "None"
    fr,fc,tr,tc = mv[:4]
    return idx_to_square(fr,fc) + idx_to_square(tr,tc)
