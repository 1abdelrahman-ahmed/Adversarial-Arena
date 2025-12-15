class MoveCodec:
    @staticmethod
    def square_to_idx(s):
        if not s or len(s) != 2:
            return None
        file_ch, rank_ch = s[0], s[1]
        if file_ch < 'a' or file_ch > 'h':
            return None
        if rank_ch < '1' or rank_ch > '8':
            return None
        c = ord(file_ch) - ord('a')
        r = 8 - int(rank_ch)
        return (r, c)

    @staticmethod
    def idx_to_square(r, c):
        return chr(ord('a') + c) + str(8 - r)

    @staticmethod
    def parse_uci(txt):
        if txt is None:
            return None
        t = txt.strip().lower()
        if len(t) not in (4, 5):
            return None
        f = MoveCodec.square_to_idx(t[:2])
        to = MoveCodec.square_to_idx(t[2:4])
        if not f or not to:
            return None
        if len(t) == 5:
            return (f[0], f[1], to[0], to[1], t[4].upper())
        return (f[0], f[1], to[0], to[1])

    @staticmethod
    def to_uci(mv):
        fr, fc, tr, tc = mv[:4]
        s = MoveCodec.idx_to_square(fr, fc) + MoveCodec.idx_to_square(tr, tc)
        if len(mv) == 5:
            s += str(mv[4]).lower()
        return s
