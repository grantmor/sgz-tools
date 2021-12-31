import random
from math import floor
from dataclasses import dataclass

from constants import *
from game import *

class Event:
    def __init__(self, eventType, payload, col, row): # will need to figureout first, 2ndtolast and last
        self.first = 0x02
        self.type = eventType
        self.payload = payload
        self.col = col
        self.row = row

        self.pen = 0xf1

        self.last = 0x00


class Stage:
    def __init__(self, stage, version): 

        # Need current/max for events, enemies (known size)
        # Constructor sets sane defaults
        # This object just takes configuration objects, validates, 
        # and returns stage data via methods for format requested
        # No state besides configuration
        # If errors occured, returns list of errors, and caller
        # Can handle appropriately

        self.stageNumber = stage

        if version == 'us11':
            if stage == 1:

                self.eventOffset = 0x02afe1
                self.eventSize = 0x8d
                
                self.terrainOffset = 0x0b00f0
                self.terrainSize = 0x01ba
                
                self.enemyOffset = 0x0b3288
                self.enemySize = 0x036c

                self.mapPtrOffsetA = 0x0b0000
                self.mapPtrOffsetB = 0x0b0008

                self.mapBasePtr = 0x80f0

                self.enemyPtrOffsetA = self.mapPtrOffsetA + 0x90
                self.enemyPtrOffsetB = self.enemyPtrOffsetA + 0x08

                self.enemyBasePtrVal = 0xb288

                self.baseEnemyPosRomAdr = 0x0ce0f
                self.baseStatInitRomAdr = 0xd194
                
                self.stageTimeOffset = 0x00
                self.startEnergyOffset = 0x26

                self.horizontalPosOffset = 0x0c
                self.verticalPosOffset = 0x0e

                self.playableZones = 4
                
                self.playerMaxEnergy = 600
                self.enemyMaxEnergy = 600

                self.warpTableRomAdr = 0xc0ff

                self.stageTime = 240

                self.tilesInMap = 640

            elif stage == 2:
                self.eventOffset = 0x02b06e
                self.eventSize = 0x7d
                
                self.terrainOffset = 0x0b041a
                self.terrainSize = 0x0436
               
                self.enemyOffset = 0x0b35f4
                self.enemySize = 0x18e

                self.mapPtrOffsetA = 0x0b0010
                self.mapPtrOffsetB = 0x0b0018

                self.mapBasePtr = 0x841a 

                self.enemyPtrOffsetA = self.mapPtrOffsetA + 0x90
                self.enemyPtrOffsetB = self.enemyPtrOffsetA + 0x08

                self.enemyBasePtrVal = 0xb5f4

                self.baseEnemyPosRomAdr = 0xceb3  
                self.baseStatInitRomAdr = 0xd1c4
                
                self.stageTimeOffset = 0x00
                self.startEnergyOffset = 0x26

                self.horizontalPosOffset = 0x0c
                self.verticalPosOffset = 0x0e

                self.playableZones = 4

                self.playerMaxEnergy = 600
                self.enemyMaxEnergy = 550

                self.warpTableRomAdr = 0xc103

                self.stageTime = 400

                self.tilesInMap = 640

            elif stage == 3:
                self.eventOffset = 0x02b0ed
                self.eventSize = 0x0fd
                
                self.terrainOffset = 0x0b06e0
                self.terrainSize = 0x097a
                
                self.enemyOffset = 0x0b3916 
                self.enemySize = 0x0716

                self.mapPtrOffsetA = 0x0b0020
                self.mapPtrOffsetB = 0x0b0028
                
                self.mapBasePtr = 0x86e0
                self.enemyBasePtrVal = 0xb916 

                self.enemyPtrOffsetA = self.mapPtrOffsetA + 0x90
                self.enemyPtrOffsetB = self.enemyPtrOffsetA + 0x08

                self.baseEnemyPosRomAdr = 0xd216 
                self.baseStatInitRomAdr = 0xd1f8
                
                self.stageTimeOffset = 0x00
                self.startEnergyOffset = 0x26

                self.horizontalPosOffset = 0x0c
                self.verticalPosOffset = 0x0e

                self.playableZones = 6

                self.playerMaxEnergy = 600
                self.enemyMaxEnergy = 700

                self.warpTableRomAdr = 0xc107

                self.stageTime = 480

                self.tilesInMap = 960

            elif stage == 4:
                self.eventOffset = 0x02b1ea
                self.eventSize = 0x012e

                self.terrainOffset = 0x0b0c24
                self.terrainSize = 0x04cc

                self.enemyOffset = 0x0b3e98
                self.enemySize = 0x0536
                
                self.mapPtrOffsetA = 0x0b0030
                self.mapPtrOffsetB = 0x0b0038
                
                self.mapBasePtr = 0x8c24

                self.enemyPtrOffsetA = self.mapPtrOffsetA + 0x90
                self.enemyPtrOffsetB = self.enemyPtrOffsetA + 0x08

                self.enemyBasePtrVal = 0xbe98

                self.baseEnemyPosRomAdr = 0xd248  # Only Battra 1
                self.baseStatInitRomAdr = 0xd22a
                
                self.stageTimeOffset = 0x00
                self.startEnergyOffset = 0x26

                self.horizontalPosOffset = 0x0c
                self.verticalPosOffset = 0x0e

                self.playableZones = 8

                self.playerMaxEnergy = 700
                self.enemyMaxEnergy = 550

                self.warpTableRomAdr = 0xc10b

                self.stageTime = 520

                self.tilesInMap = 1280

            elif stage == 5:
                self.eventOffset = 0x02b318
                self.eventSize = 0x0188
                self.terrainOffset = 0x0b10f0
                self.terrainSize = 0x0530
                self.enemyOffset = 0x0b43ce
                self.enemySize = 0x05ec

                self.mapPtrOffsetA = 0x0b0040
                self.mapPtrOffsetB = 0x0b0048
                
                self.mapBasePtr = 0x90f0

                self.enemyPtrOffsetA = self.mapPtrOffsetA + 0x90
                self.enemyPtrOffsetB = self.enemyPtrOffsetA + 0x08

                self.enemyBasePtrVal = 0xc3ce

                self.baseEnemyPosRomAdr = 0xd27a 
                self.baseStatInitRomAdr = 0xd25c
                
                self.stageTimeOffset = 0x00
                self.startEnergyOffset = 0x26

                self.horizontalPosOffset = 0x0c
                self.verticalPosOffset = 0x0e

                self.playableZones = 8

                self.playerMaxEnergy = 700
                self.enemyMaxEnergy = 800

                self.warpTableRomAdr = 0xc10f

                self.stageTime = 770

                self.tilesInMap = 1280

        elif version == 'j11':
            # TODO: Implement
            pass
        else:
            # Throw Error
            pass

