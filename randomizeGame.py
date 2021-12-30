import sys
import random

from perlin_noise import *
import matplotlib.pyplot as plot

from constants import *
from stage import *

from game import *
from stageMap import *


# TODO: Finish movement randomization for all bosses (currently only MG)
# TODO: Refactor - Split Map and Stage functionality
# TODO: Power lines

# TODO: Figure out a way to initialize time, energy
# TODO: Make energy, time, inventory persistent
# TODO: Seek and destroy continues

# TODO: Voronoi for rural areas, grid pattern for cities
# TODO: Third pass for "impassables"
# TODO: Sprinkle in stuff in "Empty Zones"?

# TODO: MVP
# 1) Prevent enemies spawning on critical tiles (optional switch) impl randomizer options dataclass
#   - Some tiles appear to be placed by the engine... need to make sure not to place tiles there    
# 2) Finish Persistent health/time 
# 3) Randomize Player / Enemy location for all maps
# DONE?) Prevent spawning on umovable tiles 
# 5) Basic unmovable obstacles / mine lines / electric lines
# 6) Patch warp to be random (every time or per stage)
# 7) Refactor to handle verification of level size
# 8) Randomize Super Lab?


def stage_info(stageNum):
    return Stage(stageNum, 'us11')


def stage_config(stageNum, inaccessibleTiles, maxCoordY):

    while True:
        playerX = random.randint(0, coord_to_steps(39)) 
        playerY = random.randint(coord_to_steps(maxCoordY), coord_to_steps(31))

        if coord_to_map_offset(playerX, playerY, False) not in inaccessibleTiles: break

    while True:
        enemyX = random.randint(0, coord_to_steps(39)) 
        enemyY = random.randint(coord_to_steps(maxCoordY), coord_to_steps(31))

        if coord_to_map_offset(enemyX, enemyY, False) not in inaccessibleTiles: break

    stageConfig = StageConfig(

        playerX,
        playerY,

        enemyX,
        enemyY,

        999,

        600, 600,
        600, 600,
    )

    return stageConfig


def coord_to_steps(coord):
    return coord * 8


