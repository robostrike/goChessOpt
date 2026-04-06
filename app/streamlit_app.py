import streamlit as st

from models.grid import Grid
from models.piece import Piece
from engine.game import run_turn
from ai.random_agent import RandomAgent


# ----------------------------
# INIT STATE
# ----------------------------

GRID_SIZE = 20

if "grid" not in st.session_state:
    st.session_state.grid = Grid(GRID_SIZE)

    # Seed initial pieces
    import random
    for _ in range(10):
        x = random.randint(0, GRID_SIZE - 1)
        y = random.randint(0, GRID_SIZE - 1)
        faction = random.choice(["A", "B"])
        st.session_state.grid.add_piece(x, y, Piece(faction, "pawn"))


# ----------------------------
# UI
# ----------------------------

st.title("Territorial Chess Simulation")

agent_A = RandomAgent()
agent_B = RandomAgent()


if st.button("Next Turn"):
    run_turn(st.session_state.grid, "A", agent_A)
    run_turn(st.session_state.grid, "B", agent_B)


# ----------------------------
# RENDER GRID
# ----------------------------

def render_grid(grid):
    for row in grid.cells:
        cols = st.columns(len(row))
        for i, cell in enumerate(row):
            if not cell:
                cols[i].write(".")
            else:
                text = "".join([p.faction for p in cell])
                cols[i].write(text)


render_grid(st.session_state.grid)
