from .constants import EMPTY


class Cell:
    def __init__(self, color=EMPTY):
        self.color = color

    def flip(self):
        if self.color == '@':
            self.color = 'O'
        elif self.color == 'O':
            self.color = '@'

    def set_color(self, color):
        self.color = color

    def get_color(self):
        return self.color

    def is_empty(self):
        return self.color == EMPTY
