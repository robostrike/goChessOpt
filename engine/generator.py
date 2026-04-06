# engine/generator.py

def generate_moves(grid, faction):
    moves = []

    for x in range(grid.size):
        for y in range(grid.size):
            cell = grid.cells[x][y]

            if not cell:
                continue

            piece = cell[0]

            if piece.faction != faction:
                continue

            # Movement + Capture
            moves.extend(get_adjacent_moves(grid, x, y, piece))

            # Reproduction (new rule)
            if has_empty_neighbor(grid, x, y):
                moves.append({
                    "type": "reproduce",
                    "x": x,
                    "y": y,
                    "faction": faction
                })

    return moves


# ----------------------------
# Movement Logic
# ----------------------------

def get_adjacent_moves(grid, x, y, piece):
    directions = [(-1,0),(1,0),(0,-1),(0,1)]
    moves = []

    for dx, dy in directions:
        nx, ny = x + dx, y + dy

        if not in_bounds(grid, nx, ny):
            continue

        target_cell = grid.cells[nx][ny]

        # Move ONLY if empty
        if not target_cell:
            moves.append({
                "type": "move",
                "from": (x, y),
                "to": (nx, ny),
                "piece": piece
            })

        # Capture ONLY if enemy
        elif target_cell and target_cell[0].faction != piece.faction:
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

def has_empty_neighbor(grid, x, y):
    directions = [(-1,0),(1,0),(0,-1),(0,1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if in_bounds(grid, nx, ny) and not grid.cells[nx][ny]:
            return True

    return False


def in_bounds(grid, x, y):
    return 0 <= x < grid.size and 0 <= y < grid.size
