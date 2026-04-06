# models/grid.py
class Grid:
    def __init__(self, size):
        self.size = size
        self.cells = [[[] for _ in range(size)] for _ in range(size)]

    def get_cell(self, x, y):
        return self.cells[x][y]

    def add_piece(self, x, y, piece):
        self.cells[x][y].append(piece)