@dataclass(frozen=True)
class StageConfig:
    playerPosX: int
    playerPosY: int

    enemyPosX: int
    enemyPosY: int

    secondEnemyPosX: int
    secondEnemyPosY: int

    stageTime: int

    playerEnergyStart: int
    playerEnergyMax: int

    enemyEnergyStart: int
    enemyEnergyMax: int
    
    warpX: int
    warpY: int

@dataclass(frozen=True)
class StageData:
    eventData: list
    mapData: list
    mapPtrA: int
    mapPtrB: int
    enemyData: list
    enemyPtrA: int
    enemyPtrB: int


@dataclass(frozen=True)
class EnemyUnit:
    type: int
    col: int
    row: int


tiles = Tiles()
events = Events()
items = Items()
enemies = Enemies()
palettes = Palettes()
engine = Engine()


@dataclass(frozen=True)
class SuperBank:
    xPos: int
    yPos:int

def print_uncompressed_map_data(data, palettesPresent):
    tileStride = engine.TilePalettePairLength if palettesPresent else 1

    rowOffset = 0
    nextRowOffset = engine.TilesInRow * tileStride

    rowIdx = 0
    while rowIdx < int(len(data) / (engine.TilesInRow * tileStride)):
        if rowIdx % (engine.MaxZones) == 0:
            print('')

        row = bytearray() 
        row += data[rowOffset:nextRowOffset]

        string = ''
        for char in row:
            string += str(char) + ' '

        print(string)

        rowIdx += 1 
        rowOffset += (20 * tileStride)
        nextRowOffset += (20 * tileStride)


def bit_list_to_byte(bitList):
    placeValue = 128

    byte = 0x00

    for bitIdx, bit in enumerate(bitList):
        byte += bitList[bitIdx] * placeValue
        placeValue = placeValue // 2
    
    return byte


