# counter_assignment
This project is for counter assignment task for the airlines to deal with the situations with a large number of arrival aircrafts.
The organization of flight operations at major airports is a difficult exercise. This difficulty is mainly due to the fact that several types of resources are limited and must be allocated efficiently in order to maximize airport capacity. These resources include check-in counters, through which passengers must pass to drop off their luggage and receive their boarding pass. In this project, we will focus on the problem of check-in counter allocation.

The solution of this problem consists of two main steps: 
1) a simplified problem, using integer linear programming 
2) a transition to a heuristic algorithm to solve complex cases and consider more restrictions.

The folder algo contains mainly the functions and modules used, and the folder instances contains some examples for testing.

Some key modules are used, including ccap.py, coloration.py and descente.py etc.

A Python module is provided (ccap.py), containing classes and methods allowing in particular :
- the reading of instance files;
- the manipulation in Python of the information about the instance and its flights;
- the calculation of the cost of the solutions;
- the validation of the respect of the constraints by a solution;
- the graphical display of a solution.

The graph.py module describes the graph structure used. Then there are two versions of the coloring, with for each of them a module coloringi.py which implements the descent, and a main file maini.py which allows to launch the program on an instance.

The results folder contains some visualization of the results for some test examples.
