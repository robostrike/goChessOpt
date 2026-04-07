# engine/game.py

import random
from engine.reproduction import reproduce
from engine.territorial import calculate_territorial_control, calculate_territorial_score
from models.piece import Piece


def evaluate_move_territory(grid, move, faction):
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
    
    # Return the score for the current faction
    return scores.get(faction, 0)


def get_strategic_moves(grid, faction, moves):
    """
    Evaluate all possible moves and return them sorted by territory gain
    Returns: List of moves sorted by territory score (descending)
    """
    move_scores = []
    
    for move in moves:
        if move["type"] in ["move", "capture"]:
            territory_score = evaluate_move_territory(grid, move, faction)
            move_scores.append({
                'move': move,
                'territory_score': territory_score
            })
    
    # Sort by territory score (descending)
    move_scores.sort(key=lambda x: x['territory_score'], reverse=True)
    
    return [item['move'] for item in move_scores]


def run_turn(grid, faction, strategy):
    moves = strategy.get_moves(grid, faction)
    
    # Phase 1: Evaluate and sort moves by territory gain
    strategic_moves = get_strategic_moves(grid, faction, moves)
    
    # Phase 2: Group strategic moves by destination
    move_targets = {}

    for move in strategic_moves:
        if move["type"] in ["move", "capture"]:
            tx, ty = move["to"]
            move_targets.setdefault((tx, ty), []).append(move)

    # Phase 3: Resolve conflicts (prioritize higher-scoring moves)
    valid_moves = []

    for target, competing_moves in move_targets.items():
        if len(competing_moves) == 1:
            valid_moves.append(competing_moves[0])
        else:
            # Choose the move with highest territory score (first in list due to sorting)
            valid_moves.append(competing_moves[0])

    # Include reproduction moves (no conflict with movement)
    for move in moves:
        if move["type"] == "reproduce":
            valid_moves.append(move)

    # Phase 4: Apply moves
    for move in valid_moves:
        apply_move(grid, move)


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
