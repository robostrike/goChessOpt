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
from ai.optimizer_agent import OptimizerAgent
from config.constants import PIECE_VALUE
from engine.territorial import (
    calculate_territorial_control, 
    calculate_territorial_score,
    get_territorial_color
)


# ----------------------------
# CONFIG
# ----------------------------

GRID_SIZE = 20

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


def get_random_empty_cell_within_distance(grid, center_x, center_y, max_distance):
    """Find empty cell within specified distance from center point"""
    import random
    
    attempts = 0
    max_attempts = 100
    
    while attempts < max_attempts:
        # Generate random position within distance bounds
        dx = random.randint(-max_distance, max_distance)
        dy = random.randint(-max_distance, max_distance)
        
        # Check if within distance (using Manhattan distance for simplicity)
        if abs(dx) + abs(dy) <= max_distance:
            x = center_x + dx
            y = center_y + dy
            
            # Check bounds and if empty
            if (0 <= x < grid.size and 0 <= y < grid.size and 
                not grid.cells[x][y]):
                return x, y
        
        attempts += 1
    
    # Fallback to any empty cell if can't find within distance
    return get_random_empty_cell(grid)


def get_spawn_distance(piece_type):
    """Return spawn distance for each piece type"""
    spawn_distances = {
        "pawn": 1,
        "rook": 2,
        "bishop": 2,
        "knight": 2,
        "queen": 1,
        "king": 5
    }
    return spawn_distances.get(piece_type, 1)


if "grid" not in st.session_state:
    st.session_state.grid = Grid(GRID_SIZE)

    factions = ["A", "B"]
    unit_types = ["pawn", "knight", "bishop", "rook", "queen"]

    for faction in factions:
        # 👑 Spawn KING first
        king_x, king_y = get_random_empty_cell(st.session_state.grid)
        st.session_state.grid.cells[king_x][king_y] = [Piece(faction, "king")]

        # 🔢 Spawn 4 more random units within distance from king
        for _ in range(4):
            kind = random.choice(unit_types)
            spawn_distance = get_spawn_distance(kind)
            x, y = get_random_empty_cell_within_distance(
                st.session_state.grid, king_x, king_y, spawn_distance
            )
            st.session_state.grid.cells[x][y] = [Piece(faction, kind)]


# ----------------------------
# UI
# ----------------------------

st.title("Territorial Chess Simulation")

# Agent selection sidebar
st.sidebar.header("Agent Configuration")
use_optimizer = st.sidebar.checkbox("Use Optimizer Agent", value=True)
agent_depth = st.sidebar.slider("Optimization Depth", min_value=1, max_value=3, value=1)

# Initialize turn state and cooldown tracking
if "current_turn" not in st.session_state:
    st.session_state.current_turn = "A"  # Start with faction A
if "piece_cooldowns_A" not in st.session_state:
    st.session_state.piece_cooldowns_A = {}
if "piece_cooldowns_B" not in st.session_state:
    st.session_state.piece_cooldowns_B = {}

# Initialize agents
if use_optimizer:
    agent_A = OptimizerAgent(depth=agent_depth)
    agent_B = OptimizerAgent(depth=agent_depth)
else:
    agent_A = RandomAgent()
    agent_B = RandomAgent()

# Debug information in sidebar
st.sidebar.header("Debug Information")
st.sidebar.write(f"**Current turn:** {st.session_state.current_turn}")
st.sidebar.write(f"**Agent type:** {'Optimizer' if use_optimizer else 'Random'}")
if use_optimizer:
    st.sidebar.write(f"**Optimization depth:** {agent_depth}")

# Show cooldown information
current_cooldowns = st.session_state.piece_cooldowns_A if st.session_state.current_turn == "A" else st.session_state.piece_cooldowns_B
if current_cooldowns:
    st.sidebar.subheader("Active Cooldowns:")
    for piece_key, cooldown in current_cooldowns.items():
        x, y = piece_key.split('_')
        st.sidebar.write(f"- Piece at ({x}, {y}): {cooldown} turns")
else:
    st.sidebar.write("**No active cooldowns**")

# Show pieces on board
st.sidebar.subheader("Pieces on Board")
pieces_info = []
for x in range(st.session_state.grid.size):
    for y in range(st.session_state.grid.size):
        cell = st.session_state.grid.cells[x][y]
        if cell:
            piece = cell[0]
            pieces_info.append(f"{piece.faction} {piece.kind} at ({x},{y})")

for info in pieces_info:
    st.sidebar.write(f"- {info}")

# Show available moves and optimization analysis
st.sidebar.subheader("Move Analysis")
if st.session_state.current_turn == "A":
    moves = agent_A.get_moves(st.session_state.grid, "A")
    if use_optimizer:
        analysis = agent_A.analyze_move_types(st.session_state.grid, "A")
        st.sidebar.write("**Faction A:**")
        for move_type, data in analysis.items():
            if data['count'] > 0:
                st.sidebar.write(f"- {move_type}: {data['count']} moves, avg: {data['avg_score']:.1f}, best: {data['best_score']:.1f}")
else:
    moves = agent_B.get_moves(st.session_state.grid, "B")
    if use_optimizer:
        analysis = agent_B.analyze_move_types(st.session_state.grid, "B")
        st.sidebar.write("**Faction B:**")
        for move_type, data in analysis.items():
            if data['count'] > 0:
                st.sidebar.write(f"- {move_type}: {data['count']} moves, avg: {data['avg_score']:.1f}, best: {data['best_score']:.1f}")

