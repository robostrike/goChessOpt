# engine/game.py

import random
from engine.reproduction import reproduce
from engine.territorial import calculate_territorial_control, calculate_territorial_score
from models.piece import Piece, PIECE_COOLDOWNS


def evaluate_move_territory(grid, move, faction, piece_cooldowns=None):
    """
    Evaluate the territory gain from a specific move
    Returns: territory_score (float)
    """
    # Create a deep copy of the grid to simulate the move
    import copy
    temp_grid = copy.deepcopy(grid)
    
    # Apply the move to the temporary grid
    apply_move(temp_grid, move)
    
    # Calculate territorial control after the move
    territory, influence = calculate_territorial_control(temp_grid)
    scores = calculate_territorial_score(temp_grid, territory)
    
    # Get base territory score
    base_score = scores.get(faction, 0)
    
    # Apply cooldown penalty if piece is on cooldown
    if piece_cooldowns is not None and move["type"] in ["move", "capture"]:
        piece = move["piece"]
        piece_key = f"{move['from'][0]}_{move['from'][1]}"  # Unique key for piece position
        
        if piece_key in piece_cooldowns and piece_cooldowns[piece_key] > 0:
            # Apply penalty based on remaining cooldown
            cooldown_penalty = piece_cooldowns[piece_key] * 5  # 5 points per cooldown turn
            base_score -= cooldown_penalty
    
    return base_score


def update_piece_cooldowns(piece_cooldowns, executed_move, current_turn):
    """
    Update cooldowns after a move is executed
    """
    if executed_move["type"] in ["move", "capture"]:
        piece = executed_move["piece"]
        piece_key = f"{executed_move['from'][0]}_{executed_move['from'][1]}"
        
        # Set cooldown for the moved piece
        cooldown = PIECE_COOLDOWNS.get(piece.kind, 1)
        piece_cooldowns[piece_key] = cooldown
    
    # Decrease all cooldowns by 1
    for key in list(piece_cooldowns.keys()):
        piece_cooldowns[key] = max(0, piece_cooldowns[key] - 1)
        
        # Remove entries with zero cooldown
        if piece_cooldowns[key] == 0:
            del piece_cooldowns[key]


def get_strategic_moves(grid, faction, moves, piece_cooldowns=None):
    """
    Evaluate all possible moves and return them sorted by territory gain
    Returns: List of moves sorted by territory score (descending)
    """
    move_scores = []
    
    for move in moves:
        if move["type"] in ["move", "capture"]:
            territory_score = evaluate_move_territory(grid, move, faction, piece_cooldowns)
            move_scores.append({
                'move': move,
                'territory_score': territory_score
            })
    
    # Sort by territory score (descending)
    move_scores.sort(key=lambda x: x['territory_score'], reverse=True)
    
    return [item['move'] for item in move_scores]


def run_turn(grid, faction, strategy, piece_cooldowns=None):
    """
    Run a turn with cooldown system
    piece_cooldowns: dict to track cooldowns across turns
    """
    # Initialize cooldowns if not provided
    if piece_cooldowns is None:
        piece_cooldowns = {}
    
    moves = strategy.get_moves(grid, faction, piece_cooldowns)
    
    if not moves:
        return None
    
    # Phase 1: Evaluate and sort moves by territory gain with cooldown consideration
    strategic_moves = get_strategic_moves(grid, faction, moves, piece_cooldowns)
    
    # Phase 2: Select only the best move (or reproduction if no movement moves)
    selected_move = None
    
    if strategic_moves:
        # Select the best strategic move (highest territory score)
        selected_move = strategic_moves[0]
    else:
        # No movement/capture moves, check for reproduction
        reproduction_moves = [move for move in moves if move["type"] == "reproduce"]
        if reproduction_moves:
            selected_move = reproduction_moves[0]
    
    # Phase 3: Apply the single selected move and update cooldowns
    if selected_move:
        apply_move(grid, selected_move)
        update_piece_cooldowns(piece_cooldowns, selected_move, faction)
    
    return selected_move


# ----------------------------
# APPLY MOVE
# ----------------------------

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

        nx, ny = random.choice(empty_neighbors)

        kind = reproduce(grid.cells[x][y])
        if kind:
            grid.cells[nx][ny] = [Piece(faction, kind)]


# ----------------------------
# HELPERS
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
