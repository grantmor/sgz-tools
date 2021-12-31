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
# DONE) Prevent enemies spawning on critical tiles (optional switch) impl randomizer options dataclass
#   - Some tiles appear to be placed by the engine... need to make sure not to place tiles there    
# 2) Finish Persistent health/time 
# DONE) Randomize Player / Enemy location for all maps
# DONE) Prevent spawning on umovable tiles 
# 5) Basic unmovable obstacles / mine lines / electric lines
# 6) Patch warp to be random (every time or per stage)
# 7) Refactor to handle verification of level size
# 8) Randomize Super Lab?
# 9) Random MUFO?

def coord_to_map_offset_only_terrain_no_split(col, row, tilesInMap):
    offset = row * engine.TilesInRow * engine.RegionsInZone + col

    return offset

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

    while True:
        playerX = random.randint(0, 39) 
        playerY = random.randint(maxCoordY, 31)
        
        playerStepsX =  coord_to_steps(playerX)
        playerStepsY = coord_to_steps(playerY)

        playerOffset = coord_to_map_offset_only_terrain_no_split(playerX, playerY, tilesInMap) 

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


        firstPosOffset = coord_to_map_offset_only_terrain_no_split(enemyX, enemyY, tilesInMap)
        secondPosOffset = coord_to_map_offset_only_terrain_no_split(secondEnemyX, secondEnemyY, tilesInMap)

        firstPosOk = not (firstPosOffset in inaccessibleTiles)
        secondPosOk = not (secondPosOffset in inaccessibleTiles)

        #print(f'firstEnemyPosOffset: {firstPosOffset}')
        #print(f'secondEnemyPosOffset: {secondPosOffset}')

        if stageNum != 4: secondPosOk = True
        if firstPosOk and secondPosOk: break
    
    while True:
        warpX = random.randint(0, 39)
        warpY = random.randint(maxCoordY, 31)

        warpStepsX = coord_to_steps(warpX)
        warpStepsY = coord_to_steps(warpY)

        warpToPosOffset = coord_to_map_offset_only_terrain_no_split(warpX, warpY, tilesInMap)

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

    # Tiles that shouldn't be overwritten by enemies
    stageSixLabOffset = 555
    criticalTiles = []

    # NEED TO CHECK THERE BEFORE WRITING EVENTS TOO
    if stageInfo.stageNumber in [5,6] and randomizerFlags.NoEnemySpawnCritical:
        criticalTiles.append(stageSixLabOffset) # Super Energy Lab for Stage 6


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

    # Can turn these loops into a general "Add event" function
    # Traps    
    if mapParams.numTraps > 0:
        trapIndex = 0
        for event in range(0, mapParams.numTraps):

            eventType = events.Trap
            eventPayload = trapIndex 
            trapIndex += 1

            xPos = random.randint(0, engine.TilesInRow * engine.RegionsInZone - 1)
            yPos = random.randint(maxCoordY, engine.RowsPerZone * engine.MaxZones // 2 - 1) # Level height in zones

            trapEvent = Event(eventType, eventPayload, xPos, yPos)
            eventList.append(trapEvent)

            # Add events to critical tiles list
            criticalTiles.append(coord_to_map_offset_only_terrain_no_split(xPos, yPos, stageInfo.tilesInMap))

    # Item Points
    if mapParams.numItems > 0:
        for event in range(0, mapParams.numItems):

            eventType = events.Item
            eventPayload = random.randint(items.MinVal, items.MaxVal)

            whitelistedItems = [
                items.EnergyCapsule, 
                items.DefenseItem, 
                items.FightingSpirit, 
                items.EnergyRefill, 
                items.SuperRefill, 
                items.StopTime, 
                items.Invincibility
            ]

            xPos = random.randint(0, engine.TilesInRow * engine.RegionsInZone - 1)
            yPos = random.randint(maxCoordY, engine.RowsPerZone * engine.MaxZones // 2 - 1) # Level height in zones

            itemPoint = Event(eventType, eventPayload, xPos, yPos)
            eventList.append(itemPoint)

            # Add events to critical tiles list
            criticalTiles.append(coord_to_map_offset_only_terrain_no_split(xPos, yPos, False))

    # Resupply Bases
    if mapParams.numResupplies > 0:
        resuppliesAdded = 0
        for event in range(0, mapParams.numResupplies):

            eventType = events.EnergyResupply
            eventPayload = resuppliesAdded
            resuppliesAdded += 1

            xPos = random.randint(0, engine.TilesInRow * engine.RegionsInZone - 1)
            yPos = random.randint(maxCoordY, engine.RowsPerZone * engine.MaxZones // 2 - 1) # Level height in zones

            resupplyPoint = Event(eventType, eventPayload, xPos, yPos)
            eventList.append(resupplyPoint)

            # Add events to critical tiles list
            criticalTiles.append(coord_to_map_offset_only_terrain_no_split(xPos, yPos, stageInfo.tilesInMap))

    # Warps
    if mapParams.numWarps > 0:
        warpsAdded = 0
        for event in range(0, mapParams.numWarps):

            eventType = events.Item
            eventPayload = items.Warp
            warpsAdded += 1

            xPos = random.randint(0, engine.TilesInRow * engine.RegionsInZone - 1)
            yPos = random.randint(maxCoordY, engine.RowsPerZone * engine.MaxZones // 2 - 1) # Level height in zones

            warp = Event(eventType, eventPayload, xPos, yPos)
            eventList.append(warp)

            # Add events to critical tiles list
            criticalTiles.append(coord_to_map_offset_only_terrain_no_split(xPos, yPos, stageInfo.tilesInMap))
    #print(criticalTiles)

    #####################
    # Super Energy Bank #
    #####################


    if stageInfo.stageNumber in [5,6]:

        eventList.append(Event(events.Trap, 0x00, superBank.xPos, superBank.yPos))
        criticalTiles.append(coord_to_map_offset_only_terrain_no_split(superBank.xPos, superBank.yPos, stageInfo.tilesInMap))

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
    
    #print(f'randomMap:{randomMap}')
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
    # Change critical tile list to a map so this isn't quadratic?
    
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
                if not (coord_to_map_offset_only_terrain_no_split(xPos, yPos, stageInfo.tilesInMap) in criticalTiles):
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


