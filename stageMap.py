from dataclasses import dataclass

@dataclass(frozen=True)
class MapParameters:
    horizontalStretchFactor: int
    noiseFrequency: int
    numItems: int
    numResupplies: int
    numTraps: int
    numEnemies: int
    numWarps: int
