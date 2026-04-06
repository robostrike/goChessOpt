# ai/random_agent.py

import random
from engine.generator import generate_moves

class RandomAgent:
    def get_moves(self, grid, faction):
        moves = generate_moves(grid, faction)
        return random.sample(moves, k=min(5, len(moves)))
