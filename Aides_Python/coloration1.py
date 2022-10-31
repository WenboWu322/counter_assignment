import graph, numpy, random, descente
from enum import Enum, auto

######################################################################
# Descente
#
# Espace de recherche : ensemble des colorations valides (sans arêtes en conflit)
# Fonction objectif : minimiser le nombre de couleurs
# Environement : graphe
# Voisinage : les sommets sont ordonnés puis coloriés 1 à 1 avec la plus
#             petite couleur possible (fonction greedy_coloration)
#             Les voisinages consistent à modifier l'ordre des sommets
#             Il y a 4 voisinages :
#               - "successif"
#                   => l'ordre de 2 sommets successifs ont été inversés
#               - "deplacer"
#                   => un sommet a été déplacé à une autre position
#               - "inverser"
#                   => l'ordre de 2 sommets ont été inversés
#               - "2-opt"
#                   => la séquence de entre 2 sommets a été retournée
########################################################################

class Voisinage(Enum):
    SUCCESSIF = auto()
    DEPLACER = auto()
    INVERSER = auto()
    DEUXOPT = auto()

def greedy_coloration(ordre, g):
    '''Renvoie une coloration valide.

    On attribue la plus petite couleur possible aux sommets en les
    considérant dans l'odre du paramètre [ordre].

    Paramètres :
    - ordre : ordre des sommets à colorier (int list)
    - g : graphe à colorier (Graph)

    Renvoie :
    - sol : la couleur (entier) de chaque sommet (int list)
    '''
    sol = [None] * g.n
    sol[ordre[0]] = 0
    for i in ordre[1:]:
        colors = []
        domaine = list(range(g.n))
        for j in g.adj[i]:
            if sol[j] != None and sol[j] not in colors:
                colors.append(sol[j])
                domaine.remove(sol[j])
        sol[i] = min(domaine)
    return sol

def count_nbcol(ordre, g):
    '''Renvoie le nombre de couleurs utilisées par la coloration générée [ordre].'''
    sol = greedy_coloration(ordre, g)
    return max(sol) + 1

def best_swap(ordre, g, swap):
    '''Renvoie la meilleure solution voisine.

    Paramètres :
    - ordre : ordre des sommets à colorier (int list)
    - g : graphe à colorier (Graph)
    - swap : type de voisinange (Voisinage)

    Valeurs renvoyées :
    - ordre_best : meilleur ordre voisin de [ordre] (int list)
    - cost_best : nombre de couleurs utilisée par [ordre_best] (int)
    '''
    col = greedy_coloration(ordre, g)
    cost = max(col) + 1
    cost_best, ordre_best = cost, [j for j in ordre]
    l = list(range(g.n - 1))
    random.shuffle(l)
    for i in l:
        jmax = i+2 if swap == Voisinage.SUCCESSIF else g.n
        p = list(range(i+1, jmax))
        random.shuffle(p)
        for j in p:
            ordre_v = [x for x in ordre]
            if swap == Voisinage.DEPLACER:
                ordre_v = ordre[:i] + ordre[i+1:j+1] + [ordre[i]] + ordre[j+1:]
            if swap == Voisinage.INVERSER:
                ordre_v[i], ordre_v[j] = ordre_v[j], ordre_v[i]
            if swap == Voisinage.DEUXOPT:
                for k in range((j-i+1)//2):
                    ordre_v[i+k], ordre_v[j-k] = ordre_v[j-k], ordre_v[i+k]
            col_v = greedy_coloration(ordre_v, g)
            cost_v = max(col_v) + 1
            if cost_v <= cost_best :
                cost_best = cost_v
                ordre_best = [j for j in ordre_v]
    return ordre_best, cost_best

def descente_coloration(ordre0, g, iter_max, swap):
    '''
    @param ordre0 : int list : ordre/solution initiale (des sommets à colorier)
    @param g : graph : graphe considéré
    @param iter_max : int : nombre d'iteration de la descente sans amélioration
    @param swap : string : swap in ["successif", "deplacer", "inverser", "2-opt"]
    @return ordre_best : int list : meilleur ordre voisin de [ordre]
    @return cost_best : int : nombre de couleurs utilisée par [ordre_best]
    '''
    def voisinage(ordre, g):
        return best_swap(ordre, g, swap)
    return descente.descente_plateau(ordre0, count_nbcol, voisinage, iter_max, g, display=True)
