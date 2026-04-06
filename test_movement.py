#!/usr/bin/env python3

import sys
import os

# Fix import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from models.grid import Grid
from models.piece import Piece
from engine.generator import generate_moves

def test_piece_movement():
    # Create a small test grid
    grid = Grid(8)
    
    # Test different piece types in the center
    test_pieces = [
        ("A", "pawn", 3, 3),
        ("A", "knight", 3, 3),
        ("A", "bishop", 3, 3),
        ("A", "rook", 3, 3),
        ("A", "queen", 3, 3),
        ("A", "king", 3, 3),
    ]
    
    for faction, kind, x, y in test_pieces:
        # Clear grid
        grid = Grid(8)
        
        # Place piece
        piece = Piece(faction, kind)
        grid.cells[x][y] = [piece]
        
        # Generate moves
        moves = generate_moves(grid, faction)
        
        print(f"\n{kind.upper()} at ({x},{y}):")
        print(f"Total moves generated: {len(moves)}")
        
        # Show move destinations
        destinations = [move["to"] for move in moves if move["type"] in ["move", "capture"]]
        print(f"Destinations: {destinations}")
        
        # Test piece's own method
        direct_moves = piece.get_valid_moves(grid, x, y)
        print(f"Direct method: {direct_moves}")

if __name__ == "__main__":
    test_piece_movement()
