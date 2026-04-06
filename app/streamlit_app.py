# app/streamlit_app.py
import streamlit as st
from engine.game import run_turn
from models.grid import Grid
from ai.random_agent import RandomAgent

st.title("Territorial Chess")

if "grid" not in st.session_state:
    st.session_state.grid = Grid(20)

agent = RandomAgent()

if st.button("Next Turn"):
    run_turn(st.session_state.grid, "A", agent)

render_grid(st.session_state.grid)
