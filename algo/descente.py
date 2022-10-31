def descente_plateau(sol, feval, getneighbor, iter_max, env, display=False):
    '''Schéma de descente avec plateau

    Paramètres :
    - sol : la solution initiale (type à définir par l'utilisateur)
    - feval : fonction d'évaluation, de type (sol, env) -> cost (type cost à définir par l'utilisateur, int ou float)
    - getneighbor : fonction qui renvoit une solution voisine, de type (sol, env) -> (sol, cost)
    - iter_max : le nombre maximum d'iterations sans amélioration (int)
    - env : données de l'environnement du problème (type à définir par l'utilisateur)
    - display : affiche (ou non) l'évolution du coût à chaque itération (bool)

    Valeurs renvoyées :
    - sol : la solution à la fin de la descente
    - cost : le coût de la solution renvoyée
    '''
    cost = feval(sol, env)
    i, improve = 0, 0
    while i < improve + iter_max:
        sol_p, cost_p = getneighbor(sol, env)
        if cost < cost_p: break # on termine si on n'améliore pas
        else:
            i += 1
            if display: print("iter {}: {}".format(i, cost), end="\r")
            if cost_p < cost:
                improve = i
            sol, cost = sol_p, cost_p
    return (sol, cost)
