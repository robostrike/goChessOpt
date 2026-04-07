# engine/generator.py

def generate_moves(grid, faction, piece_cooldowns=None):
    """
    Generate all possible moves for a faction, respecting cooldowns
    piece_cooldowns: dict tracking cooldowns for pieces at specific positions
    """
    moves = []
    
    # Initialize cooldowns if not provided
    if piece_cooldowns is None:
        piece_cooldowns = {}

    for x in range(grid.size):
        for y in range(grid.size):
            cell = grid.cells[x][y]

            if not cell:
                continue

            piece = cell[0]

            if piece.faction != faction:
                continue
            
            # Check if this piece is on cooldown
            piece_key = f"{x}_{y}"
            if piece_key in piece_cooldowns and piece_cooldowns[piece_key] > 0:
                # Piece is on cooldown, skip movement/capture moves
                # But still allow reproduction
                if has_empty_neighbor(grid, x, y):
                    moves.append({
                        "type": "reproduce",
                        "x": x,
                        "y": y,
                        "faction": faction
                    })
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
