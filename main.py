# main.py

from models.grid import Grid
from models.piece import Piece
from engine.game import run_turn
from ai.random_agent import RandomAgent
# from ai.minimax_agent import MinimaxAgent

GRID_SIZE = 20
NUM_TURNS = 20


def seed_grid(grid):
    """Initialize starting pieces"""
    import random

    factions = ["A", "B"]

    for _ in range(10):
        x = random.randint(0, grid.size - 1)
        y = random.randint(0, grid.size - 1)

        faction = random.choice(factions)
        grid.add_piece(x, y, Piece(faction, "pawn"))


def count_pieces(grid):
    counts = {}

    for x in range(grid.size):
        for y in range(grid.size):
            for p in grid.cells[x][y]:
                counts[p.faction] = counts.get(p.faction, 0) + 1

    return counts


def print_grid_summary(grid, turn):
    counts = count_pieces(grid)
    print(f"\nTurn {turn}")
    for faction, count in counts.items():
        print(f"Faction {faction}: {count} pieces")


def main():
    grid = Grid(GRID_SIZE)

    # Seed initial state
    seed_grid(grid)

    # Agents
    agents = {
        "A": RandomAgent(),
        "B": RandomAgent(),
        # "B": MinimaxAgent(depth=2)
    }

    # Run simulation
    for turn in range(NUM_TURNS):
        for faction, agent in agents.items():
            run_turn(grid, faction, agent)

        print_grid_summary(grid, turn)

    print("\nFinal State:")
    print(count_pieces(grid))


if __name__ == "__main__":
    main()
