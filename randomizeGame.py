import sys
import random

from perlin_noise import *

from sgzConst import *
from sgzGame import *
from sgzType import *
from sgzStage import *
from sgzMap import *


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
        mapParams = MapParameters(2, 8, 4, 2, 0, 16, 1)
    elif stageInfo.stageNumber == 2:
        mapParams = MapParameters(2, 8, 4, 2, 0, 16, 1)
    elif stageInfo.stageNumber == 3:
        mapParams = MapParameters(2, 10, 8, 3, 6, 24, 1)
    elif stageInfo.stageNumber == 4: 
        mapParams = MapParameters(2, 12, 10, 4, 0, 48, 1)
    elif stageInfo.stageNumber == 5: 
        mapParams = MapParameters(2, 12, 10, 3, 0, 48, 1)

    xTiles, yTiles = engine.TilesInRow * 2, stageInfo.playableZones // 2 * engine.RowsPerZone 

    ##########
    # Events #
    ##########

    eventList = []

    # Mothership
    mothershipOffsets = {
        2 : coord_to_map_offset_only_terrain_no_split(31, 5),
        3 : coord_to_map_offset_only_terrain_no_split(9, 21),
        4 : coord_to_map_offset_only_terrain_no_split(38, 28),
        5 : coord_to_map_offset_only_terrain_no_split(2, 30)
    }

    #for val in mothershipOffsets.values():
    #    print(f'mufoOffset: {val}')

    criticalTiles = {}

    # Choose a more appropriate tile later
    baseTerrainType = tiles.SpecialGround

    for val in mothershipOffsets.values():
        criticalTiles[val] = True

    if stageInfo.stageNumber == 5:
        superBankEvent = Event(events.Trap, 0x00, superBank.xPos, superBank.yPos, baseTerrainType, True)
        superBankOffset = coord_to_map_offset_only_terrain_no_split(superBank.xPos, superBank.yPos)
        criticalTiles[superBankOffset] = True
        
    # Items
    itemTiles, itemEvents = generate_events(events.Item, mapParams.numItems, criticalTiles, maxCoordY, baseTerrainType, stageInfo.tilesInMap)
    criticalTiles.update(itemTiles)
    #print(f'criticalTiles after Items: {criticalTiles}')

    # Resupplies
    resupplyTiles, resupplyEvents = generate_events(events.EnergyResupply, mapParams.numResupplies, criticalTiles, maxCoordY, baseTerrainType, stageInfo.tilesInMap)
    criticalTiles.update(resupplyTiles)
    #print(f'criticalTiles after Resupplies: {criticalTiles}')

    # Traps
    trapTiles, trapEvents = generate_events(events.Trap, mapParams.numTraps, criticalTiles, maxCoordY, baseTerrainType, stageInfo.tilesInMap)
    criticalTiles.update(trapTiles)
    #print(f'criticalTiles after Traps: {criticalTiles}')

    # Warp
    warpTiles, warpEvents = generate_events('warp', mapParams.numWarps, criticalTiles, maxCoordY, baseTerrainType, stageInfo.tilesInMap)
    criticalTiles.update(warpTiles)
    #print(f'criticalTiles after Warps: {criticalTiles}')

    eventList = itemEvents + resupplyEvents + trapEvents + warpEvents

    if stageInfo.stageNumber == 5:
        eventList.append(superBankEvent)


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
    

    # Add Mothership Tile    
    # 2 doesn't work for some reason?
    if 2 < stageInfo.stageNumber < 6:
        mufoOffset = mothershipOffsets[stageInfo.stageNumber]
        randomMap[mufoOffset] = tiles.Mothership
        
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

    # Placing enemies - do this more efficiently later -
    # Generate list of required positions first, then assign positions

    
    enemyTypes = [
        enemies.Tank,
        enemies.Missle,
        enemies.Mine
    ]

    enemyList = []

    #print(f'randomizerFlags.noEnemySpawnEvent:{randomizerFlags.NoEnemySpawnEvent}')
    for enemyType in enemyTypes:
        for enemy in range(0, mapParams.numEnemies // len(enemyTypes)):
            while True:
                xPos = random.randint(0, engine.TilesInRow * 2)
                yPos = random.randint(maxCoordY, 31)

                if not randomizerFlags.NoEnemySpawnEvent: break
                #print(f'xPos, YPos: {xPos},{yPos}') 
                #print(f'Offset: {coord_to_map_offset_only_terrain_no_split(xPos, yPos, stageInfo.tilesInMap)}')
                #print(f'criticalTiles: {criticalTiles}')
                if not (pad_offset(coord_to_map_offset_only_terrain_no_split(xPos, yPos), stageInfo.tilesInMap) in criticalTiles): break

            enemyList.append(EnemyUnit(enemyType, xPos, yPos))
    
    #print(f'EnemyList: {enemyList}')
    
    # Log enemy offsets
    #for enemy in enemyList:
    #    print(coord_to_map_offset(enemy.col, enemy.row, False))

    #print(f'Final inaccessibleTiles list:{inaccessibleTiles}')
    stageConfig = stage_config(stageInfo, randomizerFlags, inaccessibleTiles, maxCoordY)

    return eventList, randomMap, enemyList, stageConfig


# patches in super energy bank tile coordinates and returns super bank coords for generate_stage() for stage 5
def patch_super_bank():
    patchList = []

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

    #fileObj.seek(xAdr)
    #fileObj.write(bankXPosInstruction)
    patchList.append(
        Patch(
            xAdr,
            bankXPosInstruction
        )
    )

    #fileObj.seek(yAdr)
    #fileObj.write(bankYPosInstruction)
    patchList.append(
        Patch(
            yAdr,
            bankYPosInstruction
        )
    )

    return  superBank, patchList


def randomize_game(gameVersion, randomizerFlags, output):
    patchList = []

    # Randomizer Flags (arguments later)

    # Patch Game
    patchList += patch_features(
        gameVersion,
        randomizerFlags
    )

    if randomizerFlags.RandomizeMaps:
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

        #rom = open(filePath, 'r+b')

        # Randomize Bagan's Location
        enemyHorizontalPos = int_to_16_le(random.randint(0, 0xff))
        enemyVerticalPos = int_to_16_le(random.randint(0, 0xff))

        hInstructionAdr = 0xe067
        vInstructionAdr = 0xe06d

        patchList += patch_enemy_pos_instructions(enemyHorizontalPos, enemyVerticalPos, hInstructionAdr, vInstructionAdr)
        superBank, superBankPatch = patch_super_bank()
        
        patchList += superBankPatch


        # Patching Stages
        numStages = 5
        stageRange = range(1, numStages + 1)

        for stage in stageRange:
            stageInfo = stage_info(stage)

            # Move this into stage eventually
            if stage == 2 or stage == 3:
                stdPalettes = ruralPalette
            else:
                stdPalettes = urbanPalette 

            # Loop until generated stage is small enough
            mapsGenerated = 0
            while True:
                mapsGenerated += 1
                eventList, randomMap, enemyList, stageConfig = generate_stage(stageInfo, randomizerFlags, superBank, stdPalettes)

                #print_uncompressed_map_data(randomMap)

                stageData = pack_stage(
                    stageInfo, 
                    eventList, 
                    randomMap,
                    enemyList, 
                    stdPalettes, 
                    True
                )

                #print()
                #print(f'Stage: {stageInfo.stageNumber}')
                #print(f'curMapDataSize: {len(stageData.mapData)}')
                #print(f'Max map size for this stage: {stageInfo.terrainSize}')
                #print(f'curEnemyDataSize: {len(stageData.enemyData)}')
                #print(f'Max enemy size for this stage: {stageInfo.enemySize}')
                #print(f'Maps generated: {mapsGenerated}')
                #print()

                eventMapDataOk = (len(stageData.mapData) <= stageInfo.terrainSize)
                enemyMapDataOk = (len(stageData.enemyData) <= stageInfo.enemySize)

                if eventMapDataOk and enemyMapDataOk: break

            patchList += patch_stage(gameVersion, stageInfo, stageConfig, stageData, randomizerFlags)

    blob = build_ips_blob(patchList)

    if output =='stdout':
        sys.stdout.buffer.write(blob)
    else:
        ipsFile = open(output, 'w+b')
        ipsFile.write(blob)
        ipsFile.close()


def build_ips_blob(patchList):
    ipsData = bytearray()

    magicNo = bytes([0x50, 0x41, 0x54, 0x43, 0x48])
    endOfFile = bytes([0x45, 0x4f, 0x46])

    ipsData += magicNo

    for patch in patchList:
        ipsData += patch.address.to_bytes(3, 'big')

        # Annoyingly, bytearrays seem to dislike only holding one byte?
        if type(patch.data) == int:
            dataSize = 1
        else:
            dataSize = len(patch.data)

        ipsData += dataSize.to_bytes(2, 'big')

        if type(patch.data) == int:
            ipsData += bytes([patch.data])
        else:
            ipsData += patch.data

    ipsData += endOfFile

    return ipsData
