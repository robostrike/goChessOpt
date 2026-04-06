# engine/game.py
def run_turn(grid, faction, strategy):
    moves = strategy.get_moves(grid, faction)

    for move in moves:
        apply_move(grid, move)

    resolve_all_cells(grid)
