import tensorflow.keras
import numpy as np
import modelKeras
import GA_functions

"""numLay1 = 2
numLay2 = 6
numLay3 = 2
numNodes = [2, 6, 2]

data_inputs = np.array([[0, 0],
                           [0, 1],
                           [1, 0],
                           [1, 1]])

input_layer  = tensorflow.keras.layers.Input(numLay1)
dense_layer = tensorflow.keras.layers.Dense(numLay2, activation="relu")
output_layer = tensorflow.keras.layers.Dense(numLay3, activation="softmax")

model = tensorflow.keras.Sequential()
model.add(input_layer)
model.add(dense_layer)
model.add(output_layer)"""

[model, numNodes] = modelKeras.createModel()

weights = []
text_file = open("bestSolution.txt", "r")
lines = text_file.readlines()
for element in lines:
    weights.append(float(element[:-3]))         #removing the last decimals are they are not significant

"""bestSol = []
temp = []
for i in range(numLay1):                                                                #adding the weights of the first layer
    temp.append(weights[i*numLay2:(i+1)*numLay2])
bestSol.append(np.array(temp))
temp = []
bestSol.append(np.array(weights[numLay1*numLay2 : numLay1*numLay2 + numLay2]))          #biases of the first hidden layer
for i in range(numLay2):                                                                #adding the weights of the second layer
    temp.append(weights[numLay1*numLay2 + numLay2 + i*numLay3 : numLay1*numLay2 + numLay2 + (i+1)*numLay3])
bestSol.append(np.array(temp))
temp = np.array([])
bestSol.append(np.array(weights[numLay1*numLay2 + numLay2 + numLay2*numLay3 : numLay1*numLay2 + numLay2 + numLay2*numLay3 + numLay3]))      #biases of the output layer
print(bestSol)"""


bestSolBis = []
tempBis = []
"""for i in range(numLay1):                                                                #adding the weights of the first layer
    tempBis.append(weights[i*numLay2:(i+1)*numLay2])
bestSolBis.append(np.array(tempBis))
tempBis = []
bestSolBis.append(np.array(weights[numLay1*numLay2 : numLay1*numLay2 + numLay2]))          #biases of the first hidden layer"""
for j in range(len(numNodes)-1):
    tempBis = []
    for i in range(numNodes[j]):      
        offset = 0                                                              #adding the weights of the second layer
        for k in range(j):
            offset += numNodes[k]*numNodes[k+1] + numNodes[k+1]                   #offset of the previous weights + the previous biaises
        tempBis.append(weights[offset + i*numNodes[j+1] : offset + (i+1)*numNodes[j+1]])
    bestSolBis.append(np.array(tempBis))
    bestSolBis.append(np.array(weights[offset + numNodes[j]*numNodes[j+1] : offset + numNodes[j]*numNodes[j+1] + numNodes[j+1]]))      #biases of the output layer
print(bestSolBis)


"""weights = model.get_weights()
print(weights)"""
model.set_weights(bestSolBis)

solution_fitness = play_game_Example(model)
print("Fitness de este partido: ", solution_fitness)


def play_game_Example(model):
    [player, inventory, solution_fitness] = GA_functions.init_game()
    GA_functions.launch_game()
    [Inputs, inventory, player, dungeon] = GA_functions.getInputData(inventory, player)
    nbCelulasAnterior = 0
    nbCelulasCurrent = 0
    [solution_fitness, nbCelulasCurrent, nbCelulasAnterior] = GA_functions.computeFitness(player, inventory, dungeon, nbCelulasCurrent, nbCelulasAnterior)   #computing fitness function here to initialize nCelulasCurrent
    while GA_functions.gameIsOn(player):
        """predictions = pygad.nn.predict(last_layer=GANN_instance.population_networks[sol_idx],
                                    data_inputs=Inputs)"""
        predictions = model.predict(Inputs)
        GA_functions.processPrediction(predictions, inventory)
        [Inputs, inventory, player, dungeon] = GA_functions.getInputData(inventory, player)
        [solution_fitness, nbCelulasCurrent, nbCelulasAnterior] = GA_functions.computeFitness(player, inventory, dungeon, nbCelulasCurrent, nbCelulasAnterior)
    return solution_fitness



#yhat = model.predict(data_inputs)
#print(yhat)