# engine/combat.py
from config.constants import PIECE_VALUE

def resolve_combat(cell):
    if len(set(p.faction for p in cell)) <= 1:
        return cell

    # simple strongest survives
    strongest = max(cell, key=lambda p: PIECE_VALUE[p.kind])
    return [strongest]
