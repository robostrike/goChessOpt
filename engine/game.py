# engine/game.py

from engine.reproduction import reproduce
from models.piece import Piece


def run_turn(grid, faction, strategy):
    moves = strategy.get_moves(grid, faction)

    for move in moves:
        apply_move(grid, move)


def apply_move(grid, move):
    move_type = move["type"]

    if move_type == "move":
        fx, fy = move["from"]
        tx, ty = move["to"]
        piece = move["piece"]

        if piece in grid.cells[fx][fy] and not grid.cells[tx][ty]:
            grid.cells[fx][fy].remove(piece)
            grid.cells[tx][ty] = [piece]


    elif move_type == "capture":
        fx, fy = move["from"]
        tx, ty = move["to"]
        piece = move["piece"]

        if piece in grid.cells[fx][fy] and grid.cells[tx][ty]:
            target = grid.cells[tx][ty][0]

            if target.faction != piece.faction:
                grid.cells[fx][fy].remove(piece)
                grid.cells[tx][ty] = [piece]


    elif move_type == "reproduce":
        x, y = move["x"], move["y"]
        faction = move["faction"]

        empty_neighbors = get_empty_neighbors(grid, x, y)

        if not empty_neighbors:
            return

        nx, ny = empty_neighbors[0]

        kind = reproduce(grid.cells[x][y])
        if kind:
            grid.cells[nx][ny] = [Piece(faction, kind)]


# ----------------------------
# Helpers
# ----------------------------

def get_empty_neighbors(grid, x, y):
    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    result = []

    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        if 0 <= nx < grid.size and 0 <= ny < grid.size:
            if not grid.cells[nx][ny]:
                result.append((nx, ny))

    return result
