# engine/game.py

from engine.reproduction import reproduce
from engine.combat import resolve_combat
from models.piece import Piece


# ----------------------------
# MAIN TURN LOOP
# ----------------------------

def run_turn(grid, faction, strategy):
    """
    Executes a full turn for one faction:
    1. Get moves from agent
    2. Apply moves
    3. Resolve board state (combat + reproduction)
    """

    moves = strategy.get_moves(grid, faction)

    # Apply moves
    for move in moves:
        apply_move(grid, move)

    # Resolve conflicts AFTER all moves
    resolve_board(grid)


# ----------------------------
# APPLY MOVES
# ----------------------------

def apply_move(grid, move):
    move_type = move["type"]

    if move_type == "move":
        fx, fy = move["from"]
        tx, ty = move["to"]
        piece = move["piece"]

        # Safety check
        if piece in grid.cells[fx][fy]:
            grid.cells[fx][fy].remove(piece)
            grid.cells[tx][ty].append(piece)

    elif move_type == "capture":
        fx, fy = move["from"]
        tx, ty = move["to"]
        piece = move["piece"]

        if piece in grid.cells[fx][fy]:
            # Remove enemies at destination
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


# ----------------------------
# RESOLUTION PHASE
# ----------------------------

def resolve_board(grid):
    """
    After all moves:
    - Resolve combat in each cell
    - (Optional) Apply global rules
    """

    for x in range(grid.size):
        for y in range(grid.size):
            cell = grid.cells[x][y]

            if not cell:
                continue

            # Resolve combat if multiple factions present
            grid.cells[x][y] = resolve_combat(cell)
