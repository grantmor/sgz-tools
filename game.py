from dataclasses import dataclass

@dataclass(frozen=True)
class RandomizerFlags:
    PersistentEnergy: bool
    PersistentTime: bool
    NoEnemySpawnCritical: bool
    NoEnemySpawnEvent: bool
    NoMechaGodzillaWarp: bool

@dataclass(frozen=True)
class Game:
    PersistentTimePatchRomAdr: int = 0x00d05d
    PersistentEnergyPatchRomAdr: int = 0x00d0b3
    NoMechaGodzillaWarpPatchRomAdr: int = 0x00c6df

    # Instead of patching these completely out like this,
    # Jump to a subroutine that initializes health, time,
    # etc. if it's zero

    PersistentTimeCode = bytearray([
        0x4c,
        0x6a,
        0xd0
    ])

    PersistentEnergyCode = bytearray([
        0x4c,
        0xc1,
        0xd0
    ])

    NoWarpCode = bytearray([
        0x4c,
        0x32,
        0xc7
    ])

game = Game()

def patch_features(romPath, pTime, pEnergy, noWarp):
    rom = open(romPath, 'r+b')

    # Patch Persistent Time
    if pTime:
        rom.seek(game.PersistentTimePatchRomAdr)
        rom.write(game.PersistentTimeCode)

    # Patch Persistent Energy
    if pEnergy:
        rom.seek(game.PersistentEnergyPatchRomAdr)
        rom.write(game.PersistentEnergyCode)

    # Patch No Warp
    if noWarp:
        rom.seek(game.NoMechaGodzillaWarpPatchRomAdr)
        rom.write(game.NoWarpCode)

    rom.close()