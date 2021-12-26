import sys
import random

from perlin_noise import *
import matplotlib.pyplot as plot

from constants import *
from stage import *

from game import *

# TODO: Accomodate stages 3-6
# TODO: Skip hunting for Professor Ogata?
# TODO: "Safety Checks" (No spawning trapped, etc.)
# TODO: Energy Resupply Bug
# TODO: Refactor - Split Map and Stage functionality
# TODO: Different ground types result in different battle scene...

# TODO: Figure out a way to initialize time, energy
# TODO: Make energy, time, inventory persistent
# TODO: Seek and destroy continues

# TODO: Fill in water around deep water
# TODO: Delete "Lonely Cells" (Will help with compression)
# TODO: Sprinkle in stuff in "Empty Zones"?
# TODO: Explore layering two perlin textures, normalizing then using similar stopvalues?

def coord_to_steps(coord):
    return coord * 8


def generate_stage(stageInfo, stageConfig, stagePalettes):
    # Generate Test Events TODO: Only use traps if the reward is worth the risk... for example FULL heal

    print(stageInfo)
    eventList = []

    numEvents = 10

    for event in range(0, numEvents):

        eventType = random.randint(events.MinVal, events.MaxVal)
        while eventType == events.Message or eventType == events.Trap:
            eventType = random.randint(events.MinVal, events.MaxVal)
        
        if eventType == events.EnergyResupply:
            eventPayload = items.EnergyResupply
        else:
            eventPayload = random.randint(items.MinVal, items.MaxVal)

        xPos = random.randint(0, engine.TilesInRow * engine.RegionsInZone)
        yPos = random.randint(stageConfig.maxCoordY, engine.RowsPerZone * stageInfo.playableZones)

        newEvent = Event(eventType, eventPayload, xPos, yPos)
        eventList.append(newEvent)
    


    # Generating Random Terrain Data
    noise1 = PerlinNoise(seed=random.randint(0, 0xffffffffffffffff), octaves=6)

    # Half horizontal resolution
    xTiles, yTiles = engine.TilesInRow * 2, 16

    bitmap = []

    for x in range (yTiles):
        row = []
        for y in range(xTiles):
            noiseVal = noise1([x/xTiles, y/yTiles])
            row.append(noiseVal)
            # double up x noise
            row.append(noiseVal)
        bitmap.append(row)

    #plot.imshow(bitmap, cmap='gray')
    #plot.show()

    randomMap = bytearray()

    tileIdx = 0

    stop1 = -.23
    stop2 = -.1
    stop3 = .1
    stop4 = .3

    for y in range(0, yTiles):
        for x in range(0, xTiles):
            tileValue = bitmap[y][x]
            if tileValue <= stop1:
                randomMap.append(tiles.DeepSea)

            elif stop1 < tileValue <= stop2:
                randomMap.append(tiles.Sea)
            elif stop2 < tileValue <= stop3:
                randomMap.append(tiles.Ground)

            elif stop3 < tileValue <= stop4:
                if stageInfo.stageNumber == 2 or stageInfo.stageNumber == 3:
                    randomMap.append(tiles.Mountain)
                else:
                    randomMap.append(tiles.Building)

            else:
                if stageInfo.stageNumber == 2 or stageInfo.stageNumber == 3:
                    randomMap.append(tiles.RockyMountain)
                else:
                    randomMap.append(tiles.SkyScraper)

    numTanks = 4
    numMissles = 4
    numMines = 4

    enemyList = []

    for tank in range(0, numTanks):
        xPos = random.randint(0, engine.TilesInRow * 2)
        yPos = random.randint(stageConfig.maxCoordY, 31)
        enemyList.append(EnemyUnit(enemies.Tank, xPos, yPos))

    for missle in range(0, numMissles):
        xPos = random.randint(0, engine.TilesInRow * 2)
        yPos = random.randint(stageConfig.maxCoordY, 31)
        enemyList.append(EnemyUnit(enemies.Missle, xPos, yPos))

    for mine in range(0, numTanks):
        xPos = random.randint(0, engine.TilesInRow * 2)
        yPos = random.randint(stageConfig.maxCoordY, 31)
        enemyList.append(EnemyUnit(enemies.Mine, xPos, yPos))

    return eventList, randomMap, enemyList


def stage_info(stageNum):
    return Stage(stageNum, 'us11')


def stage_config(stageNum):

    if stageNum < 3:
        numZonesInStage = 4
    elif stageNum == 3:
        numZonesInStage = 6
    else:
        numZonesInStage = 8

    maxCoordY = int(numZonesInStage / 2 * engine.RowsPerZone)   
    yCoordRange = range(0, maxCoordY)

    stageConfig = StageConfig(

        random.randint(0, coord_to_steps(39)), 
        random.randint(coord_to_steps(maxCoordY), coord_to_steps(31)),

        random.randint(0, coord_to_steps(39)), 
        random.randint(coord_to_steps(maxCoordY), coord_to_steps(31)),

        999,

        700, 700,
        700, 700,

        maxCoordY
    )

    return stageConfig

# Patch Game
patch_features(sys.argv[1], True, True, True)

# Standard Palettes
urbanPalette = {
    tiles.Ground: palettes.Map,
    tiles.Sea: palettes.Blue,
    tiles.DeepSea: palettes.Blue,

    tiles.Building: palettes.Map,
    tiles.SkyScraper: palettes.Map,

    tiles.ResupplyBase: palettes.Blue,
    tiles.ItemPoint: palettes.Yellow,
    tiles.AreaPoint: palettes.Orange,

    tiles.Mothership : palettes.UFO,

    enemies.Tank: palettes.Enemy,
    enemies.Missle: palettes.Enemy,
    enemies.Mine: palettes.Enemy
}

ruralPalette = {
    tiles.Ground: palettes.Green,
    tiles.Sea: palettes.Blue,
    tiles.DeepSea: palettes.Blue,

    tiles.Mountain: palettes.Green,
    tiles.RockyMountain: palettes.Green,

    tiles.ResupplyBase: palettes.Blue,
    tiles.ItemPoint: palettes.Yellow,
    tiles.AreaPoint: palettes.Orange,

    tiles.Mothership: palettes.UFO,

    enemies.Tank: palettes.Enemy,
    enemies.Missle: palettes.Enemy,
    enemies.Mine: palettes.Enemy
}

currentMaxStage = 2
stageRange = range(1, currentMaxStage + 1)

for stage in stageRange:
    stageInfo = stage_info(stage)
    stageConfig = stage_config(stage)

    # Move this into stage eventually
    if stage == 2 or stage == 3:
        stdPalettes = ruralPalette
    else:
        stdPalettes = urbanPalette 

    eventList, randomMap, enemyList = generate_stage(stageInfo, stageConfig, stdPalettes)

    #print_uncompressed_map_data(randomMap)

    stageData = pack_test_map(
        stageInfo, 
        eventList, 
        randomMap,
        enemyList, 
        stdPalettes, 
        True
    )

    patch_stage(sys.argv[1], stageInfo, stageConfig, stageData)