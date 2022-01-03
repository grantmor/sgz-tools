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
# ?) Prevent enemies spawning on critical tiles (optional switch) impl randomizer options dataclass
#   - Some tiles appear to be placed by the engine... need to make sure not to place tiles there    
# 1) Basic unmovable obstacles / mine lines / electric lines
# 2) Refactor to handle verification of level size
# 3) Add Mothership on appropritate tiles
# 4) Refactor event code into function, PAD OFFSET***

def coord_to_map_offset_only_terrain_no_split(col, row):
    #numTilesInFullMap = engine.MaxZones * engine.RowsPerZone * engine.TilesInRow
    #unusedtiles = numTilesInFullMap - tilesInMap
    offset = row * engine.TilesInRow * engine.RegionsInZone + col

    return offset #- unusedtiles


def pad_offset(offset, tilesInMap):
    numTilesInFullMap = engine.MaxZones * engine.RowsPerZone * engine.TilesInRow
    unusedtiles = numTilesInFullMap - tilesInMap

    return offset + unusedtiles

def stage_info(stageNum):
    return Stage(stageNum, 'us11')


def stage_config(stageNum, randomizerFlags, inaccessibleTiles, maxCoordY):

    # Refactor this to use stageInfo object later
    if stageNum in [1,2]:
        tilesInMap = 640
    elif stageNum == 3:
        tilesInMap = 960
    else:
        tilesInMap = 1280

    # These blocks should be a function
    while True:
        playerX = random.randint(0, 39) 
        playerY = random.randint(maxCoordY, 31)
        
        playerStepsX =  coord_to_steps(playerX)
        playerStepsY = coord_to_steps(playerY)

        playerOffset = coord_to_map_offset_only_terrain_no_split(playerX, playerY) 

        print(f'playerOffset:{playerOffset}')

        if not (playerOffset in inaccessibleTiles): break

    while True:
        enemyX = random.randint(0, 39) 
        enemyY = random.randint(maxCoordY, 31)

        enemyStepsX = coord_to_steps(enemyX)
        enemyStepsY = coord_to_steps(enemyY)

        if stageNum == 4:
            secondEnemyX = random.randint(0, 39) 
            secondEnemyY = random.randint(maxCoordY, 31)

            secondEnemyStepsX = coord_to_steps(secondEnemyX)
            secondEnemyStepsY = coord_to_steps(secondEnemyY)
        else:
            secondEnemyX = 0
            secondEnemyY = 0

            secondEnemyStepsX = 0
            secondEnemyStepsY = 0


        firstPosOffset = coord_to_map_offset_only_terrain_no_split(enemyX, enemyY)
        secondPosOffset = coord_to_map_offset_only_terrain_no_split(secondEnemyX, secondEnemyY)

        firstPosOk = not (firstPosOffset in inaccessibleTiles)
        secondPosOk = not (secondPosOffset in inaccessibleTiles)

        print(f'firstEnemyPosOffset: {firstPosOffset}')
        print(f'secondEnemyPosOffset: {secondPosOffset}')

        if stageNum != 4: secondPosOk = True
        if firstPosOk and secondPosOk: break
    
    while True:
        warpX = random.randint(0, 39)
        warpY = random.randint(maxCoordY, 31)

        warpStepsX = coord_to_steps(warpX)
        warpStepsY = coord_to_steps(warpY)

        warpToPosOffset = coord_to_map_offset_only_terrain_no_split(warpX, warpY)
        print(f'warpToPosOffset:{warpToPosOffset}')
        if not (warpToPosOffset in inaccessibleTiles) : break

# Finish coding second enemy parameters, modify stage_config to take randomizer params, set values here
    stageConfig = StageConfig (

        playerStepsX,
        playerStepsY,

        enemyStepsX,
        enemyStepsY,

        secondEnemyStepsX,
        secondEnemyStepsY,

        stageInfo.stageTime,

        stageInfo.playerMaxEnergy, stageInfo.playerMaxEnergy,
        stageInfo.enemyMaxEnergy, stageInfo.enemyMaxEnergy,

        warpStepsX,
        warpStepsY
    )

    return stageConfig


def coord_to_steps(coord):
    return coord * 8


