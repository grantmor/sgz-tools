from dataclasses import dataclass

@dataclass(frozen=True)
class MapParameters:
    horizontalStretchFactor: int
    noiseFrequency: int
    numEvents: int
    numEnemies: int