st.sidebar.write(f"**Available moves:** {len(moves)}")
st.sidebar.subheader("Top 5 Available Moves:")
for i, move in enumerate(moves[:5]):  # Show first 5 moves
    if move["type"] in ["move", "capture"]:
        st.sidebar.write(f"{i+1}. {move['type']}: {move['from']} -> {move['to']} ({move['piece'].kind})")
    elif move["type"] == "reproduce":
        st.sidebar.write(f"{i+1}. {move['type']}: at ({move['x']}, {move['y']})")

if st.button("Next Turn"):
    if st.session_state.current_turn == "A":
        run_turn(st.session_state.grid, "A", agent_A, st.session_state.piece_cooldowns_A)
        st.session_state.current_turn = "B"
    else:
        run_turn(st.session_state.grid, "B", agent_B, st.session_state.piece_cooldowns_B)
        st.session_state.current_turn = "A"

# ----------------------------
# RENDER GRID
# ----------------------------

def get_strongest_piece(cell):
    return max(cell, key=lambda p: PIECE_VALUE[p.kind])

def render_grid(grid):
    # Calculate territorial control
    territory, influence = calculate_territorial_control(grid, k=3)
    scores = calculate_territorial_score(grid, territory)
    
    # Display territorial scores with color indicators
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        # Faction A with color indicator
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 8px;">
            <div style="width: 20px; height: 20px; background-color: {FACTION_COLORS['A']}; border-radius: 4px;"></div>
            <div>
                <div style="font-size: 0.8rem; color: #666;">Faction A</div>
                <div style="font-size: 1.2rem; font-weight: bold;">{scores["A"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Dynamic divider bar
        total = scores["A"] + scores["B"]
        if total > 0:
            a_percentage = scores["A"] / total
            b_percentage = scores["B"] / total
            
            st.markdown(f"""
            <div style="padding: 10px 0;">
                <div style="font-size: 0.8rem; color: #666; text-align: center; margin-bottom: 5px;">Territory Control</div>
                <div style="height: 30px; border-radius: 15px; overflow: hidden; display: flex; border: 1px solid #ddd;">
                    <div style="width: {a_percentage*100}%; background-color: {FACTION_COLORS['A']}; display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-size: 0.7rem; font-weight: bold;">{a_percentage*100:.0f}%</span>
                    </div>
                    <div style="width: {b_percentage*100}%; background-color: {FACTION_COLORS['B']}; display: flex; align-items: center; justify-content: center;">
                        <span style="color: white; font-size: 0.7rem; font-weight: bold;">{b_percentage*100:.0f}%</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="padding: 10px 0;">
                <div style="font-size: 0.8rem; color: #666; text-align: center; margin-bottom: 5px;">Territory Control</div>
                <div style="height: 30px; border-radius: 15px; background-color: #f0f0f0; display: flex; align-items: center; justify-content: center; border: 1px solid #ddd;">
                    <span style="color: #666; font-size: 0.8rem;">No Territory</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        # Faction B with color indicator
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 8px; justify-content: flex-end;">
            <div style="text-align: right;">
                <div style="font-size: 0.8rem; color: #666; text-align: right;">Faction B</div>
                <div style="font-size: 1.2rem; font-weight: bold;">{scores["B"]}</div>
            </div>
            <div style="width: 20px; height: 20px; background-color: {FACTION_COLORS['B']}; border-radius: 4px;"></div>
        </div>
        """, unsafe_allow_html=True)
    
    # CSS for equal-sized grid cells
    st.markdown("""
    <style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(20, 1fr);
        gap: 1px;
        width: 100%;
        aspect-ratio: 1;
        max-width: 90vh;
        margin: 0 auto;
    }
    .grid-cell {
        aspect-ratio: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: bold;
        border: 1px solid #e0e0e0;
    }
    .piece-cell {
        color: white !important;
    }
    .territory-cell {
        font-size: 0.5rem !important;
        color: #333 !important;
    }
    .neutral-cell {
        color: #999 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Build grid HTML
    grid_html = '<div class="grid-container">'
    
    for y in range(grid.size):
        for x in range(grid.size):
            cell = grid.cells[x][y]
            
            if cell:
                # Piece cell
                piece = cell[0]
                color = FACTION_COLORS.get(piece.faction, "#999")
                symbol = PIECE_SYMBOLS.get(piece.kind, "?")
                grid_html += f'<div class="grid-cell piece-cell" style="background-color:{color};">{symbol}</div>'
            else:
                # Empty cell
                faction = territory[x][y]
                influence_val = influence[x][y]
                
                if faction and influence_val > 0:
                    # Territorial coloring with 50% opacity
                    base_color = FACTION_COLORS.get(faction, "#999")
                    light_color = get_territorial_color(base_color, influence_val)
                    grid_html += f'<div class="grid-cell territory-cell" style="background-color:{light_color}; opacity: 0.5;">.</div>'
                else:
                    # Neutral cell with white dot
                    grid_html += '<div class="grid-cell neutral-cell" style="background-color:#f8f9fa; color: white;">.</div>'
    
    grid_html += '</div>'
    st.markdown(grid_html, unsafe_allow_html=True)


render_grid(st.session_state.grid)
