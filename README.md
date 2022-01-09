# SGZ Tools
Tools for hacking, editing, and randomizing Super Godzilla for the SNES, including a proof-of-concept randomizer.

## Library Fuctionality
+ Terrain/Event and Enemy layer map data compression routines
+ Data structures and constants specifying values used by the game engine for tiles, enemy units, palettes, and 6502 family opcodes and instructions necessary to disable MechaGodzilla warping in Stage 2 and implement the persistent campaign
+ Functions to patch random maps, starting locations and stats

## Randomizer Features and Options
+ Procedurally generated maps created with Perlin noise
+ Persistent Campaign - Energy and Time will not regenerate between stages

## Dependencies
+ Python v3.10
 + Install the perlin_noise module:
```
pip install perlin_noise
```

## Installation and Execution
```sh
git clone https://github.com/grantmor/sgz-tools.git
cd sgz-tools
python ./randomizerGui.py
```
NOTE: If you receive an error message similar to:
```
ImportError: cannot import name 'Iterable' from 'collections' (<filename>)
```
This issue can be worked around by changing the import line in the perlin_noise.py file you installed earlier to refer to 'collections.abc' in place of 'collections'