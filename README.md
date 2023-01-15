# VisionArtificial
Estos programas se han desarollado en y para un entorno Linux con Python 3.8.10. Se puede que otras versiones de Python funcionen pero no aseguramos nada. 

Requirements de modulos Python:
tensorflow==2.11.0
numpy==1.20.1
pygad==2.18.1

Es importante tener el modulo numpy en la version specificada por compatibilidad entre PyGAD y Tensorflow. 

Se puede requirir de compilar el juego con el Makefile. Si no existe la carpeta /bin o si esta vacia, ejecutar el comando
$ make
para compilar los archivos C del juego y generar el ejecutable. 

El modulo apt gnome-terminal es necesario para correr los diferentes agentes. 
Se puede instalar en un entorno GNU/Linux con el comando
$ sudo apt-get install gnome-terminal

Para correr el programa de entrenamiento de la red, solo hay que ejecutar el archivo main.py. Si una de las simulaciones parece pillada, no dudar el Ctrl+C en el terminal de main.py, es normal y pasa al siguiente individuo. 

Cuando se acaba el entrenamiento se genera un archivo bestSolution.txt, que contiene los pesos de la red que tiene el mejor valor de fitness del entrenamiento. 

Esos pesos se pueden luego aplicar a una red de misma arquitectura lanzando el programa runExample.py. Este programa lee los pesos que estan escritos en bestSolution.txt y les utiliza para hacer predicciones del juego de Rogue. Asi se pueden probar muchas redes "a mano", si han sido selecionadas previamente. 