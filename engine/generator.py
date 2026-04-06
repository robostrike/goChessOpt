# engine/generator.py

from config.constants import GRID_SIZE


def generate_moves(grid, faction):
    """
    Generate all possible moves for a faction.
    Returns a list of move dictionaries.
    """
    moves = []

    for x in range(grid.size):
        for y in range(grid.size):
            cell = grid.cells[x][y]

            if not cell:
                continue

            for piece in cell:
                if piece.faction != faction:
                    continue

                # Movement moves
                moves.extend(get_adjacent_moves(grid, x, y, piece))

                # Reproduction move
                if len(cell) >= 2:
                    moves.append({
                        "type": "reproduce",
                        "x": x,
                        "y": y,
                        "faction": faction
                    })

    return moves


# ----------------------------
# Movement (simple version)
# ----------------------------

def get_adjacent_moves(grid, x, y, piece):
    """
    Basic movement: up/down/left/right
    (You can later expand per piece type)
    """
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    moves = []

    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        if not in_bounds(grid, nx, ny):
            continue

        target_cell = grid.cells[nx][ny]

        # Move (empty or same faction)
        if not target_cell or all(p.faction == piece.faction for p in target_cell):
            moves.append({
                "type": "move",
                "from": (x, y),
                "to": (nx, ny),
                "piece": piece
            })

        # Capture (enemy present)
        elif any(p.faction != piece.faction for p in target_cell):
            moves.append({
                "type": "capture",
                "from": (x, y),
                "to": (nx, ny),
                "piece": piece
            })

    return moves


# ----------------------------
# Helpers
# ----------------------------

def in_bounds(grid, x, y):
    return 0 <= x < grid.size and 0 <= y < grid.size
