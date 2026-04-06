# engine/game.py

from engine.reproduction import reproduce
from engine.combat import resolve_combat
from models.piece import Piece


def run_turn(grid, faction, strategy):
    moves = strategy.get_moves(grid, faction)

    for move in moves:
        apply_move(grid, move)

    resolve_board(grid)


def apply_move(grid, move):
    move_type = move["type"]

    if move_type == "move":
        fx, fy = move["from"]
        tx, ty = move["to"]
        piece = move["piece"]

        if piece in grid.cells[fx][fy]:

            # ❌ Block movement if occupied
            if grid.cells[tx][ty]:
                return

            grid.cells[fx][fy].remove(piece)
            grid.cells[tx][ty] = [piece]


    elif move_type == "capture":
        fx, fy = move["from"]
        tx, ty = move["to"]
        piece = move["piece"]

        if piece in grid.cells[fx][fy]:

            # Only capture if enemy exists
            if grid.cells[tx][ty]:
                target = grid.cells[tx][ty][0]

                if target.faction != piece.faction:
                    grid.cells[fx][fy].remove(piece)
                    grid.cells[tx][ty] = [piece]


    elif move_type == "reproduce":
        x, y = move["x"], move["y"]
        faction = move["faction"]

        # ❌ Only reproduce into EMPTY adjacent cell
        empty_neighbors = get_empty_neighbors(grid, x, y)

        if not empty_neighbors:
            return

        nx, ny = empty_neighbors[0]  # simple choice

        kind = reproduce(grid.cells[x][y])
        if kind:
            grid.cells[nx][ny] = [Piece(faction, kind)]

def resolve_board(grid):
    for x in range(grid.size):
        for y in range(grid.size):
            cell = grid.cells[x][y]

            if not cell:
                continue

            grid.cells[x][y] = resolve_combat(cell)

def get_empty_neighbors(grid, x, y):
    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    result = []

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid.size and 0 <= ny < grid.size:
            if not grid.cells[nx][ny]:
                result.append((nx, ny))

    return result
