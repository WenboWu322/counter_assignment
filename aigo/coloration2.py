import graph, numpy, random, descente

######################################################################
# Descente
#
# Espace de recherche : ensemble des colorations potentiellement non valides
#                       (avec des arêtes en conflit) et ayant au plus k couleurs
# Fonction objectif : minimiser le nombre d'arêtes en conflits
# Environement : graphe, nombre de couleurs
# Voisinage : best 1-move critique : renvoie le meilleur voisin 1-move critique
#               - 1-move = ensemble des colorations ayant un seul sommet
#                 de couleur différente par rapport à la coloration courante
#               - 1-move critique = sous-ensemble de 1-move, seul les sommets
#                 critiques (ie. impliqués dans une arête en conflit) peuvent
#                 changer de couleur
########################################################################
def conflits(sol, env):
    '''Renvoie le nombre de conflits de la coloration [sol]
    et la liste des sommets impliqués dans un conflits (sommets critiques).'''
    g, _ = env
    cost = 0
    v_conflit = []
    for i,j in g.e:
        if sol[i] == sol[j]:
            cost += 1
            if i not in v_conflit : v_conflit.append(i)
            if j not in v_conflit : v_conflit.append(j)
    return cost, v_conflit

def count_conflits(sol, env):
    '''Renvoie le nombre de conflits de la coloration [sol].'''
    cost, _ = conflits(sol, env)
    return cost

def best_1_move(sol, env):
    '''Renvoie la meilleure solution voisine de [sol]
    pour le voisinage 1-move critique.'''
    g, nbcol = env
    cost, v_conflit = conflits(sol, env)
    cost_best, sol_best = cost, [j for j in sol]
    random.shuffle(v_conflit)
    for i in v_conflit:
        cols = [col for col in range(nbcol) if col != sol[i]]
        random.shuffle(cols)
        for c in cols:
            sol_v = [j for j in sol]
            sol_v[i] = c
            cost_v = count_conflits(sol_v, env)
            if cost_v <= cost_best :
                cost_best = cost_v
                sol_best = [j for j in sol_v]
    return sol_best, cost_best

def descente_k_coloration(sol, nbcol, g, iter_max):
    env = (g, nbcol)
    return descente.descente_plateau(sol, count_conflits, best_1_move, iter_max, env, display=True)

def descente_coloration(g, sol, iter_max):
    solValid = None
    nbcol = max(sol) + 1
    cost = count_conflits(sol, (g, nbcol))
    if cost == 0:
        solValid = [x for x in sol]
    else:
        # lancer le recherche locale à partir de cette solution
        sol, cost = descente_k_coloration(sol, nbcol, g, iter_max)
    while cost == 0:
        # La solution est valide, alors on diminue de 1 le nombre de couleur
        #    et on construit une solution à k-1 couleurs à partir de celle
        #    à k couleurs
        print("Coloration a {} couleurs valide trouvée.".format(nbcol))
        solValid = [x for x in sol]
        nbcol = nbcol-1
        sol_km1 = coloration_init_km1(sol, nbcol)
        sol, cost = descente_k_coloration(sol_km1, nbcol, g, iter_max)
    return solValid, nbcol+1

def random_coloration(g, k):
    return [random.randint(0,k) for _ in range(g.n)]

def coloration_init_km1(sol, k):
    return [random.randint(0,k-1) if ci >= k else ci for ci in sol]
