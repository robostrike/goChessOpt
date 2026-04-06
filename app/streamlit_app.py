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
ACTION = 0

# Responsive grid configuration
def get_grid_config():
    """Get responsive grid configuration based on screen size"""
    # Use CSS container queries for better responsiveness
    return {
        'cell_size': 'min(40px, max(20px, 4vw))',  # Responsive cell size
        'font_size': 'min(20px, max(12px, 2vw))',  # Responsive font size
        'gap': 'min(3px, max(1px, 0.2vw))',       # Responsive gap
        'grid_max_size': 'min(800px, 90vw)'        # Max grid container size
    }

FACTION_COLORS = {
    "A": "#4A90E2",
    "B": "#E94E4E",
}

PIECE_SYMBOLS = {
    "pawn": "♙",
    "knight": "♘",
    "bishop": "♗",
    "rook": "♖",
    "queen": "♕",
    "king": "♔"
}


# ----------------------------
# INIT STATE
# ----------------------------


def get_random_empty_cell(grid):
    import random

    while True:
        x = random.randint(0, grid.size - 1)
        y = random.randint(0, grid.size - 1)

        if not grid.cells[x][y]:
            return x, y


if "grid" not in st.session_state:
    st.session_state.grid = Grid(GRID_SIZE)

    factions = ["A", "B"]
    unit_types = ["pawn", "knight", "bishop", "rook", "king"]

    for faction in factions:
        # 👑 Spawn KING first
        x, y = get_random_empty_cell(st.session_state.grid)
        st.session_state.grid.cells[x][y] = [Piece(faction, "king")]

        # 🔢 Spawn 4 more random units (total = 5)
        for _ in range(4):
            x, y = get_random_empty_cell(st.session_state.grid)
            kind = random.choice(unit_types)
            st.session_state.grid.cells[x][y] = [Piece(faction, kind)]


# ----------------------------
# UI
# ----------------------------

st.title("Territorial Chess Simulation")

agent_A = RandomAgent()
agent_B = RandomAgent()

if st.button("Next Turn"):
    if ACTION == 0:
        run_turn(st.session_state.grid, "A", agent_A)
    else:
        run_turn(st.session_state.grid, "B", agent_B)
    ACTION = ACTION*(-1) - 1

# ----------------------------
# RENDER GRID
# ----------------------------

def get_strongest_piece(cell):
    return max(cell, key=lambda p: PIECE_VALUE[p.kind])

def render_grid(grid):
    config = get_grid_config()
    
    # Create responsive grid container with CSS Grid
    grid_html = f"""
    <div style="
        display: grid;
        grid-template-columns: repeat({grid.size}, minmax({config['cell_size']}, 1fr));
        grid-auto-rows: minmax({config['cell_size']}, 1fr);
        gap: {config['gap']};
        width: {config['grid_max_size']};
        height: {config['grid_max_size']};
        margin: 20px auto;
        background-color: #f8f9fa;
        padding: 8px;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e9ecef;
        aspect-ratio: 1;
    ">
    """
    
    for row_idx, row in enumerate(grid.cells):
        for col_idx, cell in enumerate(row):
            if not cell:
                # Empty cell with subtle styling
                grid_html += f"""
                <div style="
                    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                    border: 1px solid #e9ecef;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: {config['font_size']};
                    color: #adb5bd;
                    border-radius: 4px;
                    transition: all 0.15s ease;
                    position: relative;
                    overflow: hidden;
                " onmouseover="this.style.background='linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)'" 
                   onmouseout="this.style.background='linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)'">
                    <span style="opacity: 0.3;">·</span>
                </div>
                """
            else:
                piece = cell[0]
                color = FACTION_COLORS.get(piece.faction, "#6c757d")
                symbol = PIECE_SYMBOLS.get(piece.kind, "?")
                
                # Piece cell with enhanced styling
                grid_html += f"""
                <div style="
                    background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                    border: 2px solid {color};
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: {config['font_size']};
                    color: white;
                    font-weight: bold;
                    border-radius: 6px;
                    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
                    cursor: pointer;
                    position: relative;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
                    text-shadow: 0 1px 2px rgba(0,0,0,0.2);
                " onmouseover="this.style.transform='scale(1.05) translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.25)'" 
                   onmouseout="this.style.transform='scale(1) translateY(0)'; this.style.boxShadow='0 2px 8px rgba(0,0,0,0.15)'">
                    {symbol}
                </div>
                """
    
    grid_html += "</div>"
    
    # Add responsive CSS for better mobile experience
    st.markdown("""
    <style>
    @media (max-width: 768px) {
        .stApp > div {
            padding: 0.5rem !important;
        }
    }
    
    @media (max-width: 480px) {
        .stApp > div {
            padding: 0.25rem !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(grid_html, unsafe_allow_html=True)


render_grid(st.session_state.grid)
