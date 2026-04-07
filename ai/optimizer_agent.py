# ai/optimizer_agent.py

import random
from engine.generator import generate_moves
from engine.territorial import calculate_territorial_control, calculate_territorial_score
from engine.game import apply_move
import copy

class OptimizerAgent:
    def __init__(self, depth=1):
        self.depth = depth  # How many moves ahead to look
    
    def get_moves(self, grid, faction, piece_cooldowns=None):
        """Get the best moves for the faction using optimization"""
        all_moves = generate_moves(grid, faction, piece_cooldowns)
        
        if not all_moves:
            return []
        
        # Evaluate each move and score the resulting board state
        scored_moves = []
        for move in all_moves:
            score = self._evaluate_move(grid, move, faction, piece_cooldowns)
            scored_moves.append((move, score))
        
        # Sort by score (descending) and return top moves
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        
        # Return top 3-5 best moves for variety
        top_moves = [move for move, score in scored_moves[:5]]
        
        # Add some randomness to avoid being too predictable
        if len(top_moves) > 1 and random.random() < 0.3:  # 30% chance to pick 2nd best
            return random.sample(top_moves, min(3, len(top_moves)))
        
        return top_moves
    
    def _evaluate_move(self, grid, move, faction, piece_cooldowns=None):
        """Evaluate a move by simulating it and scoring result"""
        # Check if piece is on cooldown and return 0 if so
        if piece_cooldowns is not None and move["type"] in ["move", "capture"]:
            piece_key = f"{move['from'][0]}_{move['from'][1]}"
            if piece_key in piece_cooldowns and piece_cooldowns[piece_key] > 0:
                return 0  # Give weight 0 to cooldown pieces
        
        # Create a deep copy of the grid to simulate the move
        sim_grid = copy.deepcopy(grid)
        
        # Apply the move to the simulated grid
        apply_move(sim_grid, move)
        
        # Calculate territorial control for the resulting board state
        territory, influence = calculate_territorial_control(sim_grid, k=3)
        
        # Primary metric: Number of cells controlled by this faction
        controlled_cells = sum(1 for row in territory for cell in row if cell == faction)
        
        # Secondary metric: Total influence strength (weighted by distance)
        total_influence = 0
        for x in range(sim_grid.size):
            for y in range(sim_grid.size):
                if territory[x][y] == faction:
                    total_influence += influence[x][y]
        
        # Tertiary metric: Positional advantage (center control)
        center_x, center_y = sim_grid.size // 2, sim_grid.size // 2
        positional_bonus = 0
        if move["type"] in ["move", "capture"]:
            to_x, to_y = move["to"]
            # Distance from center (closer is better)
            dist_from_center = abs(to_x - center_x) + abs(to_y - center_y)
            max_dist = center_x + center_y
            positional_bonus = (max_dist - dist_from_center) / max_dist * 5
        
        # Bonus for captures (removes enemy influence)
        capture_bonus = 3 if move["type"] == "capture" else 0
        
        # Bonus for reproduction (adds new pieces)
        reproduction_bonus = 2 if move["type"] == "reproduce" else 0
        
        # Mobility bonus: pieces that move to positions with more future options
        mobility_bonus = 0
        if move["type"] in ["move", "capture"]:
            piece = move["piece"]
            to_x, to_y = move["to"]
            
            # Count potential moves from new position
            future_moves = piece.get_valid_moves(sim_grid, to_x, to_y)
            mobility_bonus = len(future_moves) * 0.5
        
        # Calculate final score
        # Weight territorial control much higher than piece value
        final_score = (
            controlled_cells * 10 +           # Primary: Territory control
            total_influence * 2 +            # Secondary: Influence strength
            positional_bonus +                # Tertiary: Positional advantage
            mobility_bonus +                  # Bonus: Future mobility
            capture_bonus +                  # Bonus: Captures
            reproduction_bonus                 # Bonus: Reproduction
        )
        
        return final_score
    
    def get_best_move(self, grid, faction, piece_cooldowns=None):
        """Get the single best move (no randomness)"""
        all_moves = generate_moves(grid, faction, piece_cooldowns)
        
        if not all_moves:
            return None
        
        best_move = None
        best_score = float('-inf')
        
        for move in all_moves:
            score = self._evaluate_move(grid, move, faction, piece_cooldowns)
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def analyze_move_types(self, grid, faction, piece_cooldowns=None):
        """Analyze which types of moves are most beneficial"""
        all_moves = generate_moves(grid, faction, piece_cooldowns)
        
        move_analysis = {
            'move': {'count': 0, 'avg_score': 0, 'best_score': 0},
            'capture': {'count': 0, 'avg_score': 0, 'best_score': 0},
            'reproduce': {'count': 0, 'avg_score': 0, 'best_score': 0}
        }
        
        move_scores = {'move': [], 'capture': [], 'reproduce': []}
        
        for move in all_moves:
            score = self._evaluate_move(grid, move, faction, piece_cooldowns)
            move_type = move['type']
            
            move_analysis[move_type]['count'] += 1
            move_scores[move_type].append(score)
            
            if score > move_analysis[move_type]['best_score']:
                move_analysis[move_type]['best_score'] = score
        
        # Calculate average scores
        for move_type in move_scores:
            if move_scores[move_type]:
                move_analysis[move_type]['avg_score'] = sum(move_scores[move_type]) / len(move_scores[move_type])
        
        return move_analysis
