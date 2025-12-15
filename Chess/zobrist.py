import random
from pieces import PIECES

ZOBRIST_PIECES = [[0]*64 for _ in range(len(PIECES))]
ZOBRIST_SIDE = 0

def init_zobrist():
    global ZOBRIST_PIECES, ZOBRIST_SIDE
    random.seed(123456)
    for i in range(len(PIECES)):
        for sq in range(64):
            ZOBRIST_PIECES[i][sq] = random.getrandbits(64)
    ZOBRIST_SIDE = random.getrandbits(64)

def piece_index(ch):
    try:
        return PIECES.index(ch)
    except ValueError:
        return None

def compute_zobrist(board):
    key = 0
    for r in range(8):
        for c in range(8):
            p = board.get_piece(r,c)
            if p != '.':
                idx = piece_index(p)
                if idx is not None:
                    sq = r*8 + c
                    key ^= ZOBRIST_PIECES[idx][sq]
    if board.side_to_move == 'b':
        key ^= ZOBRIST_SIDE
    return key
