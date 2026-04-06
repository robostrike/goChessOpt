# engine/game.py

from engine.reproduction import reproduce
from engine.combat import resolve_combat
from models.piece import Piece


def run_turn(grid, faction, strategy):
    moves = strategy.get_moves(grid, faction)

    for move in moves:
        apply_move(grid, move)

    resolve_board(grid)


# ✅ THIS FUNCTION MUST EXIST
def apply_move(grid, move):
    move_type = move["type"]

    if move_type == "move":
        fx, fy = move["from"]
        tx, ty = move["to"]
        piece = move["piece"]

        if piece in grid.cells[fx][fy]:
            grid.cells[fx][fy].remove(piece)
            grid.cells[tx][ty].append(piece)

    elif move_type == "capture":
        fx, fy = move["from"]
        tx, ty = move["to"]
        piece = move["piece"]

        if piece in grid.cells[fx][fy]:
            grid.cells[tx][ty] = [
                p for p in grid.cells[tx][ty]
                if p.faction == piece.faction
            ]

            grid.cells[fx][fy].remove(piece)
            grid.cells[tx][ty].append(piece)

    elif move_type == "reproduce":
        x, y = move["x"], move["y"]
        faction = move["faction"]

        kind = reproduce(grid.cells[x][y])
        if kind:
            grid.cells[x][y].append(Piece(faction, kind))


def resolve_board(grid):
    for x in range(grid.size):
        for y in range(grid.size):
            cell = grid.cells[x][y]

            if not cell:
                continue

            grid.cells[x][y] = resolve_combat(cell)
