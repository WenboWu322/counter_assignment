import sys, graph, descente, coloration1
from coloration1 import Voisinage

def run_descente_swap_ordre():
    if len(sys.argv) != 4:
        print("Usage: python main1.py filename iter_max swap\n\t with swap in [1=\"successif\", 2=\"deplacer\", 3=\"inverser\", 4=\"2-opt\"]")
        exit(0)
    filename = sys.argv[1]
    iter_max = int(sys.argv[2])
    swap_in = int(sys.argv[3])
    swap = Voisinage(swap_in)
    g = graph.read_dimacs(filename)
    ordre = list(range(g.n))
    sol0 = coloration1.greedy_coloration(ordre, g)
    k0 = max(sol0) + 1
    print('Nombre initial de couleurs :', k0)
    ordre, k = coloration1.descente_coloration(ordre, g, iter_max, swap)
    col = coloration1.greedy_coloration(ordre, g)
    k = max(col) + 1
    print("Fin de la descente : coloration à {} couleurs trouvée\n{}".format(k, col))

if __name__ == "__main__":
    run_descente_swap_ordre()
