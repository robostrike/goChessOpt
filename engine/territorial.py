# engine/territorial.py

def calculate_territorial_control(grid, k=3, piece_values=None):
    """
    Calculate territorial control using k-NN nearest neighbors
    Returns: 2D array of dominant faction and influence scores
    """
    if piece_values is None:
        from config.constants import PIECE_VALUE
        piece_values = PIECE_VALUE
    
    size = grid.size
    territory = [[None for _ in range(size)] for _ in range(size)]
    influence = [[0.0 for _ in range(size)] for _ in range(size)]
    
    # Collect all pieces with their positions
    pieces = []
    for x in range(size):
        for y in range(size):
            cell = grid.cells[x][y]
            if cell:
                piece = cell[0]
                pieces.append({
                    'x': x,
                    'y': y,
                    'faction': piece.faction,
                    'kind': piece.kind,
                    'value': piece_values.get(piece.kind, 1)
                })
    
    # For each grid cell, find k nearest pieces
    for x in range(size):
        for y in range(size):
            if not grid.cells[x][y]:  # Only calculate for empty cells
                # Calculate distance to all pieces
                distances = []
                for piece in pieces:
                    # Use Manhattan distance
                    dist = abs(x - piece['x']) + abs(y - piece['y'])
                    distances.append({
                        'dist': dist,
                        'faction': piece['faction'],
                        'value': piece['value']
                    })
                
                # Sort by distance and take k nearest
                distances.sort(key=lambda d: d['dist'])
                k_nearest = distances[:k]
                
                # Calculate influence based on distance and piece value
                faction_scores = {}
                for neighbor in k_nearest:
                    if neighbor['dist'] == 0:
                        influence_strength = neighbor['value']
                    else:
                        # Inverse distance weighting
                        influence_strength = neighbor['value'] / neighbor['dist']
                    
                    if neighbor['faction'] not in faction_scores:
                        faction_scores[neighbor['faction']] = 0
                    faction_scores[neighbor['faction']] += influence_strength
                
                # Determine dominant faction
                if faction_scores:
                    dominant_faction = max(faction_scores.items(), key=lambda x: x[1])
                    territory[x][y] = dominant_faction[0]
                    influence[x][y] = dominant_faction[1]
    
    return territory, influence


def calculate_territorial_score(grid, territory, piece_control_weight=10, influence_weight=1):
    """
    Calculate overall territorial control scores for each faction
    Args:
        grid: Game grid
        territory: 2D array of dominant factions
        piece_control_weight: Points for controlling a cell with a piece
        influence_weight: Points for influencing an empty cell
    Returns: Dictionary of faction scores
    """
    faction_scores = {"A": 0, "B": 0}
    
    for x in range(grid.size):
        for y in range(grid.size):
            cell = grid.cells[x][y]
            if cell:
                # Direct piece control
                faction_scores[cell[0].faction] += piece_control_weight
            elif territory[x][y]:
                # Territorial influence
                faction_scores[territory[x][y]] += influence_weight
    
    return faction_scores


def get_territorial_statistics(grid, territory, influence):
    """
    Get detailed territorial statistics for analysis
    Returns: Dictionary with various metrics
    """
    stats = {
        'total_cells': grid.size * grid.size,
        'occupied_cells': 0,
        'controlled_cells': {'A': 0, 'B': 0},
        'influenced_cells': {'A': 0, 'B': 0},
        'neutral_cells': 0,
        'average_influence': {'A': 0.0, 'B': 0.0},
        'max_influence': {'A': 0.0, 'B': 0.0}
    }
    
    influence_sum = {'A': 0.0, 'B': 0.0}
    influence_count = {'A': 0, 'B': 0}
    
    for x in range(grid.size):
        for y in range(grid.size):
            cell = grid.cells[x][y]
            if cell:
                stats['occupied_cells'] += 1
                stats['controlled_cells'][cell[0].faction] += 1
            elif territory[x][y]:
                faction = territory[x][y]
                stats['influenced_cells'][faction] += 1
                influence_sum[faction] += influence[x][y]
                influence_count[faction] += 1
                stats['max_influence'][faction] = max(stats['max_influence'][faction], influence[x][y])
            else:
                stats['neutral_cells'] += 1
    
    # Calculate averages
    for faction in ['A', 'B']:
        if influence_count[faction] > 0:
            stats['average_influence'][faction] = influence_sum[faction] / influence_count[faction]
    
    return stats


def get_territorial_color(base_color, influence_value, max_influence=5.0):
    """
    Convert faction color to lighter version based on influence
    Args:
        base_color: Hex color string (e.g., "#4A90E2")
        influence_value: Numerical influence strength
        max_influence: Expected maximum influence for normalization
    Returns: Lighter hex color string
    """
    # Convert hex to RGB
    rgb = tuple(int(base_color[i:i+2], 16) for i in (1, 3, 5))
    
    # Normalize influence to 0-1 range
    normalized_influence = min(1.0, influence_value / max_influence)
    
    # Make it much lighter based on influence (10% to 25% of original color)
    lightness_factor = 0.1 + 0.15 * normalized_influence
    light_rgb = tuple(int(255 - (255 - c) * lightness_factor) for c in rgb)
    
    # Convert back to hex
    return f"#{light_rgb[0]:02x}{light_rgb[1]:02x}{light_rgb[2]:02x}"
