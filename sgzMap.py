from dataclasses import *
import random

from sgzType import *

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
    eventMapData = []

    # Mutating input is lava
    for tile in mapData:
        eventMapData.append(tile)

    tileStride = engine.TilePalettePairLength if palettesPresent else 1 

    # Get list of event offsets
    eventPositionMap = {}
    for event in eventList:
        if not event.noTerrainModification:
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
    while tileIdx < len(eventMapData):
        if tileIdx in eventPositionMap:
            eventMapData[tileIdx] = eventPositionMap[tileIdx]
            if palettesPresent:
                eventMapData[tileIdx + 1] = tilePalette
        tileIdx += tileStride

    
    return eventMapData


def merge_enemy_list_map_data(mapData, enemyList, palettesPresent, stdPalettes):

    #print(f'before merging enemies:{mapData}')
    enemyMapData = []

    # Mutating input is lava
    for tile in mapData:
        enemyMapData.append(tile)

    tileStride = engine.TilePalettePairLength if palettesPresent else 1 

    # Get list of enemy offsets
    enemyPositionMap = {}
    for enemy in enemyList:
        enemyPositionMap[coord_to_map_offset_region_split(enemy.col, enemy.row, palettesPresent)] = enemy.type
    
    print(f'enemyPositionMap:{enemyPositionMap}')
    
    tileIdx = 0
    while tileIdx < len(enemyMapData):
        if tileIdx in enemyPositionMap:
            enemyMapData[tileIdx] = enemyPositionMap[tileIdx]
            if palettesPresent:
                enemyMapData[tileIdx + 1] = palettes.Enemy
        tileIdx += tileStride
    
    #print(f'after merging enemies:{enemyMapData}')
    return enemyMapData


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


def coord_to_map_offset_only_terrain_no_split(col, row):
    offset = row * engine.TilesInRow * engine.RegionsInZone + col
    return offset 


def pad_offset(offset, tilesInMap):
    numTilesInFullMap = engine.MaxZones * engine.RowsPerZone * engine.TilesInRow
    unusedtiles = numTilesInFullMap - tilesInMap

    return offset + unusedtiles


def coord_to_steps(coord):
    return coord * 8


def generate_events(eventType, quantity, criticalTiles, maxCoordY, terrainType, tilesInMap):
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

            currentEvent = Event(eventType, eventPayload, xPos, yPos, terrainType, False)
            newTileIdx = pad_offset(coord_to_map_offset_only_terrain_no_split(xPos, yPos), tilesInMap)

            if not (newTileIdx in criticalTiles): break

        tileIdxMap[newTileIdx] = True
        eventList.append(currentEvent)

    return tileIdxMap, eventList 