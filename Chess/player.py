class Player:
    def __init__(self, color, kind='human', depth=3):
        self.color = color
        self.kind = kind
        self.depth = int(depth) if depth is not None else 3

    @property
    def is_ai(self):
        return self.kind == 'ai'