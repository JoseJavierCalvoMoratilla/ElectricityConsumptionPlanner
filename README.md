# ElectricityConsumptionPlanner
Genetic algorithms for planning electricity consumption in a house with basic electrification.

Each device has an assigned ID:
| ID | Devices |
| ------------- | ------------- |
| 0  | Horno |
| 1  | Cocina  |
| 2  | Lavadora |
| 3  | Secadora |
| 4  | Termo  |
| 5  | Lavavajillas |
| 6  | Aire  |
| 7  | Microondas |
| 8  | Tostadora  |
| 9  | Máquina de café  |


Initial configuration is defined:
| Configuration |
| ------------- | 
| Electricifación básica 5,750 KW  |
| Cuatro franjas por hora  |
| Tareas simultáneas  | 


Each device has an instantaneous consumption in watts with an average duration:
| Device | W | Tiempo de uso medio |
| ------------- | ------------- | ------------- |
| Horno | 1200 | 0.75 |
| Cocina  | 1000 | 0.75 |
| Nevera  | 120 | 24 |
| Congelador | 120 | 24 |
| Lavadora | 800 | 1.5 |
| Secadora | 3000 | 1 |
| Termo  | 4500 | 2 |
| Lavavajillas | 1300 | 1.5 |
| Aire  | 3250 | 5 |
| Microondas | 1000 | 0.5 |
| Tostadora  | 850 | 0.1 |
| Máquina de café  | 800 | 0.1 |


The price per time slot supplied by the electric company is defined:
| Hour | price (€) |  Hour | price (€) |
| ------------- | ------------- | ------------- | ------------- |
| 0 | 0.16364 | 12 | 0.20769 |
| 1  | 0.16165 | 13 | 0.19385 |
| 2  | 0.15442 | 14 | 0.17929 |
| 3 | 0.15414 | 15 | 0.1784 |
| 4 | 0.15362 | 16 | 0.18255 |
| 5 | 0.16287 | 17 | 0.20195 |
| 6  | 0.18831 | 18 | 0.23366 |
| 7 | 0.22118 | 19 | 0.25676 |
| 8  | 0.2464 | 20 | 0.25938 |
| 9 | 0.2464 | 21 | 0.25534 |
| 10  | 0.22257 | 22 | 0.22141 |
| 11  | 0.21475 | 23 | 0.22141 |

Solution format (Array 1 dimension):
| 18 | 21 |  23 | 2 | 11 |
| ------------- | ------------- | ------------- | ------------- | ------------- |

Task selected:
| 2 | 6 |  2 | 1 | 3 |
| ------------- | ------------- | ------------- | ------------- | ------------- |

In the solution array each column corresponds to a specific task and the content is the time to connect a device.
The tasks are grouped in a task array and identify each of the columns of the problem solution.


# 1. Genetic algorithm

# 2. Simulated annealing
