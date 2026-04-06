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

            # Get piece-specific valid moves
            valid_positions = piece.get_valid_moves(grid, x, y)
            
            # Convert positions to move objects
            for nx, ny in valid_positions:
                target_cell = grid.cells[nx][ny]
                
                if not target_cell:
                    # Empty cell - move
                    moves.append({
                        "type": "move",
                        "from": (x, y),
                        "to": (nx, ny),
                        "piece": piece
                    })
                else:
                    # Enemy piece - capture
                    moves.append({
                        "type": "capture",
                        "from": (x, y),
                        "to": (nx, ny),
                        "piece": piece
                    })

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
# Helpers
# ----------------------------

def has_empty_neighbor(grid, x, y):
    """Check if there's at least one empty adjacent cell"""
    directions = [(-1,0),(1,0),(0,-1),(0,1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if in_bounds(grid, nx, ny) and not grid.cells[nx][ny]:
            return True

    return False


def in_bounds(grid, x, y):
    """Check if position is within grid bounds"""
    return 0 <= x < grid.size and 0 <= y < grid.size
