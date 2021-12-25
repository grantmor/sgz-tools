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

# Standard Palettes
stdPalettes = {
    tiles.Ground: palettes.Map,
    tiles.Sea: palettes.Blue,
    tiles.DeepSea: palettes.Blue,

    tiles.ResupplyBase: palettes.Blue,
    tiles.ItemPoint: palettes.Yellow,

    enemies.Tank: palettes.Enemy,
    enemies.Missle: palettes.Enemy,
    enemies.Mine: palettes.Enemy

}
# Generate Test Events
energyResupply = Event(events.EnergyResupply, items.EnergyResupply, 4, 27)
fightingSpirit = Event(events.Item, items.FightingSpirit, 5, 27) 
defenseItem = Event(events.Item, items.DefenseItem, 6, 27) 
superRefill = Event(events.Item, items.SuperRefill, 7, 27)
energyRefill = Event(events.Item, items.EnergyRefill, 8, 27) 
energyCapsule = Event(events.Item, items.EnergyCapsule, 9, 27)
invincibility = Event(events.Item, items.Invincibility, 10, 27)
warp = Event(events.Item, items.Warp, 11, 27)
stopTime = Event(events.Item, items.StopTime, 12, 27)
messageItem = Event(events.Item, items.Message, 13, 27)

testEvents = [
    energyResupply,
    fightingSpirit,
    defenseItem,
    superRefill,
    energyRefill,
    energyCapsule,
    invincibility,
    warp,
    stopTime,
    messageItem
]


# Generating Terrain Data
palettesPresent = False # ********* TEST FALSE ***********

numMapTiles = engine.MaxZones * engine.RowsPerZone * engine.TilesInRow
tileStride = engine.TilePalettePairLength if palettesPresent else 1
mapDataSize = numMapTiles * tileStride

mapData = bytearray()

# Just filling the screen for now, will actually use argument later
tileIdx = 0
while tileIdx < numMapTiles: #numCells (tiles)
    mapData.append(tiles.Ground)
    mapData.append(stdPalettes[tiles.Ground])
    tileIdx += 1

# Adding test event tiles
#mapData[coord_to_map_offset(4, 27, True)] = tiles.ResupplyBase
#mapData[coord_to_map_offset(5, 27, True)] = tiles.ItemPoint

# Generating Enemy List
enemyList = [
    EnemyUnit(enemies.Tank, 5, 30),
    EnemyUnit(enemies.Missle, 6, 30),
    EnemyUnit(enemies.Mine, 7, 30),

    EnemyUnit(enemies.Tank, 4, 29),
    EnemyUnit(enemies.Missle, 8, 29),
    EnemyUnit(enemies.Mine, 12, 29)
]

stageOneData = pack_test_map(
    stage1, 
    testEvents, 
    mapData, 
    enemyList, 
    stdPalettes, 
    True
)

def patch_stage(stageInfo, stageData):
    rom = open(sys.argv[1], 'r+b')

    # Write Stage 1 Terrain Region Pointers
    rom.seek(stageInfo.mapPtrOffsetA)
    rom.write(stageData.mapPtrA)
    
    rom.seek(stageInfo.mapPtrOffsetB)
    rom.write(stageData.mapPtrB)

    # Write Stage 1 Map Data
    rom.seek(stageInfo.terrainOffset)
    rom.write(stageData.mapData)

    # Write Stage 1 Enemy Region Pointers
    rom.seek(stageInfo.enemyPtrOffsetA)
    rom.write(stageData.enemyPtrA)

    rom.seek(stageInfo.enemyPtrOffsetB)
    rom.write(stageData.enemyPtrB)

    # Write Stage 1 Enemy Data
    rom.seek(stageInfo.enemyOffset)
    rom.write(stageData.enemyData)

    # Write Stage 1 Event Data
    rom.seek(stageInfo.eventOffset)
    rom.write(stageData.eventData)

    rom.close()

patch_stage(stage1, stageOneData)