def switch_list_to_row_header(typeSwitches):
    # Pad
    typeSwitchLength = len(typeSwitches)
    bitFieldLength = 24
    numMissingBits = bitFieldLength - typeSwitchLength

    while numMissingBits > 0:
        typeSwitches.append(0)    
        numMissingBits -= 1

    switchListPos = 0

    bits = 0x000000
    while switchListPos < bitFieldLength:
        bits += (0x800000 * typeSwitches[switchListPos])

        # Don't shift if this is the last bit
        if switchListPos < bitFieldLength - 1:
            bits = bits >> 1

        switchListPos += 1

    firstByte = bits & 0x0000ff

    secondByte = bits & 0x00ff00
    secondByte = secondByte >> (8 * 1)

    thirdByte = bits & 0xff0000
    thirdByte = thirdByte >> (8 * 2)

    rowHeader = bytes([firstByte, secondByte, thirdByte])

    #print('\nRow Header:')
    #for byte in rowHeader:
    #    print(byte)

    return rowHeader


def row_header(mapRow, palettePresent):
    tileStride = engine.TilePalettePairLength if palettePresent else 1

    typeSwitches = []

    curTileType = 0x00
    prevTileType = 0x00 

    tilePosition = 0
    while tilePosition < (engine.TilesInRow * tileStride):
        curTileType = mapRow[tilePosition]

        if tilePosition == 0:
            typeSwitches.append(engine.NewTile)
            curTileType = mapRow[tilePosition]
        else:
            if curTileType != prevTileType:
                typeSwitches.append(engine.NewTile)
            else:
                typeSwitches.append(engine.SameTile)
        prevTileType = curTileType
        tilePosition += tileStride

    rowHeader = switch_list_to_row_header(typeSwitches)

    return rowHeader


def tile_type_sequence(mapRow, stdPalettes, palettePresent):
    newTileSequence = bytearray()

    tileStride = engine.TilePalettePairLength if palettePresent else 1

    curTileType = 0x00
    prevTileType = 0x00
    
    tileIdx = 0
    rowLength = len(mapRow)

    while tileIdx < rowLength:
        curTileType = mapRow[tileIdx]

        if curTileType != prevTileType:
            newTileSequence.append(curTileType)
            newTileSequence.append(stdPalettes[curTileType])

        prevTileType = curTileType
        tileIdx += tileStride
    
    return newTileSequence


def compress_map_data(mapData, stdPalettes, palettePresent):
    compressedMapData = bytes()

    #print('*** cmd ***')
    tileStride = engine.TilePalettePairLength if palettePresent else 1
    numRows = int(len(mapData) / tileStride / engine.TilesInRow)

    #print(f'numRows: {numRows}')
    #print(f'len mapdata: {len(mapData)}')

    #print(f'compress_map_data() numRows: {numRows}')

    bRegionOffset = 0x00

    for rowIdx, row in enumerate(range(0, numRows)):
        rowOffset = rowIdx * engine.TilesInRow * tileStride
        nextRowOffset = (rowIdx + 1) * engine.TilesInRow * tileStride

        rowData = bytes()
        rowSlice = mapData[rowOffset:nextRowOffset]

        rowHeader = row_header(rowSlice, palettePresent)

        typeSequence = tile_type_sequence(rowSlice, stdPalettes, palettePresent)
        rowData = rowHeader + typeSequence

        #print(f'Compressed row header: {rowHeader}')
        #print()
        #print(f'Adding compressed row:' )
        #for byte in rowData:
        #    print(byte)


        compressedMapData += rowData

        # # # Removed floor()
        if rowIdx == int(numRows / 2) - 1:
            # PLUS ONE TEST
            bRegionOffset = len(compressedMapData)
            #print(f'bRegionOffset:{bRegionOffset}')
            #print(f'halfwayRow:{rowIdx}')
            #print()

    return bRegionOffset, compressedMapData


# Zones are populated starting with the A region (west), folowed by the B Region (east)
def coord_to_map_offset_region_split(col, row, palettePresent):

    #print()
    #print(f'coord_to_map_offset')

    tileStride = engine.TilePalettePairLength if palettePresent else 1
    tilesInMap = engine.MaxZones * engine.RowsPerZone * engine.TilesInRow
    regionModifier = int(tilesInMap / 2 - engine.TilesInRow) if col >= engine.TilesInRow else 0
    offset = (row * engine.TilesInRow  + col + regionModifier) * tileStride

    #print(f'col: {col}, row: {row}, offset: {offset}')    
    return offset 


