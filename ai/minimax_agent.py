# ai/minimax_agent.py
class MinimaxAgent:
    def __init__(self, depth=2):
        self.depth = depth

    def get_moves(self, grid, faction):
        best_move = None
        best_score = -float("inf")

        for move in generate_moves(grid, faction):
            new_grid = simulate(grid, move)
            score = minimax(new_grid, self.depth, faction)

            if score > best_score:
                best_score = score
                best_move = move

        return [best_move]
