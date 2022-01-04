from dataclasses import dataclass
from sgzConst import *

class Event:
    def __init__(self, eventType, payload, col, row, terrainMod):
        self.first = 0x02
        self.type = eventType
        self.payload = payload
        self.col = col
        self.row = row

        self.pen = 0xf1
        self.last = 0x00

        self.noTerrainModification = terrainMod


class Stage:
    def __init__(self, stage, version): 

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

                self.playerMaxEnergy = 600
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


@dataclass(frozen=True)
class SuperBank:
    xPos: int
    yPos: int


@dataclass(frozen=True)
class MapParameters:
    horizontalStretchFactor: int
    noiseFrequency: int
    numItems: int
    numResupplies: int
    numTraps: int
    numEnemies: int
    numWarps: int

tiles = Tiles()
events = Events()
items = Items()
enemies = Enemies()
palettes = Palettes()
engine = Engine()