from dataclasses import dataclass

@dataclass(frozen=True)
class Opcodes:
    JmpAbs = 0x4c

    LdaIme = 0xa9
    LdaAbs = 0xad
    LdaAbsLongIdxX = 0xbf

    StaAbs = 0x8d

    CmpIme = 0xc9
    CmpAbs = 0xcd

    BneRel = 0xd0

opcodes = Opcodes()

@dataclass(frozen=True)
class RandomizerFlags:
    PersistentEnergy: bool
    PersistentTime: bool
    NoEnemySpawnCritical: bool
    NoEnemySpawnEvent: bool
    NoMechaGodzillaWarp: bool

@dataclass(frozen=True)
class Game:
    PersistentTimePatchRomAdr: int = 0x00d059
    PersistentEnergyPatchRomAdr: int = 0x00d0b3

    PersistentTimePatchSubAdr: int = 0x00
    PersistentEnergyPatchSubAdr: int = 0x00

    NoMechaGodzillaWarpPatchRomAdr: int = 0x00c6df

    # Instead of patching these completely out like this,
    # Jump to a subroutine that initializes health, time,
    # etc. if it's zero

    #PersistentTimeCode = bytearray([
    #    0x4c,
    #    0x6a,
    #    0xd0
    #])

    PersistentTimeCode = bytearray([
        opcodes.JmpAbs, 0x8b, 0xf5,

    ])

    PersistentTimeSub = bytearray([
        # Store Time in memory for unrelated reasons (jumped over this code)
        opcodes.LdaAbsLongIdxX, 0x94, 0xd1, 0x01,
        opcodes.StaAbs, 0x85, 0x11,
        opcodes.LdaAbsLongIdxX, 0x95, 0xd1, 0x01,
        opcodes.StaAbs, 0x86, 0x11,

        # If Hi Byte of Time isn't zero, don't initialize
        opcodes.LdaAbs, 0x2b, 0x0e,
        opcodes.CmpIme, 0x00,
        opcodes.BneRel, 0x11, # decimal 17### adr of jump at end

        # Same for Lo Byte
        opcodes.LdaAbs, 0x2b, 0x0e,
        opcodes.CmpIme, 0x00,
        opcodes.BneRel, 0x0a, #decimal 11 ### adr of jump at end

        # If both bytes are zero, need to initialize time
        # Hard-coded 768 seconds for now
        opcodes.LdaIme, 0x00,
        opcodes.StaAbs, 0x2b, 0x0e,
        opcodes.LdaIme, 0x03,
        opcodes.StaAbs, 0x2c, 0x0e,

        opcodes.JmpAbs, 0x6d, 0xd0
    ])

    PersistentEnergyCode = bytearray([
        opcodes.JmpAbs, 0xb4, 0xf5
    ])

    PersistentEnergySub = bytearray([
        # Store (max energy?)
        opcodes.LdaAbsLongIdxX, 0xbc, 0xd1, 0x01,
        opcodes.StaAbs, 0x73, 0x0e,
        opcodes.LdaAbsLongIdxX, 0xbd, 0xd1, 0x01,
        opcodes.StaAbs, 0x74, 0x0e,

        # If Hi Byte of Energy isn't zero, don't initialize
        opcodes.LdaAbs, 0x71, 0x0e,
        opcodes.CmpIme, 0x00,
        opcodes.BneRel, 0x13, # decimal 19### adr of jump at end

        # Same for Lo Byte
        opcodes.LdaAbs, 0x72, 0x0e,
        opcodes.CmpIme, 0x00,
        opcodes.BneRel, 0x0c, #decimal 13 ### adr of jump at end

        # Didn't branch, need to initizlize energy
        opcodes.LdaAbs, 0x73, 0x0e,
        opcodes.StaAbs, 0x71, 0x0e,

        opcodes.LdaAbs, 0x74, 0x0e,
        opcodes.StaAbs, 0x72, 0x0e,

        opcodes.JmpAbs, 0xcf, 0xd0
    ])
    


    NoWarpCode = bytearray([
        opcodes.JmpAbs,
        0x32,
        0xc7
    ])

game = Game()

def patch_features(romPath, pTime, pEnergy, noWarp):
    rom = open(romPath, 'r+b')

    # Patch Persistent Time
    if pTime:
        # Jump to Time Sub
        rom.seek(game.PersistentTimePatchRomAdr)
        rom.write(game.PersistentTimeCode)

        # Time Sub
        rom.seek(0xf58b)
        rom.write(game.PersistentTimeSub)

    # Patch Persistent Energy
    if pEnergy:
        # Jump to Energy Sub
        rom.seek(game.PersistentEnergyPatchRomAdr)
        rom.write(game.PersistentEnergyCode)

        # Energy Sub
        rom.seek(0xf5b4)
        rom.write(game.PersistentEnergySub)

    # Patch No Warp
    if noWarp:
        rom.seek(game.NoMechaGodzillaWarpPatchRomAdr)
        rom.write(game.NoWarpCode)

    rom.close()