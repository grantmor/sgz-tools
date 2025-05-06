from dataclasses import dataclass


@dataclass(frozen=True)
class Tiles:
    Sea = 0xeb
    DeepSea = 0xec

    Ground = 0xf1 # Deprecated, use specific ground types
    UrbanGround = 0xf1
    RuralGround = 0xf5
    SpecialGround = 0xfb

    Building = 0xf0
    SkyScraper = 0xf2
    
    Rubble = 0xf3 # Also F7

    Mountain = 0xf4
    RockyMountain = 0xf6
    
    PowerCableV = 0xf8
    PowerTowerH = 0xf9
    PowerTower = 0xfa

    Mothership = 0xea

    ItemPoint = 0xed
    ResupplyBase = 0xee
    AreaPoint = 0xef
    SpecialEnergy = 0xfc
    
    Warp = 0xed # Same as Item though?


@dataclass(frozen=True)
class Enemies:
    Mine = 0xe8
    Tank = 0xe0
    Missle = 0xe4
    Destroyed = 0xe9


@dataclass(frozen=True)
class Events:
    EnergyResupply = 0x00
    Trap = 0x01
    Message = 0x02
    Item = 0x03

    MinVal = 0x00
    MaxVal = 0x03


@dataclass(frozen=True)
class Items:
    FightingSpirit = 0x00
    DefenseItem = 0x01
    EnergyRefill = 0x03
    SuperRefill = 0x02

    EnergyResupply = 0x0a

    EnergyCapsule = 0x04
    Invincibility = 0x05

    Warp = 0x06

    StopTime = 0x07
    Message = 0x08

    MinVal = 0x00
    MaxVal = 0x08


@dataclass(frozen=True)
class Palettes:
    # Deprecated, use Gray or Green instead
    Map = 0x1c
    
    Gray = 0x1c
    Green = 0x07

    Enemy = 0x06
    Blue = 0x00
    Yellow = 0x0c
    Orange = 0x01
    UFO = 0x04


# Engine constants
@dataclass(frozen=True)
class Engine:
    RowHeaderLength = 3
    TilePalettePairLength = 2
    MaxZones = 8
    RowsPerZone = 8
    TilesInRow = 20
    RegionsInZone = 2

    StepsInTile = 8

    SameTile = 0x00
    NewTile = 0x01


# Instantiate "enums"
tiles = Tiles()
enemies = Enemies()
events = Events()
items = Items()
palettes = Palettes()
engine = Engine()
