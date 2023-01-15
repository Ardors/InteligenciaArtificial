import tensorflow.keras
import tensorflow as tf


def createModel():
    numLay1 = 13955
    numLay2 = 1000
    numLay3 = 1000
    numLay4 = 100
    numLay5 = 25
    numNodes = [numLay1, numLay2, numLay3, numLay4, numLay5]


    input_layer  = tensorflow.keras.layers.Input(shape=(1,))
    dense_layer1 = tensorflow.keras.layers.Dense(numLay2, activation="sigmoid")
    #dense_layer2 = tensorflow.keras.layers.Dense(numLay3, activation="sigmoid")
    dense_layer3 = tensorflow.keras.layers.Dense(numLay4, activation="relu")
    output_layer = tensorflow.keras.layers.Dense(numLay5, activation="softmax")

    model = tensorflow.keras.Sequential()
    model.add(input_layer)
    model.add(dense_layer1)
    #model.add(dense_layer2)
    model.add(dense_layer3)
    model.add(output_layer)
    print(model.summary)

    return [model, numNodes]