import tensorflow.keras



def createModel():
    numLay1 = 13955
    numLay2 = 1000
    numLay3 = 1000
    numLay4 = 100
    numNodes = [numLay1, numLay2, numLay3, numLay4]


    input_layer  = tensorflow.keras.layers.Input(numLay1)
    dense_layer = tensorflow.keras.layers.Dense(numLay2, activation="sigmoid")
    dense_layer = tensorflow.keras.layers.Dense(numLay3, activation="relu")
    output_layer = tensorflow.keras.layers.Dense(numLay4, activation="softmax")

    model = tensorflow.keras.Sequential()
    model.add(input_layer)
    model.add(dense_layer)
    model.add(output_layer)
    return [model, numNodes]