def generate_stage(stageInfo, randomizerFlags, stagePalettes):

    if stageInfo.stageNumber < 3:
        numZonesInStage = 4
    elif stageInfo.stageNumber == 3:
        numZonesInStage = 6
    else:
        numZonesInStage = 8

    playableRows = stageInfo.playableZones // engine.RegionsInZone * engine.RowsPerZone
    maxRowsInStage = engine.MaxZones // 2 * engine.RowsPerZone
    maxCoordY = maxRowsInStage - playableRows

    # Tiles that shouldn't be overwritten by enemies
    stageSixLabOffset = 555
    criticalTiles = []

    # NEED TO CHECK THERE BEFORE WRITING EVENTS TOO
    if stageInfo.stageNumber in [5,6] and randomizerFlags.NoEnemySpawnCritical:
        criticalTiles.append(stageSixLabOffset) # Super Energy Lab for Stage 6


    if stageInfo.stageNumber in [1,2]:
        mapParams = MapParameters(2, 6, 4, 2, 0, 12)
    elif stageInfo.stageNumber == 3:
        mapParams = MapParameters(2, 10, 8, 3, 6, 16)
    else: 
        mapParams = MapParameters(2, 12, 10, 4, 0, 16)

    xTiles, yTiles = engine.TilesInRow * 2, stageInfo.playableZones // 2 * engine.RowsPerZone 

    eventList = []

    
    if mapParams.numTraps > 0:
        trapIndex = 0
        for event in range(0, mapParams.numTraps + 1):

            eventType = events.Trap
            eventPayload = trapIndex 
            trapIndex += 1

            xPos = random.randint(0, engine.TilesInRow * engine.RegionsInZone - 1)
            yPos = random.randint(maxCoordY, engine.RowsPerZone * engine.MaxZones // 2 - 1) # Level height in zones

            trapEvent = Event(eventType, eventPayload, xPos, yPos)
            eventList.append(trapEvent)

            # Add events to critical tiles list
            criticalTiles.append(coord_to_map_offset(xPos, yPos, False))

    if mapParams.numItems > 0:
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
            yPos = random.randint(maxCoordY, engine.RowsPerZone * engine.MaxZones // 2 - 1) # Level height in zones

            itemPoint = Event(eventType, eventPayload, xPos, yPos)
            eventList.append(itemPoint)

            # Add events to critical tiles list
            criticalTiles.append(coord_to_map_offset(xPos, yPos, False))

    if mapParams.numResupplies > 0:

        resuppliesAddded = 0
        for event in range(0, mapParams.numResupplies + 1):

            eventType = events.EnergyResupply
            eventPayload = resuppliesAddded
            resuppliesAddded += 1

            xPos = random.randint(0, engine.TilesInRow * engine.RegionsInZone - 1)
            yPos = random.randint(maxCoordY, engine.RowsPerZone * engine.MaxZones // 2 - 1) # Level height in zones

            resupplyPoint = Event(eventType, eventPayload, xPos, yPos)
            eventList.append(resupplyPoint)

            # Add events to critical tiles list
            criticalTiles.append(coord_to_map_offset(xPos, yPos, False))

    #print(criticalTiles)

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

    #stop1 = -.23
    #stop2 = -.1
    #stop3 = .1
    #stop4 = .3

    stop1 = -.23
    stop2 = -.1
    stop3 = .08
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
            elif stop3 < tileValue <= stop4:
                if stageInfo.stageNumber in [2,3]:
                    randomMap.append(tiles.Mountain)
                else:
                    randomMap.append(tiles.Building)

            else:
                if stageInfo.stageNumber == 2 or stageInfo.stageNumber == 3:
                    randomMap.append(tiles.RockyMountain)
                else:
                    randomMap.append(tiles.SkyScraper)
    ### TODO: - Place more "obstacles" (skyscraper, rocky mountain, electric fence)

    # Tiles that can't be moved through (player or boss shouldn't spawn here)
    inaccessibleTiles = []

    # Find inaccessible tiles
    for tileIdx, tile in enumerate(randomMap):
        if tile in [tiles.SkyScraper, tiles.RockyMountain]:
            inaccessibleTiles.append(tileIdx)

    #print(f'inaccesibleTiles:{inaccessibleTiles}')
    ####################################################################
    # Placing enemies - do this more efficiently later -
    # Generate list of required positions first, then assign positions
    # Change critical tile list to a map?
    
    enemyTypes = [
        enemies.Tank,
        enemies.Missle,
        enemies.Mine
    ]

    enemyList = []

    for enemyType in enemyTypes:
        for enemy in range(0, mapParams.numEnemies // len(enemyTypes)):
            while True:
                xPos = random.randint(0, engine.TilesInRow * 2)
                yPos = random.randint(maxCoordY, 31)

                if not randomizerFlags.NoEnemySpawnEvent: break
                
                if coord_to_map_offset(xPos, yPos, False) not in criticalTiles:
                    break

            enemyList.append(EnemyUnit(enemyType, xPos, yPos))
    
    # Log enemy offsets
    #for enemy in enemyList:
    #    print(coord_to_map_offset(enemy.col, enemy.row, False))

    stageConfig = stage_config(stageInfo.stageNumber, inaccessibleTiles, maxCoordY)

    return eventList, randomMap, enemyList, stageConfig



######################
# *** Randomize! *** #
######################

# Randomizer Flags (arguments later)
randomizerFlags = RandomizerFlags(False, False, True, True, True)

# Patch Game
patch_features(
    sys.argv[1],
    randomizerFlags.PersistentTime,
    randomizerFlags.PersistentEnergy,
    randomizerFlags.NoMechaGodzillaWarp
)

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

    tiles.SpecialEnergy: palettes.Blue,

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

    tiles.SpecialEnergy: palettes.Blue,

    tiles.Mothership: palettes.UFO,

    enemies.Tank: palettes.Enemy,
    enemies.Missle: palettes.Enemy,
    enemies.Mine: palettes.Enemy
}

numStages = 5
stageRange = range(1, numStages + 1)

for stage in stageRange:
    stageInfo = stage_info(stage)

    # Move this into stage eventually
    if stage == 2 or stage == 3:
        stdPalettes = ruralPalette
    else:
        stdPalettes = urbanPalette 

    eventList, randomMap, enemyList, stageConfig = generate_stage(stageInfo, randomizerFlags, stdPalettes)

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

# Handling Stage 6 Manually for now

# Randomize Bagan's Location

rom = open(sys.argv[1], 'r+b')

enemyHorizontalPos = int_to_16_le(random.randint(0, 0xff))
enemyVerticalPos = int_to_16_le(random.randint(0, 0xff))

hInstructionAdr = 0xe067
vInstructionAdr = 0xe06d

patch_enemy_pos_instructions(rom, enemyHorizontalPos, enemyVerticalPos, hInstructionAdr, vInstructionAdr)

rom.close()


