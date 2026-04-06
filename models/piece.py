# models/piece.py

class Piece:
    def __init__(self, faction, kind):
        self.faction = faction
        self.kind = kind
    
    def get_valid_moves(self, grid, x, y):
        """Return list of valid (x, y) positions this piece can move to"""
        if self.kind == "pawn":
            return self._get_pawn_moves(grid, x, y)
        elif self.kind == "knight":
            return self._get_knight_moves(grid, x, y)
        elif self.kind == "bishop":
            return self._get_bishop_moves(grid, x, y)
        elif self.kind == "rook":
            return self._get_rook_moves(grid, x, y)
        elif self.kind == "queen":
            return self._get_queen_moves(grid, x, y)
        elif self.kind == "king":
            return self._get_king_moves(grid, x, y)
        else:
            return []
    
    def _get_pawn_moves(self, grid, x, y):
        """Pawns move forward one square (simplified)"""
        moves = []
        # Determine forward direction based on faction
        forward = -1 if self.faction == "A" else 1
        
        # Move forward
        nx, ny = x, y + forward
        if self._in_bounds(grid, nx, ny) and not grid.cells[nx][ny]:
            moves.append((nx, ny))
        
        # Capture diagonally
        for dx in [-1, 1]:
            nx, ny = x + dx, y + forward
            if (self._in_bounds(grid, nx, ny) and grid.cells[nx][ny] and 
                grid.cells[nx][ny][0].faction != self.faction):
                moves.append((nx, ny))
        
        return moves
    
    def _get_knight_moves(self, grid, x, y):
        """Knights move in L-shape: 2 squares in one direction, 1 in perpendicular"""
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]
        
        moves = []
        for dx, dy in knight_moves:
            nx, ny = x + dx, y + dy
            if self._in_bounds(grid, nx, ny):
                target = grid.cells[nx][ny]
                if not target or target[0].faction != self.faction:
                    moves.append((nx, ny))
        
        return moves
    
    def _get_bishop_moves(self, grid, x, y):
        """Bishops move diagonally any distance"""
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dx, dy in directions:
            for i in range(1, grid.size):
                nx, ny = x + dx * i, y + dy * i
                if not self._in_bounds(grid, nx, ny):
                    break
                
                target = grid.cells[nx][ny]
                if not target:
                    moves.append((nx, ny))
                else:
                    if target[0].faction != self.faction:
                        moves.append((nx, ny))
                    break  # Can't move past any piece
        
        return moves
    
    def _get_rook_moves(self, grid, x, y):
        """Rooks move horizontally or vertically any distance"""
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dx, dy in directions:
            for i in range(1, grid.size):
                nx, ny = x + dx * i, y + dy * i
                if not self._in_bounds(grid, nx, ny):
                    break
                
                target = grid.cells[nx][ny]
                if not target:
                    moves.append((nx, ny))
                else:
                    if target[0].faction != self.faction:
                        moves.append((nx, ny))
                    break  # Can't move past any piece
        
        return moves
    
    def _get_queen_moves(self, grid, x, y):
        """Queen combines rook and bishop moves"""
        return self._get_rook_moves(grid, x, y) + self._get_bishop_moves(grid, x, y)
    
    def _get_king_moves(self, grid, x, y):
        """King moves one square in any direction"""
        moves = []
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), 
                     (0, 1), (1, -1), (1, 0), (1, 1)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self._in_bounds(grid, nx, ny):
                target = grid.cells[nx][ny]
                if not target or target[0].faction != self.faction:
                    moves.append((nx, ny))
        
        return moves
    
    def _in_bounds(self, grid, x, y):
        """Check if position is within grid bounds"""
        return 0 <= x < grid.size and 0 <= y < grid.size
