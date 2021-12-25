from constants import *
from math import floor


def coord_to_map_offset(col, row, palettePresent):
    tileStride = engine.TilePalettePairLength if palettePresent else 1
    tilesInMap = engine.MaxZones * engine.RowsPerZone * engine.TilesInRow
    regionModifier = int(tilesInMap / 2 - engine.TilesInRow) if col >= engine.TilesInRow else 0
    offset = (row * engine.TilesInRow  + col + regionModifier) * tileStride
    return offset 

print(coord_to_map_offset(20, 0, True))
print(coord_to_map_offset(22, 30, True))
print(coord_to_map_offset(32, 30, True))