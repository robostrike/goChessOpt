# ai/random_agent.py

import random
from engine.generator import generate_moves

class RandomAgent:
    def get_moves(self, grid, faction, piece_cooldowns=None):
        moves = generate_moves(grid, faction, piece_cooldowns)
        return random.sample(moves, k=min(5, len(moves)))
