
class Graph:
    '''Représentation de graphes G = (V, E) non orientés, non pondérés.

    La représentation utilise des listes d'adjacence.
    Les sommets sont numérotés de 0 à |V| - 1.
    '''
    def __init__(self, n):
        self.v = [i for i in range(n)]    # int list : liste des sommets
        self.e = []                       # (int, int) list : liste de arêtes
        self.n = n                        # int : nombre de sommets
        self.m = 0                        # int : nombre d'arêtes
        self.adj = [[] for _ in range(n)] # int list list : liste pour chaque sommet des sommets voisins

    def add_edge(self, i, j):
        '''Ajout d'une arrête au graphe.'''
        self.e.append((i, j))
        self.adj[i].append(j)
        self.adj[j].append(i)
        self.m += 1

def read_dimacs(filename):
    '''Renvoie un Graph à partir d'un fichier texte au format DIMACS.'''
    graph = None
    with open(filename) as f:
        for line in f:
            data = line.strip().split()
            if len(data) > 1 and data[0] != "c":
                if data[0] == "p":
                    graph = Graph(int(data[2]))
                if data[0] == "e":
                    v1 = int(data[1]) - 1
                    v2 = int(data[2]) - 1
                    graph.add_edge(v1, v2)
    return graph
