import sys, graph, descente, coloration1, coloration2

def run_descente_best1move():
    if len(sys.argv) != 4:
        print("Usage: python main2.py filename iter_max nbcol")
        exit(0)
    filename = sys.argv[1]
    iter_max = int(sys.argv[2])
    k0 = int(sys.argv[3])
    g = graph.read_dimacs(filename)
    sol0 = None
    if k0 > 0 :
        # on fixe un nombre de couleur et on essaye de trouver une colortion valide
        sol0 = coloration2.random_coloration(g, k0)
    else:
        # on trouve une coloration valide
        ordre = list(range(g.n))
        sol0 = coloration1.greedy_coloration(ordre, g)
        k0 = max(sol0) + 1
    print('Nombre initial de couleur :', k0)
    sol, k = coloration2.descente_coloration(g, sol0, iter_max)
    print("Fin de la descente : coloration a {} couleurs trouvée (nb conflits = {})\n{}".format(k, coloration2.count_conflits(sol, (g,k)), sol))


if __name__ == "__main__":
    run_descente_best1move()
