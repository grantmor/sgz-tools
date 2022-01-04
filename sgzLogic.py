
def int_to_16_le(num):
    word = bytearray()
    firstByte = num & 0x00ff

    secondByte = num & 0xff00
    secondByte = secondByte >> 8

    word.append(firstByte)
    word.append(secondByte)

    return word