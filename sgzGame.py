from dataclasses import dataclass
from sgzLogic import *
from sgzType import *

@dataclass(frozen=True)
class Opcodes:
    JmpAbs = 0x4c

    LdaIme = 0xa9
    LdaAbs = 0xad
    LdaAbsLongIdxX = 0xbf

    LdyImeLong = 0xa0
    StaAbs = 0x8d

    CmpIme = 0xc9
    CmpAbs = 0xcd

    BneRel = 0xd0
    
    Nop = 0xea

opcodes = Opcodes()

@dataclass(frozen=True)
class RandomizerFlags:
    TimeLimit: int
    RandomizeMaps: bool
    PersistentEnergy: bool
    PersistentTime: bool
    PersistentInventory: bool
    NoEnemySpawnCritical: bool
    NoEnemySpawnEvent: bool
    NoMechaGodzillaWarp: bool
    NoStartingContinues: bool
    NoAddedContinues: bool

# Can't be frozen, need to supply time (and possible energy at runtime)
@dataclass
class Game:
    PersistentTimePatchRomAdr: int = 0x00d059
    PersistentEnergyPatchRomAdr: int = 0x00d0b3

    PersistentTimePatchSubAdr: int = 0x00
    PersistentEnergyPatchSubAdr: int = 0x00

    NoMechaGodzillaWarpPatchRomAdr: int = 0x00c6df

    # Might be a bug here or elsewhere, looks like this is getting written to one byte later
    # Note: all operands to 65c816 instructions are little-endian
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
        opcodes.BneRel, 0x11, 

        # Same for Lo Byte
        opcodes.LdaAbs, 0x2b, 0x0e,
        opcodes.CmpIme, 0x00,
        opcodes.BneRel, 0x0a, 

        # If both bytes are zero, need to initialize time
        # Default is 768, but this is replaced by user
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
        opcodes.BneRel, 0x13,

        # Same for Lo Byte
        opcodes.LdaAbs, 0x72, 0x0e,
        opcodes.CmpIme, 0x00,
        opcodes.BneRel, 0x0c,

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

    NoStartContinueInstruction = bytearray([
        opcodes.LdaIme, 0x00
    ])

    NoAddedContinueInstruction = bytearray([
        opcodes.LdyImeLong, 0x00, 0x00
    ])

    PersistentInventory = bytearray([
        opcodes.Nop,
        opcodes.Nop,
        opcodes.Nop,
        opcodes.Nop,
        opcodes.Nop,
        opcodes.Nop,
        opcodes.Nop,
        opcodes.Nop,
        opcodes.Nop,
        opcodes.Nop,
        opcodes.Nop,
        opcodes.Nop
    ])

game = Game()


def patch_features(gameVersion, randomizerFlags):
    patchList = []

    # Patch Persistent Time
    if randomizerFlags.PersistentTime:
        # Jump to Time Sub
        patchList.append(
            Patch(
                game.PersistentTimePatchRomAdr, 
                game.PersistentTimeCode
            )
        )

        # Modify time
        timeLoByteOperandOffset = 29
        timeHiByteOperandOffset = 34
        timeBytes = int_to_16_le(randomizerFlags.TimeLimit)

        game.PersistentTimeSub[timeLoByteOperandOffset] = timeBytes[0]
        game.PersistentTimeSub[timeHiByteOperandOffset] = timeBytes[1]

        # Time Sub
        patchList.append(
            Patch(
                0xf58b, 
                game.PersistentTimeSub
            )
        )

    # Patch Persistent Energy
    if randomizerFlags.PersistentEnergy:
        # Jump to Energy Sub
        patchList.append(
            Patch(
                game.PersistentEnergyPatchRomAdr, 
                game.PersistentEnergyCode
            )
        )

        # Energy Sub
        patchList.append(
            Patch(0xf5b4, game.PersistentEnergySub)
        )

    # Patch No Warp
    if randomizerFlags.NoMechaGodzillaWarp:
        patchList.append(
            Patch(
                game.NoMechaGodzillaWarpPatchRomAdr,
                game.NoWarpCode
            )
        )

    # Patch No Starting Continues
    if randomizerFlags.NoStartingContinues:
        patchList.append(
            Patch(
                0x1024,
                game.NoStartContinueInstruction
            )
        )

    # Patch No Added Continues
    if randomizerFlags.NoAddedContinues:
        patchList.append(
            Patch(
                0x3e52,
                game.NoAddedContinueInstruction
            )
        )

        patchList.append(
            Patch(
                0x3e5d,
                game.NoAddedContinueInstruction
            )
        )
    
    # Patch Persistent Inventory
    if randomizerFlags.PersistentInventory:
        patchList.append(
            Patch(
                0xcd67,
                game.PersistentInventory
            )
        )


    return patchList