def event_obj_to_tile(event):
    eventTileMap = {
        events.EnergyResupply: tiles.ResupplyBase,
        events.Item: tiles.ItemPoint,
        events.Message: tiles.ItemPoint,
        events.Trap: tiles.AreaPoint
    }

    return eventTileMap[event.type]


def merge_event_list_map_data(mapData, eventList, insertSpecialEnergy, palettesPresent, stdPalettes):
    tileStride = engine.TilePalettePairLength if palettesPresent else 1 

    # Get list of event offsets
    eventPositionMap = {}
    for event in eventList:
        eventPositionMap[coord_to_map_offset_region_split(event.col, event.row, palettesPresent)] = event_obj_to_tile(event)

    # Upgrade Resupply Bases to Special Energy
    if insertSpecialEnergy:
        specialEnergiesInserted = 0

        for offset, tileType in eventPositionMap.items():
            if specialEnergiesInserted < 3 and tileType == tiles.ResupplyBase:
                eventPositionMap[offset] = tiles.SpecialEnergy
                specialEnergiesInserted += 1

    tilePalette = 0x00
    if event.type == events.EnergyResupply:
        tilePalette = palettes.Blue


    elif event.type == events.Item:
        tilePalette = palettes.Yellow
    elif event.type == events.Trap:
        tilePalette == palettes.Orange
    elif event.type == events.Message:
        tilePalette == palettes.Yellow

    tileIdx = 0
    while tileIdx < len(mapData):
        if tileIdx in eventPositionMap:
            mapData[tileIdx] = eventPositionMap[tileIdx]
            if palettesPresent:
                mapData[tileIdx + 1] = tilePalette
        tileIdx += tileStride

    
    return mapData


def merge_enemy_list_map_data(mapData, enemyList, palettesPresent, stdPalettes):
    tileStride = engine.TilePalettePairLength if palettesPresent else 1 

    # Get list of enemy offsets
    enemyPositionMap = {}
    for enemy in enemyList:
        enemyPositionMap[coord_to_map_offset_region_split(enemy.col, enemy.row, palettesPresent)] = enemy.type
    
    tileIdx = 0
    while tileIdx < len(mapData):
        if tileIdx in enemyPositionMap:
            mapData[tileIdx] = enemyPositionMap[tileIdx]
            if palettesPresent:
                mapData[tileIdx + 1] = palettes.Enemy
        tileIdx += tileStride
    
    return mapData


def pack_map(self, events, map, enemies): 
    pass


def insert_palettes(mapData, stdPalettes):
    mapDataWithPalettes = bytearray()
    
    for tile in mapData:
        currentTile = tile
        mapDataWithPalettes.append(currentTile)
        mapDataWithPalettes.append(stdPalettes[currentTile])

    return mapDataWithPalettes


def split_map_by_region(mapData):
    regionA = bytearray()
    regionB = bytearray()

    tileIdx = 0
    rowIdx = 0
    while tileIdx < len(mapData):
        rowIdx = tileIdx % (engine.TilesInRow * 2)
        if rowIdx < 20:
            regionA.append(mapData[tileIdx])
        else:
            regionB.append(mapData[tileIdx])
        tileIdx += 1
    return regionA + regionB

def pad_map(mapData, padTile):
    mapTiles = len(mapData)
    maxMapTiles = engine.MaxZones * engine.RowsPerZone * engine.TilesInRow

    paddedMap = bytearray()

    if (mapTiles < maxMapTiles):
        numPadTiles = maxMapTiles - mapTiles
        for tile in range(0, numPadTiles):
            paddedMap.append(padTile)
    #print()
    #print('pad_map:')
    #print(f'len map: {len(mapData)}')
    #print(f'len padded map: {len(paddedMap)}')
    #print()

    return paddedMap + mapData


# Expects data for a full 8-zone map
# Assumes Region A is at standard retail cartridge address for now, only b is moved based on data
def pack_test_map(stage, eventInput, mapInput, enemyInput, stdPalettes, palettesPresent):

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
        eventData.append(event.pen)
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
    bRegionEnemyOffset, compressedEnemyData  = compress_map_data(mapEventData, stdPalettes, True)

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

def int_to_16_le(num):
    word = bytearray()
    firstByte = num & 0x00ff

    secondByte = num & 0xff00
    secondByte = secondByte >> 8

    word.append(firstByte)
    word.append(secondByte)

    return word


