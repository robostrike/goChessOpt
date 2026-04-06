# engine/reproduction.py
def reproduce(cell):
    count = len(cell)

    if count < 2:
        return None
    elif count >= 5:
        return "queen"
    elif count == 4:
        return "rook"
    elif count == 3:
        return "bishop"
    return "pawn"
