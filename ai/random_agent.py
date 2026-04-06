# ai/random_agent.py
import random

class RandomAgent:
    def get_moves(self, grid, faction):
        moves = generate_moves(grid, faction)
        return random.sample(moves, k=min(5, len(moves)))
