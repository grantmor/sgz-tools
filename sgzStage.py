import random
from math import floor
from dataclasses import dataclass

from sgzConst import *
from sgzGame import *
from sgzType import *

from sgzMap import *
from sgzLogic import *

# Expects data for a full 8-zone map
# Assumes Region A is at standard retail cartridge address for now, only b is moved based on data

def stage_info(stageNum):
    return Stage(stageNum, 'us11')


def stage_config(stageInfo, randomizerFlags, inaccessibleTiles, maxCoordY):

    # Refactor this to use stageInfo object later
    if stageInfo.stageNumber in [1,2]:
        tilesInMap = 640
    elif stageInfo.stageNumber == 3:
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

        #print(f'playerOffset:{playerOffset}')

        if not (playerOffset in inaccessibleTiles): break

    while True:
        enemyX = random.randint(0, 39) 
        enemyY = random.randint(maxCoordY, 31)

        enemyStepsX = coord_to_steps(enemyX)
        enemyStepsY = coord_to_steps(enemyY)

        if stageInfo.stageNumber == 4:
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

        #print(f'firstEnemyPosOffset: {firstPosOffset}')
        #print(f'secondEnemyPosOffset: {secondPosOffset}')

        if stageInfo.stageNumber != 4: secondPosOk = True
        if firstPosOk and secondPosOk: break
    
    while True:
        warpX = random.randint(0, 39)
        warpY = random.randint(maxCoordY, 31)

        warpStepsX = coord_to_steps(warpX)
        warpStepsY = coord_to_steps(warpY)

        warpToPosOffset = coord_to_map_offset_only_terrain_no_split(warpX, warpY)
        #print(f'warpToPosOffset:{warpToPosOffset}')

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


def pack_stage(stage, eventInput, mapInput, enemyInput, stdPalettes, palettesPresent):

    #print(f'\n\n\n*** Stage  {stage.stageNumber} ***\n')
    #print(f'\nmap before pad:')
    #print_uncompressed_map_data(mapInput, False)

    padTile = tiles.RockyMountain if stage.stageNumber in [2,3] else tiles.SkyScraper
    mapData = pad_map(mapInput, padTile)
    
    #print(f'\nmap after pad')
    #print_uncompressed_map_data(mapData, False)
    #print(f'len after padding:{len(mapData)}')
    mapData = split_map_by_region(mapData)

    #print(f'\nmap after split')
    #print_uncompressed_map_data(mapData, False)

    mapData = insert_palettes(mapData, stdPalettes)

    #print(f'\nmap after palette insertion ')
    #print_uncompressed_map_data(mapData, True)

    eventData = bytearray()
    # Eventually, put in "standard events?"
    for event in eventInput:
        eventData.append(event.first)
        eventData.append(event.type)
        eventData.append(event.payload)
        eventData.append(event.col)
        eventData.append(event.row)
        eventData.append(event.terrainType)
        eventData.append(event.last)

    # Insert Special Energy in Stage 5
    if stage.stageNumber == 5:
        insertSpecialEnergy = True
    else:
        insertSpecialEnergy = False

    # Merge event data with terrain data    
    mapEventData = merge_event_list_map_data(mapData, eventInput, insertSpecialEnergy, palettesPresent, stdPalettes)

    # Compress Terrain Data
    bRegionTerrainOffset, compressedMapData = compress_map_data(mapEventData, stdPalettes, True)
    #print(f'bRegionTerrainOffset:{bRegionTerrainOffset}')
    # Compress Enemy Data - Unfortunately, this mutates mapData - will need to figure out how to deep copy later...
    mapEnemyData = merge_enemy_list_map_data(mapEventData, enemyInput, palettesPresent, stdPalettes) 
    bRegionEnemyOffset, compressedEnemyData  = compress_map_data(mapEnemyData, stdPalettes, True)

    # Computing pointers to map data
    aRegionPointer = stage.mapBasePtr
    bRegionPointer = aRegionPointer + bRegionTerrainOffset

    #print(f'aRegionPointer: {aRegionPointer}')
    #print(f'bRegionPointer: {bRegionPointer}')

    # Compute pointers to enemy data
    aRegionEnemyPointer = stage.enemyBasePtrVal
    bRegionEnemyPointer = aRegionEnemyPointer + bRegionEnemyOffset

    #print(f'aRegionEnemyPointer: {aRegionEnemyPointer}')
    #print(f'bRegionEnemyPointer: {bRegionEnemyPointer}')

    data = StageData(
        eventData, 
        compressedMapData, int_to_16_le(aRegionPointer), int_to_16_le(bRegionPointer),
        compressedEnemyData, int_to_16_le(aRegionEnemyPointer), int_to_16_le(bRegionEnemyPointer)
    )

    return data


