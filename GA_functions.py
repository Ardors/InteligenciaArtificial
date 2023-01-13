import numpy
import pygad
import pygad.nn
import pygad.gann
import subprocess
import os


def init_game():
    """Initialize player inventory, equipment and other things"""
    return({}, {})

def play_game(GANN_instance, solution, sol_idx):
    player, inventory, solution_fitness = init_game()
    launch_game()
    Inputs = getDataFromGame()
    while gameIsOn():
        predictions = pygad.nn.predict(last_layer=GANN_instance.population_networks[sol_idx],
                                    data_inputs=Inputs)
        sendPredictionToGame(predictions)
        Inputs = getDataFromGame()
        solution_fitness = updateFitness(solution_fitness, Inputs)
    return solution_fitness

def launch_game():
    #launch server
    cmd_line = "gnome-terminal -x bash -c \"bin/rogue; exec bash\""
    os.system(cmd_line)

def getDataFromGame():
    