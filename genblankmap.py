import sys

from constants import *
from stage import *

    
# Instantiate "enums"
tiles = Tiles()
enemies = Enemies()
events = Events()
items = Items()
palettes = Palettes()
engine = Engine()
        
# US v1.1 Values
stage1 = Stage(1, 'us11')
stage2 = Stage(2, 'us11')
stage3 = Stage(3, 'us11')
stage4 = Stage(4, 'us11')
stage5 = Stage(5, 'us11')


fullRowHeader = b'\x01\x00\x00'

emptyRowSize = engine.RowHeaderLength + engine.TilePalettePairLength

mapSize = engine.MaxZones * engine.RowsPerZone * emptyRowSize

rowIdx = rowsPerZone
row = fullRowHeader + tiles.Ground + palettes.Map

emptyMap = bytes()
for zone in range(0, engine.CellsInRow):
    while rowIdx >= 1:
        emptyMap += row
        rowIdx -= 1
    rowIdx = engine.cellsInRow


rom = open(sys.argv[1], 'r+b')

#rom.seek(stage1.eventOffset)
#rom.write()

rom.seek(stage1.terrainOffset)
rom.write(emptyMap)

rom.seek(stage2.terrainOffset)
rom.write(emptyMap)

rom.seek(stage3.terrainOffset)
rom.write(emptyMap)

rom.seek(stage4.terrainOffset)
rom.write(emptyMap)

rom.seek(stage5.terrainOffset)
rom.write(emptyMap)

rom.close()

#with open('zone1', 'wb') as file:
#    file.write(stageOneMap)