def generate_events(eventType, quantity, criticalTiles, maxCoordY, tilesInMap):
    eventList = [] 
    tileIdxMap = {}

    whitelistedItems = [
        items.EnergyCapsule, 
        items.DefenseItem, 
        items.FightingSpirit, 
        items.EnergyRefill, 
        items.SuperRefill, 
        items.StopTime, 
        items.Invincibility
    ]

    trapIndex = 0
    resuppliesAdded = 0
    for event in range(0, quantity):
        if eventType == events.Trap:
            eventType = events.Trap
            eventPayload = trapIndex 
            trapIndex += 1
        elif eventType == events.EnergyResupply:
            eventType = events.EnergyResupply
            eventPayload = resuppliesAdded
            resuppliesAdded += 1
        elif eventType == events.Item:
            eventType = events.Item
            while True:
                eventPayload = random.randint(items.MinVal, items.MaxVal)
                if eventPayload in (whitelistedItems): break
        elif eventType == 'warp':
            eventType = events.Item
            eventPayload = items.Warp

        while True:
            xPos = random.randint(0, engine.TilesInRow * engine.RegionsInZone - 1)
            yPos = random.randint(maxCoordY, engine.RowsPerZone * engine.MaxZones // 2 - 1) # Level height in zones

            currentEvent = Event(eventType, eventPayload, xPos, yPos)
            newTileIdx = pad_offset(coord_to_map_offset_only_terrain_no_split(xPos, yPos), tilesInMap)

            if not (newTileIdx in criticalTiles): break

        tileIdxMap[newTileIdx] = True
        eventList.append(currentEvent)

    return tileIdxMap, eventList 
            # Add events to critical tiles list
            #eventTile = 
            #criticalTiles.append(eventTile)


def generate_stage(stageInfo, randomizerFlags, superBank, stagePalettes):

    if stageInfo.stageNumber < 3:
        numZonesInStage = 4
    elif stageInfo.stageNumber == 3:
        numZonesInStage = 6
    else:
        numZonesInStage = 8

    playableRows = stageInfo.playableZones // engine.RegionsInZone * engine.RowsPerZone
    maxRowsInStage = engine.MaxZones // 2 * engine.RowsPerZone
    maxCoordY = maxRowsInStage - playableRows

    if stageInfo.stageNumber == 1:
        mapParams = MapParameters(2, 8, 4, 2, 0, 12, 1)
    elif stageInfo.stageNumber == 2:
        mapParams = MapParameters(4, 6, 4, 2, 0, 12, 1)
    elif stageInfo.stageNumber == 3:
        mapParams = MapParameters(2, 10, 8, 3, 6, 16, 1)
    else: 
        mapParams = MapParameters(2, 12, 10, 4, 0, 16, 1)

    xTiles, yTiles = engine.TilesInRow * 2, stageInfo.playableZones // 2 * engine.RowsPerZone 

    eventList = []


    ##########
    # Events #
    ##########

    # TODO: Super Bank should be random 
    stageSixLabOffset = 555
    criticalTiles = {}

    if stageInfo.stageNumber in [5,6] and randomizerFlags.NoEnemySpawnCritical:
        energyBankOffset = pad_offset(stageSixLabOffset, stageInfo.tilesInMap)
        criticalTiles[energyBankOffset] = True

    # Items
    itemTiles, itemEvents = generate_events(events.Item, mapParams.numItems, criticalTiles, maxCoordY, stageInfo.tilesInMap)
    criticalTiles.update(itemTiles)
    # Resupplies
    resupplyTiles, resupplyEvents = generate_events(events.EnergyResupply, mapParams.numResupplies, criticalTiles, maxCoordY, stageInfo.tilesInMap)
    criticalTiles.update(resupplyTiles)
    # Traps
    trapTiles, trapEvents = generate_events(events.Trap, mapParams.numTraps, criticalTiles, maxCoordY, stageInfo.tilesInMap)
    criticalTiles.update(trapTiles)
    # Warp
    warpTiles, warpEvents = generate_events('warp', mapParams.numWarps, criticalTiles, maxCoordY, stageInfo.tilesInMap)
    criticalTiles.update(warpTiles)

    eventList = itemEvents + resupplyEvents + trapEvents + warpEvents


    #####################
    # Super Energy Bank #
    #####################


    if stageInfo.stageNumber in [5,6]:

        eventList.append(Event(events.Trap, 0x00, superBank.xPos, superBank.yPos))
        superBankOffset = coord_to_map_offset_only_terrain_no_split(superBank.xPos, superBank.yPos)
        criticalTiles[superBankOffset] = True

    # Log Events
    print()
    print(f'Stage {stageInfo.stageNumber}')
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
    stop3 = .05
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
    
    #print(f'randomMap:{randomMap}')
    ### TODO: - Place more "obstacles" (skyscraper, rocky mountain, electric fence)

    # Tiles that can't be moved through (player or boss shouldn't spawn here)
    inaccessibleTiles = []

    # Find inaccessible tiles
    for tileIdx, tile in enumerate(randomMap):
        
        if tile in [tiles.SkyScraper, tiles.RockyMountain]:
            #print(f'iaccessible: tile: {tile}')
            #print(f'iaccessible: tileIdx: {tileIdx}')
            #print()
            inaccessibleTiles.append(pad_offset(tileIdx, stageInfo.tilesInMap))

    #print(f'inaccesibleTiles:{inaccessibleTiles}')
    ####################################################################
    # Placing enemies - do this more efficiently later -
    # Generate list of required positions first, then assign positions

    
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
                #print(f'xPos, YPos: {xPos},{yPos}') 
                #print(f'Offset: {coord_to_map_offset_only_terrain_no_split(xPos, yPos, stageInfo.tilesInMap)}')
                #print(f'criticalTiles: {criticalTiles}')
                if not (coord_to_map_offset_only_terrain_no_split(xPos, yPos) in criticalTiles):
                    break

            enemyList.append(EnemyUnit(enemyType, xPos, yPos))
    
    # Log enemy offsets
    #for enemy in enemyList:
    #    print(coord_to_map_offset(enemy.col, enemy.row, False))

    print(f'Final inaccessibleTiles list:{inaccessibleTiles}')
    stageConfig = stage_config(stageInfo.stageNumber, randomizerFlags, inaccessibleTiles, maxCoordY)

    return eventList, randomMap, enemyList, stageConfig


# patches in super energy bank tile coordinates and returns super bank coords for generate_stage() for stage 5
def patch_super_bank(fileObj):
    #labCol = 0x23
    #labRow = 0x0d
    superBankX = random.randint(0, 39)
    superBankY = random.randint(0, 31)

    superBank = SuperBank(
        superBankX,
        superBankY
    )

    unknownConstant = 0x04

    xSuperBankBytes = superBankX << 3
    xSuperBankBytes += unknownConstant

    ySuperBankBytes = superBankY << 3
    ySuperBankBytes += unknownConstant


    # patch in super bank instructions
    xAdr = 0x0e0ed
    yAdr = 0x0e0f0

    ldx = 0xa2
    ldy = 0xa0

    bankXPosInstruction = bytes([ldx]) + int_to_16_le(xSuperBankBytes)
    bankYPosInstruction = bytes([ldy]) + int_to_16_le(ySuperBankBytes)

    fileObj.seek(xAdr)
    fileObj.write(bankXPosInstruction)

    fileObj.seek(yAdr)
    fileObj.write(bankYPosInstruction)

    return  superBank


######################
# *** Randomize! *** #
######################

# Randomizer Flags (arguments later)
randomizerFlags = RandomizerFlags(True, True, True, True, True, True, True)

# Patch Game
patch_features(
    sys.argv[1],
    randomizerFlags.PersistentTime,
    randomizerFlags.PersistentEnergy,
    randomizerFlags.NoMechaGodzillaWarp,
    randomizerFlags.NoStartingContinues,
    randomizerFlags.NoAddedContinues
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

# Handling Stage 6 Manually for now
# MUST BE DONE BEFORE PATCHING OTHER STAGES TO GET SUPER BANK POSITION
# Randomize Bagan's Location

rom = open(sys.argv[1], 'r+b')

enemyHorizontalPos = int_to_16_le(random.randint(0, 0xff))
enemyVerticalPos = int_to_16_le(random.randint(0, 0xff))

hInstructionAdr = 0xe067
vInstructionAdr = 0xe06d

patch_enemy_pos_instructions(rom, enemyHorizontalPos, enemyVerticalPos, hInstructionAdr, vInstructionAdr)
superBank = patch_super_bank(rom)

# NEED TO PASS SUPER BANK INTO GENERATE STAGE TO GET ADDED TO CRITICAL TILES LIST
rom.close()

# Patching remaining stages
numStages = 5
stageRange = range(1, numStages + 1)

for stage in stageRange:
    stageInfo = stage_info(stage)

    # Move this into stage eventually
    if stage == 2 or stage == 3:
        stdPalettes = ruralPalette
    else:
        stdPalettes = urbanPalette 

    eventList, randomMap, enemyList, stageConfig = generate_stage(stageInfo, randomizerFlags, superBank, stdPalettes)

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


