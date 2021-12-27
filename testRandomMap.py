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

    #print(stageInfo)
    # Half horizontal resolution


    # Handle zones to generate ...
    print(f'*** TERRAIN GEN ***')
    print(f'pzs: {stageInfo.playableZones}')
    xTiles, yTiles = engine.TilesInRow * 2, stageInfo.playableZones // 2 * engine.RowsPerZone 

    eventList = []

    numEvents = 12  

    for event in range(0, numEvents):

        eventType = random.randint(events.MinVal, events.MaxVal)
        #while eventType == events.Message or eventType == events.Trap:
        #    eventType = random.randint(events.MinVal, events.MaxVal)
        
        
        if eventType == events.EnergyResupply:
            eventPayload = items.EnergyResupply
        else:
            eventPayload = random.randint(items.MinVal, items.MaxVal)

        # Hack for now...
        if stageInfo.stageNumber == 3:
            eventType = events.Trap

        xPos = random.randint(0, engine.TilesInRow * engine.RegionsInZone - 1)
        #xPos = random.randint(0, (engine.TilesInRow * engine.RegionsInZone // 2) - 1)
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
    noise1 = PerlinNoise(seed=random.randint(0, 0xffffffffffffffff), octaves=4)


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

            # Deep Sea
            if tileValue <= stop1:
                randomMap.append(tiles.DeepSea)
            # Sea
            elif stop1 < tileValue <= stop2:
                randomMap.append(tiles.Sea)
            
            # Ground
            elif stop2 < tileValue <= stop3:
                randomMap.append(tiles.Ground)

            # Building / Mountain
            elif stop3 < tileValue:
                if stageInfo.stageNumber == 2 or stageInfo.stageNumber == 3:
                    randomMap.append(tiles.Mountain)
                else:
                    randomMap.append(tiles.Building)

            #else:
                #if stageInfo.stageNumber == 2 or stageInfo.stageNumber == 3:
                #    randomMap.append(tiles.RockyMountain)
                #else:
                #    randomMap.append(tiles.SkyScraper)
    
    print(f'len gen map: {len(randomMap)}')

    numTanks = 2
    numMissles = 2
    numMines = 2

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
patch_features(sys.argv[1], False, False, True)

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