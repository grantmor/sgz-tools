from constants import *

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


# this and other functions may need to be made more generic to be reused with enemies...
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

    row = [0xf2, 0x1c] * 20

    print(row_header(row, True))
    print(tile_type_sequence(row, stdPalettes, palettePresent)(row, True))