def patch_enemy_pos_instructions(hPos, vPos, hAdr, vAdr):
    patchList = []

    # This works, but is this the right opcode???
    lda = 0xa2
    enemyHzInstruction = bytes([lda]) + hPos
    enemyVtInstruction = bytes([lda]) + vPos

    #fileObj.seek(hAdr)
    #fileObj.write(enemyHzInstruction)
    patchList.append(
        Patch(
            hAdr, 
            enemyHzInstruction
        )
    )

    #fileObj.seek(vAdr)
    #fileObj.write(enemyVtInstruction)
    patchList.append(
        Patch(
            vAdr, 
            enemyVtInstruction
        )
    )

    return patchList


def patch_stage(gameVersion, stageInfo, stageConfig, stageData):
    patchList = []

    # Write Stage Terrain Region Pointers
    #rom.seek(stageInfo.mapPtrOffsetA)
    #print(f'Stage mapPtrA:{stageData.mapPtrA}')
    #rom.write(stageData.mapPtrA)
    patchList.append(
        Patch(
            stageInfo.mapPtrOffsetA, 
            stageData.mapPtrA
        )
    )

    #rom.seek(stageInfo.mapPtrOffsetB)
    #print(f'Stage mapPtrB:{stageData.mapPtrB}')
    #rom.write(stageData.mapPtrB)
    patchList.append(
        Patch(
            stageInfo.mapPtrOffsetB, 
            stageData.mapPtrB
        )
    )
    
    # Write Stage Map Data
    #rom.seek(stageInfo.terrainOffset)
    #rom.write(stageData.mapData)
    patchList.append(
        Patch(
            stageInfo.terrainOffset, 
            stageData.mapData
        )
    )

    # Write Stage Enemy Region Pointers
    #rom.seek(stageInfo.enemyPtrOffsetA)
    #rom.write(stageData.enemyPtrA)
    patchList.append(
        Patch(
            stageInfo.enemyPtrOffsetA, 
            stageData.enemyPtrA
        )
    )

    #rom.seek(stageInfo.enemyPtrOffsetB)
    #rom.write(stageData.enemyPtrB)
    patchList.append(
        Patch(
            stageInfo.enemyPtrOffsetB, 
            stageData.enemyPtrB
        )
    )

    # Write Stage Enemy Data
    #rom.seek(stageInfo.enemyOffset)
    #rom.write(stageData.enemyData)
    patchList.append(
        Patch(
            stageInfo.enemyOffset, 
            stageData.enemyData
        )
    )

    # Write Stage Event Data
    #rom.seek(stageInfo.eventOffset)
    #rom.write(stageData.eventData)
    patchList.append(
        Patch(
            stageInfo.eventOffset, 
            stageData.eventData
        )
    )

    # Time
    #rom.seek(stageInfo.baseStatInitRomAdr + stageInfo.stageTimeOffset)
    timeOffset = stageInfo.baseStatInitRomAdr + stageInfo.stageTimeOffset
    time = int_to_16_le(stageConfig.stageTime)

    #rom.write(time)
    patchList.append(
        Patch(
            timeOffset,
            time
        )
    )

    # Player Position
    playerPositionBuffer = bytearray()
    playerPositionBuffer += int_to_16_le(stageConfig.playerPosX)
    playerPositionBuffer += bytes([stageConfig.playerPosY])

    #rom.seek(stageInfo.baseStatInitRomAdr + stageInfo.horizontalPosOffset)
    playerPositionAdr = stageInfo.baseStatInitRomAdr + stageInfo.horizontalPosOffset

    #rom.write(playerPositionBuffer)
    patchList.append(
        Patch(
            playerPositionAdr, 
            playerPositionBuffer
        )
    )

    # Warp Table
    warpDataBuffer = bytearray() 
    warpDataBuffer += int_to_16_le(stageConfig.warpX) 
    warpDataBuffer += int_to_16_le(stageConfig.warpY)

    #rom.seek(stageInfo.warpTableRomAdr)
    #rom.write(warpDataBuffer)
    patchList.append(
        Patch(
            stageInfo.warpTableRomAdr, 
            warpDataBuffer
        )
    )

    # Enemy Position

    enemyHorizontalPos = int_to_16_le(stageConfig.enemyPosX)
    enemyVerticalPos = int_to_16_le(stageConfig.enemyPosY)

    if stageInfo.stageNumber == 1:
        # King Ghidorah's position x and y components randomly selected from two addresses each
        enemyPositionBuffer = bytearray()
        enemyPositionBuffer += enemyHorizontalPos
        enemyPositionBuffer += enemyVerticalPos
        enemyPositionBuffer += enemyHorizontalPos
        enemyPositionBuffer += enemyVerticalPos
        enemyPositionBuffer += bytes([0x03]) # Need to debug more to determine what the last byte is used for

        #rom.seek(stageInfo.baseEnemyPosRomAdr)
        #rom.write(enemyPositionBuffer)
        patchList.append(
            Patch(
                stageInfo.baseEnemyPosRomAdr, 
                enemyPositionBuffer
            )
        )

    elif stageInfo.stageNumber == 4:
        # This part can be moved to generic block...?
        # Battra 1
        enemyPositionBuffer = bytearray()
        enemyPositionBuffer += enemyHorizontalPos
        enemyPositionBuffer += enemyVerticalPos

        #rom.seek(stageInfo.baseEnemyPosRomAdr)
        #rom.write(enemyPositionBuffer)
        patchList.append(
            Patch(
                stageInfo.baseEnemyPosRomAdr, 
                enemyPositionBuffer
            )
        )

        # Battra 2
        enemyHorizontalPos = int_to_16_le(stageConfig.secondEnemyPosX)
        enemyVerticalPos = int_to_16_le(stageConfig.secondEnemyPosY)

        hPosInstructionAdr = 0xe03c
        vPosInstructionAdr = 0xe042

        # RETURN PATCHLIST FROM THIS    
        patchList += patch_enemy_pos_instructions(
                enemyHorizontalPos, 
                enemyVerticalPos, 
                hPosInstructionAdr, 
                vPosInstructionAdr
        )

    else:
        # Only Enemy Position
        enemyPositionBuffer = bytearray()
        enemyPositionBuffer += enemyHorizontalPos
        enemyPositionBuffer += enemyVerticalPos

        #rom.seek(stageInfo.baseEnemyPosRomAdr)
        #rom.write(enemyPositionBuffer)
        patchList.append(
            Patch(
                stageInfo.baseEnemyPosRomAdr, 
                enemyPositionBuffer
            )
        )

    # Energy Buffer
    energyBuffer = bytes()
    energyBuffer += int_to_16_le(stageConfig.playerEnergyStart)
    energyBuffer += int_to_16_le(stageConfig.playerEnergyMax)
    energyBuffer += int_to_16_le(stageConfig.enemyEnergyStart)
    energyBuffer += int_to_16_le(stageConfig.enemyEnergyMax)

    # Player/Enemy Energy
    #rom.seek(stageInfo.baseStatInitRomAdr + stageInfo.startEnergyOffset)
    energyOffsetAdr = stageInfo.baseStatInitRomAdr + stageInfo.startEnergyOffset
    #rom.write(energyBuffer)
    patchList.append(Patch(energyOffsetAdr, energyBuffer))

    return patchList