import sys
import random

from perlin_noise import *
import matplotlib.pyplot as plot

from constants import *
from stage import *

from game import *
from stageMap import *


# TODO: Finish movement randomization for all bosses (currently only MG)
# TODO: Skip hunting for Professor Ogata?
# TODO: "Safety Checks" (No spawning trapped, etc.)
# TODO: Energy Resupply Bug
# TODO: Refactor - Split Map and Stage functionality
# TODO: Power lines

# TODO: Figure out a way to initialize time, energy
# TODO: Make energy, time, inventory persistent
# TODO: Seek and destroy continues

# TODO: Separate water and ground/building noise into passes
# TODO: Add one large body of water per level 
# TODO: Voronoi for rural areas, grid pattern for cities
# TODO: Third pass for "impassables"
# TODO: Sprinkle in stuff in "Empty Zones"?


def coord_to_steps(coord):
    return coord * 8


def generate_stage(stageInfo, stageConfig, stagePalettes):
    # Generate Test Events TODO: Only use traps if the reward is worth the risk... for example FULL heal

    if stageInfo.stageNumber in [1,2]:
        mapParams = MapParameters(2, 6, 5, 2, 0, 12)
    elif stageInfo.stageNumber == 3:
        mapParams = MapParameters(2, 8, 8, 4, 6, 24)
    else: 
        mapParams = MapParameters(2, 8, 12, 4, 0, 24)

    print(mapParams.horizontalStretchFactor)

    xTiles, yTiles = engine.TilesInRow * 2, stageInfo.playableZones // 2 * engine.RowsPerZone 


    # This is a dumb way to do this, will fix later
    # Should instead do a pass for each type (items, immediate items, resupply bases, traps, SE)
    eventList = []

    for event in range(0, mapParams.numItems + 1):

        eventType = events.Item
        eventPayload = random.randint(items.MinVal, items.MaxVal)

        whitelistedItems = [
            items.EnergyCapsule, 
            items.DefenseItem, 
            items.FightingSpirit, 
            items.EnergyRefill, 
            items.SuperRefill, 
            items.Warp, 
            items.StopTime, 
            items.Invincibility
        ]

        xPos = random.randint(0, engine.TilesInRow * engine.RegionsInZone - 1)
        yPos = random.randint(stageConfig.maxCoordY, engine.RowsPerZone * engine.MaxZones // 2 - 1) # Level height in zones

        newEvent = Event(eventType, eventPayload, xPos, yPos)
        eventList.append(newEvent)

    for event in range(0, mapParams.numResupplies + 1):

        eventType = events.EnergyResupply
        eventPayload = items.EnergyResupply

        xPos = random.randint(0, engine.TilesInRow * engine.RegionsInZone - 1)
        yPos = random.randint(stageConfig.maxCoordY, engine.RowsPerZone * engine.MaxZones // 2 - 1) # Level height in zones

        newEvent = Event(eventType, eventPayload, xPos, yPos)
        eventList.append(newEvent)

    for event in range(0, mapParams.numTraps + 1):

        eventType = events.Trap
        # The professor is only at one location
        if event == 0:
            eventPayload = items.ProfessorRescue
        else:
            eventPayload = 0x01

        xPos = random.randint(0, engine.TilesInRow * engine.RegionsInZone - 1)
        yPos = random.randint(stageConfig.maxCoordY, engine.RowsPerZone * engine.MaxZones // 2 - 1) # Level height in zones

        newEvent = Event(eventType, eventPayload, xPos, yPos)
        eventList.append(newEvent)

    # Log Events
    #print()
    #print(f'Stage {stageInfo.stageNumber}')
    #for event in eventList:
    #    print()
    #    print(f'event.type:{event.type}')
    #    print(f'event.payload:{event.payload}')
    #    print(f'event.col:{event.col}')
    #    print(f'event.row:{event.row}')

    # Generating Random Terrain Data

    noise1 = PerlinNoise(seed=random.randint(0, 0xffffffffffffffff), octaves=mapParams.noiseFrequency)

    bitmap = []

    for x in range (yTiles):
        row = []
        for y in range(xTiles):
            noiseVal = noise1([x/xTiles, y/yTiles])

            # Longer lines of the same tile on horizontal lines compresses better
            for stretch in range(0, mapParams.horizontalStretchFactor):
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

            # Deep Sea
            if tileValue <= stop1:
                randomMap.append(tiles.DeepSea)
            # Sea
            elif stop1 < tileValue <= stop2:
                randomMap.append(tiles.Sea)
            
            # Ground
            elif stop2 < tileValue <= stop3:
                if stageInfo.stageNumber in [2, 3]:
                    randomMap.append(tiles.RuralGround)
                else:
                    randomMap.append(tiles.UrbanGround)

            # Building / Mountain
            elif stop3 < tileValue:
                if stageInfo.stageNumber in [2,3]:
                    randomMap.append(tiles.Mountain)
                else:
                    randomMap.append(tiles.Building)

            #else:
                #if stageInfo.stageNumber == 2 or stageInfo.stageNumber == 3:
                #    randomMap.append(tiles.RockyMountain)
                #else:
                #    randomMap.append(tiles.SkyScraper)
    
    print(f'len gen map: {len(randomMap)}')

    numTanks = mapParams.numEnemies // 3
    numMissles = mapParams.numEnemies // 3
    numMines = mapParams.numEnemies // 3

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

    print(f'STAGENUM: {stageNum}, numZonesInStage: {numZonesInStage}')

    playableRows = stageInfo.playableZones // engine.RegionsInZone * engine.RowsPerZone
    maxRowsInStage = engine.MaxZones // 2 * engine.RowsPerZone
    maxCoordY = maxRowsInStage - playableRows

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

    tiles.UrbanGround: palettes.Map,
    tiles.SpecialGround: palettes.Map,

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

    tiles.RuralGround: palettes.Green,
    tiles.SpecialGround: palettes.Green,

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

numStages = 5
stageRange = range(1, numStages + 1)

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