def patch_enemy_pos_instructions(fileObj, hPos, vPos, hAdr, vAdr):
    # This works, but is this the right opcode???
    lda = 0xa2
    enemyHzInstruction = bytes([lda]) + hPos
    enemyVtInstruction = bytes([lda]) + vPos

    fileObj.seek(hAdr)
    fileObj.write(enemyHzInstruction)

    fileObj.seek(vAdr)
    fileObj.write(enemyVtInstruction)


def patch_stage(romPath, stageInfo, stageConfig, stageData):
    rom = open(romPath, 'r+b')

    # Write Stage Terrain Region Pointers
    rom.seek(stageInfo.mapPtrOffsetA)
    #print(f'Stage mapPtrA:{stageData.mapPtrA}')
    rom.write(stageData.mapPtrA)

    rom.seek(stageInfo.mapPtrOffsetB)
    #print(f'Stage mapPtrB:{stageData.mapPtrB}')
    rom.write(stageData.mapPtrB)

    # Write Stage Map Data
    rom.seek(stageInfo.terrainOffset)
    rom.write(stageData.mapData)

    # Write Stage Enemy Region Pointers
    rom.seek(stageInfo.enemyPtrOffsetA)
    rom.write(stageData.enemyPtrA)

    rom.seek(stageInfo.enemyPtrOffsetB)
    rom.write(stageData.enemyPtrB)

    # Write Stage Enemy Data
    rom.seek(stageInfo.enemyOffset)
    rom.write(stageData.enemyData)

    # Write Stage Event Data
    rom.seek(stageInfo.eventOffset)
    rom.write(stageData.eventData)

    # Time
    rom.seek(stageInfo.baseStatInitRomAdr + stageInfo.stageTimeOffset)
    time = int_to_16_le(stageConfig.stageTime)
    rom.write(time)

    # Player Position
    playerPositionBuffer = bytearray()
    playerPositionBuffer += int_to_16_le(stageConfig.playerPosX)
    playerPositionBuffer += bytes([stageConfig.playerPosY])

    rom.seek(stageInfo.baseStatInitRomAdr + stageInfo.horizontalPosOffset)
    rom.write(playerPositionBuffer)

    # Warp Table
    warpDataBuffer = bytearray() 
    warpDataBuffer += int_to_16_le(stageConfig.warpX) 
    warpDataBuffer += int_to_16_le(stageConfig.warpY)

    rom.seek(stageInfo.warpTableRomAdr)
    rom.write(warpDataBuffer)

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
        enemyPositionBuffer += bytes([0x03]) # Need to debug more to know what the last byte is used for

        rom.seek(stageInfo.baseEnemyPosRomAdr)
        rom.write(enemyPositionBuffer)

    elif stageInfo.stageNumber == 4:
        # This part can be moved to generic block...?
        enemyPositionBuffer = bytearray()
        enemyPositionBuffer += enemyHorizontalPos
        enemyPositionBuffer += enemyVerticalPos

        rom.seek(stageInfo.baseEnemyPosRomAdr)
        rom.write(enemyPositionBuffer)

        # Battra 2
        enemyHorizontalPos = int_to_16_le(stageConfig.secondEnemyPosX)
        enemyVerticalPos = int_to_16_le(stageConfig.secondEnemyPosY)

        hPosInstructionAdr = 0xe03c
        vPosInstructionAdr = 0xe042
            
        patch_enemy_pos_instructions(rom, enemyHorizontalPos, enemyVerticalPos, hPosInstructionAdr, vPosInstructionAdr)

    else:
        enemyPositionBuffer = bytearray()
        enemyPositionBuffer += enemyHorizontalPos
        enemyPositionBuffer += enemyVerticalPos

        rom.seek(stageInfo.baseEnemyPosRomAdr)
        rom.write(enemyPositionBuffer)

    # Energy Buffer
    energyBuffer = bytes()
    energyBuffer += int_to_16_le(stageConfig.playerEnergyStart)
    energyBuffer += int_to_16_le(stageConfig.playerEnergyMax)
    energyBuffer += int_to_16_le(stageConfig.enemyEnergyStart)
    energyBuffer += int_to_16_le(stageConfig.enemyEnergyMax)

    # Player/Enemy Energy
    rom.seek(stageInfo.baseStatInitRomAdr + stageInfo.startEnergyOffset)
    rom.write(energyBuffer)

    rom.close()