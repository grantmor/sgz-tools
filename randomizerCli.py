import sys
from sgzGame import *
from randomizeGame import *


def arg_to_bool(value):
    #argValue = None
    argLower = value.lower()

    if argLower == 'true':
        argValue = True
    elif argLower == 'false':
        argValue = False
    
    return argValue
    

def arg_to_int(value):
    argInt = int(value)
    return argInt


def process_args():
    # Set defaults
    timeLimit = 768
    randomizeMaps = True
    persistentEnergy = True
    persistentTime = True
    #
    persistentInventory = True
    noEnemySpawnCritical = True
    noEnemySpawnEvent = True
    noMechaGodzillaWarp = True
    noStartingContinues = True
    noAddedContinues = True
    output = 'SuperGodzillaRandomizerPatch.ips'


    args = sys.argv[1:]

    for arg in args:
        # Validate input later
        param, value = arg.split('=')
        param = param.lower()
        
        if param == 'tl':
            timeLimit = arg_to_int(value)
        elif param == 'rm':
            randomizeMaps = arg_to_bool(value)
        elif param == 'pe':
            persistentEnergy = arg_to_bool(value)
        elif param == 'pt':
            persistentTime = arg_to_bool(value)
        elif param == 'pi':
            persistentInventory = arg_to_bool(value)
        elif param == 'nesc':
            noEnemySpawnCritical = arg_to_bool(value)
        elif param == 'nese':
            noEnemySpawnEvent = arg_to_bool(value)
        elif param == 'nmgw':
            noMechaGodzillaWarp = arg_to_bool(value)
        elif param == 'nsc':
            noStartingContinues = arg_to_bool(value)
        elif param == 'nac':
            noAddedContinues = arg_to_bool(value)
        elif param == 'out':
            output = value



    randomizerFlags = RandomizerFlags(
        timeLimit,
        randomizeMaps,
        persistentEnergy,
        persistentTime,
        persistentInventory,
        noEnemySpawnCritical,
        noEnemySpawnEvent,
        noMechaGodzillaWarp,
        noStartingContinues,
        noAddedContinues
    )

    print(randomizerFlags)
    randomize_game('us11', randomizerFlags, output)

process_args()