from constants import WHITE, BLACK, PROMOTION_CHOICES

PIECES = ['P','N','B','R','Q','K','p','n','b','r','q','k']

def color_of(piece):
    if not piece or piece == '.':
        return None
    return WHITE if piece.isupper() else BLACK

def is_white(piece):
    return color_of(piece) == WHITE

def is_black(piece):
    return color_of(piece) == BLACK

def normalize_promo(piece, side):
    p = (piece or 'Q').upper()
    if p not in PROMOTION_CHOICES:
        p = 'Q'
    return p if side == WHITE else p.lower()

IMAGE_NAME_BY_PIECE = {
    'P': 'white_pawn.png', 'N': 'white_knight.png', 'B': 'white_bishop.png', 'R': 'white_rook.png',
    'Q': 'white_queen.png', 'K': 'white_king.png',
    'p': 'black_pawn.png', 'n': 'black_knight.png', 'b': 'black_bishop.png', 'r': 'black_rook.png',
    'q': 'black_queen.png', 'k': 'black_king.png',
}
