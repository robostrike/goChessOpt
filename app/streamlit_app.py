import sys
import os

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import random

from models.grid import Grid
from models.piece import Piece
from engine.game import run_turn
from ai.random_agent import RandomAgent
from config.constants import PIECE_VALUE


# ----------------------------
# CONFIG
# ----------------------------

GRID_SIZE = 20

FACTION_COLORS = {
    "A": "#4A90E2",
    "B": "#E94E4E",
}

PIECE_SYMBOLS = {
    "pawn": "P",
    "knight": "K",
    "bishop": "B",
    "rook": "R",
    "queen": "Q"
}


# ----------------------------
# INIT STATE
# ----------------------------

if "grid" not in st.session_state:
    st.session_state.grid = Grid(GRID_SIZE)

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

def get_strongest_piece(cell):
    return max(cell, key=lambda p: PIECE_VALUE[p.kind])

def render_grid(grid):
    for row in grid.cells:
        cols = st.columns(len(row))

        for i, cell in enumerate(row):
            if not cell:
                cols[i].markdown(
                    "<div style='text-align:center;'>.</div>",
                    unsafe_allow_html=True
                )
                continue

            piece = cell[0]

            color = FACTION_COLORS.get(piece.faction, "#999")
            symbol = PIECE_SYMBOLS.get(piece.kind, "?")

            cols[i].markdown(f"""
                <div style="
                    background-color:{color};
                    padding:6px;
                    text-align:center;
                    color:white;
                    font-weight:bold;
                    border-radius:4px;
                ">
                    {symbol}
                </div>
            """, unsafe_allow_html=True)


render_grid(st.session_state.grid)
