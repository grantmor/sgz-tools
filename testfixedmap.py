import sys

from constants import *
from stage import *

from perlin_noise import *
import matplotlib.pyplot as plot

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

    tiles.Building: palettes.Map,
    tiles.SkyScraper: palettes.Map,

    tiles.ResupplyBase: palettes.Blue,
    tiles.ItemPoint: palettes.Yellow,

    enemies.Tank: palettes.Enemy,
    enemies.Missle: palettes.Enemy,
    enemies.Mine: palettes.Enemy
}

# Generate Test Events
energyResupply = Event(events.EnergyResupply, items.EnergyResupply, 10, 27)
fightingSpirit = Event(events.Item, items.FightingSpirit, 11, 27) 
defenseItem = Event(events.Item, items.DefenseItem, 12, 27) 
superRefill = Event(events.Item, items.SuperRefill, 23, 27)
energyRefill = Event(events.Item, items.EnergyRefill, 24, 27) 
energyCapsule = Event(events.Item, items.EnergyCapsule, 25, 27)
invincibility = Event(events.Item, items.Invincibility, 26, 27)
warp = Event(events.Item, items.Warp, 27, 27)
stopTime = Event(events.Item, items.StopTime, 28, 27)
messageItem = Event(events.Item, items.Message, 29, 27)

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

# Generating Random Terrain Data
noise1 = PerlinNoise(seed=28976387430987, octaves=4)

xPixels, yPixels = 40, 16

bitmap = []

for x in range (yPixels):
    row = []
    for y in range(xPixels):
        noiseVal = noise1([x/xPixels, y/yPixels])
        row.append(noiseVal)
    bitmap.append(row)

#plot.imshow(bitmap, cmap='gray')
#plot.show()

for val in bitmap:
    print(val)

randomMap = bytearray()

tileIdx = 0

stop1 = -.23
stop2 = -.1
stop3 = .1
stop4 = .3

for y in range(0, yPixels):
    for x in range(0, xPixels):
        tileValue = bitmap[y][x]
        if tileValue <= stop1:
            randomMap.append(tiles.DeepSea)
        elif stop1 < tileValue <= stop2:
            randomMap.append(tiles.Sea)
        elif stop2 < tileValue <= stop3:
            randomMap.append(tiles.Ground)
        elif stop3 < tileValue <= stop4:
            randomMap.append(tiles.Building)
        else:
            randomMap.append(tiles.SkyScraper)

print(f'randomMap:{randomMap}')

# Generating Enemy List

numTanks = 4
numMissles = 4
numMines = 4

enemyList = [
    EnemyUnit(enemies.Tank, 35, 30),
    EnemyUnit(enemies.Missle, 36, 30),
    EnemyUnit(enemies.Mine, 37, 30),

    EnemyUnit(enemies.Tank, 20, 29),
    EnemyUnit(enemies.Missle, 22, 29),
    EnemyUnit(enemies.Mine, 24, 29)
]


# Setting Stage Parameters
stageOneConfig = StageConfig(
    0x0000, 0xee,
    0x0000, 0xee,

    999,

    700, 700,
    700, 700
)

stageOneData = pack_test_map(
    stage1, 
    testEvents, 
    randomMap,
    enemyList, 
    stdPalettes, 
    True
)


patch_stage(sys.argv[1], stage1, stageOneConfig, stageOneData)