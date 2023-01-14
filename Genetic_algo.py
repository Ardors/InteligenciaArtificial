import numpy
import pygad
import pygad.nn
import pygad.gann
import GA_functions

def fitness_func(solution, sol_idx):
    global GANN_instance
    solution_fitness = GA_functions.play_game(GANN_instance, solution, sol_idx)
    '''correct_predictions = numpy.where(predictions == data_outputs)[0].size
    solution_fitness = (correct_predictions/data_outputs.size)*100'''

    return solution_fitness

def callback_generation(ga_instance):
    global GANN_instance

    population_matrices = pygad.gann.population_as_matrices(population_networks=GANN_instance.population_networks, 
                                                            population_vectors=ga_instance.population)

    GANN_instance.update_population_trained_weights(population_trained_weights=population_matrices)

    print("Generation = {generation}".format(generation=ga_instance.generations_completed))
    print("Accuracy   = {fitness}".format(fitness=ga_instance.best_solution()[1]))

print("aa")
GANN_instance = pygad.gann.GANN(num_solutions=10,
                                num_neurons_input=13955,    #13955
                                num_neurons_hidden_layers=[1000, 500, 100],
                                num_neurons_output=25,
                                hidden_activations=["relu", "sigmoid", "relu"],
                                output_activation="softmax")

print("bb")
population_vectors = pygad.gann.population_as_vectors(population_networks=GANN_instance.population_networks)
print("cc")
ga_instance = pygad.GA(num_generations=1000, 
                       num_parents_mating=100, 
                       initial_population=population_vectors.copy(),
                       fitness_func=fitness_func,
                       mutation_percent_genes=5,
                       callback_generation=callback_generation,
                       save_best_solutions=True)

ga_instance.run()

ga_instance.plot_fitness()

solution, solution_fitness, solution_idx = ga_instance.best_solution()
print(solution)
print(solution_fitness)
print(solution_idx)