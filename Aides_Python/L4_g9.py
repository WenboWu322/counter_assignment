
import pulp
import numpy as np
import matplotlib.pyplot as plt
import sys
import signal

from ccap import *
import re

# print("Vol\t TKO\t nombre de comptoirs requis")
#
# print(instance._flights[0])

# df = pd.pandas.read_csv('../Instances/instance_04_12_1.csv')
# pd.set_option('display.max_columns',None)
# pd.set_option('display.max_rows',None)
# print(df)
# #df.drop('na',axis=1, inplace=True)

"""def timelimit(tml):
    def alarm(*_):
        raise SystemExit("time out!")
    signal.signal(signal.SIGALRM,alarm)
    signal.alarm(int(tml))"""


instance = Instance.from_file('../Instances/instance_10_20_2.csv')
l_rangee = [i for i in range(instance.rows)]  # liste des rangées numérotées  a partir de 0
nb_rangees = instance.rows  # nombre total de rangées dans l'aérogare
nb_compt_r = instance.booths // nb_rangees
V = instance._flights

def solve():
    print(sys.argv)

    tml = sys.argv[1]
    prob = pulp.LpProblem("modele_1", pulp.LpMinimize)
    instance = Instance.from_file(sys.argv[2])

    for f in instance:
        print("{}\t {}\t {}".format(f.callsign, f.tko, f.booths))

    V = instance._flights

    nbVariables1 = len(V)
    indices1 = list(range(nbVariables1))

    N = 0
    for i in range(nbVariables1):
        N += V[i].booths
    print(N)

    E = []
    S = []

    O = [V[i].opening.tm for i in range(len(V))]
    F = [V[i].closing.tm for i in range(len(V))]
    T = [V[i].tko.tm for i in range(len(V))]
    pref = [V[i].preferences for i in range(len(V))]  # liste des rangées preferees par la comp pour le vol i
    print(pref)
    l_rangee = [i for i in range(instance.rows)]  # liste des rangées numérotées  a partir de 0
    nb_rangees = instance.rows  # nombre total de rangées dans l'aérogare
    nb_compt_r = instance.booths // nb_rangees
    # nombre de comptoirs par rangée
    print("liste des rangees", l_rangee)
    print("nombre de rangees :", nb_rangees)
    print("nb compt par rangee :", nb_compt_r)
    # definition de la matrice des couts et de l'ensemble vol / rangee

    mat_couts = np.ones((len(V), nb_rangees), int)
    for l in range(len(mat_couts)):  # l est un indice de vol
        print("numero ligne :", l, "pref :", pref[l])
        for colonne in range(nb_rangees):  # colonne est un in dice de rangee
            if colonne in pref[l]:
                mat_couts[l, colonne] = 0
    B = [(i, r) for i in range(len(V)) for r in l_rangee]
    print("matrice :", mat_couts)
    print("ens b :", B)

    # definition des ensembles incompatibles
    for i in range(len(V)):
        for j in range(len(V)):
            if i != j and O[j] < F[i] and F[j] > O[i]:
                E.append((i, j))
            if i != j and T[i] <= T[j] and F[i] <= O[j] < T[i]:
                S.append((i, j))

    P = pulp.LpVariable.dicts("P", indices1, lowBound=1, cat="Integer")  # le plus petit comptoir associé à un vol i

    R = pulp.LpVariable.dicts("R", indices1, lowBound=1, cat="Integer")  # le comptoir qui reste ouvert

    Y = pulp.LpVariable.dicts("Y", E, lowBound=0, cat="Binary")  # ordonnancement des plus petits comptoirs

    r = pulp.LpVariable.dicts("r", S, lowBound=0, cat="Binary")
    z = pulp.LpVariable.dicts("z", S, lowBound=0, cat="Binary")
    x = pulp.LpVariable.dicts("x", B, lowBound=0, cat="Binary")

    for i in range(nbVariables1):
        prob += sum([x[i, r] for r in l_rangee]) == 1
        prob += nb_compt_r * (sum([x[i, r] * r for r in l_rangee])) + 1 <= P[i]

        prob += P[i] + V[i].booths - 1 <= nb_compt_r * (sum([x[i, r] * r for r in l_rangee]) + 1)
        prob += P[i] - R[i] <= 0
        prob += R[i] - P[i] - V[i].booths + 1 <= 0

    for e in E:
        prob += P[e[1]] + V[e[1]].booths - instance.booths * (1 - Y[e[0], e[1]]) <= P[e[0]]
        prob += Y[e[0], e[1]] + Y[e[1], e[0]] == 1

    for s in S:
        prob += R[s[0]] - instance.booths * (1 - z[s[0], s[1]]) <= P[s[1]] - 1
        prob += R[s[0]] + instance.booths * (1 - r[s[0], s[1]]) - V[s[1]].booths >= P[s[1]]
        prob += z[s[0], s[1]] + r[s[0], s[1]] == 1
    # print(mat_couts[i,r])
    prob += sum([mat_couts[i, r] * x[i, r] for r in l_rangee for i in range(len(V))])  # FONCTION OBJECTIVE

    prob.solve(pulp.GLPK_CMD(msg=1, options=["--tmlim", "{}".format(tml)]))

    print("Statut:", pulp.LpStatus[prob.status])

    val_opt = pulp.value(prob.objective)
    print("valeur optimale :", val_opt)
    for i in range(len(V)):
        for r in l_rangee:
            print("x pour i={} et r={}".format(i, r), x[i, r].varValue)
    P = [P[i].varValue for i in range(nbVariables1)]
    print('liste du 1er comptoir de chaque vol: ', P)
    R = [R[i].varValue for i in range(nbVariables1)]
    print('liste du comptoir qui reste ouvert: ', R)
    # for [i,j] in E:
    # print("couple {} - {}".format(i,j),Y[i, j].varValue)

    #     for i,ti in enumerate(t_opt):
    #         print("t_{} = {}".format(i, ti))
    #     print("Fonction objectif optimale = ", val_opt)
    #     print("t_opt = t_opt)
    #     display(t_opt, e, c, l)

    # print(P[13], "P3 :",P[3], "C3 :",V[3].booths)
    # print(P)
    first = []
    """regexpr_first = r"^P_*"
    for v in prob.variables():
        if re.match(regexpr_first,str(v.name)) is not None:
            first.append(v.varValue-1)

    print(first)"""
    instance.solution([p - 1 for p in P], [r - 1 for r in R])
    instance.validate()
    instance.draw()
    instance._validate_overflow()
    instance._validate_conflicts()
    instance._validate_last()
    instance._validate_rows()

    return P, O, F


# P, O, F = solve()
# print(P, O, F)

color = ['orange', 'skyblue', 'darkolivegreen', 'crimson', 'seagreen', 'maroon', 'yellow', 'blue', 'red', 'green']


def display(P, O, T, V):
    print(max(T))
    axes = plt.gca()
    axes.set_xlim(min(O), max(T))
    c = [i.booths for i in V]
    print(c)
    for i in range(len(V)):
        print(i)
        for ic in range(0, c[i]):
            print("premier comptoir :", P[i])
            plt.plot([O[i], T[i]], [P[i] + ic, P[i] + ic], color[i])
    #
    plt.xlabel("temps")
    plt.ylabel("comptoirs")
    plt.show()


def get_solution_init():
    # instance = Instance.from_file('../Instances/instance_10_20_2.csv')

    for f in instance:
        print("{}\t {}\t {}".format(f.callsign, f.tko, f.booths))

    V = instance._flights

    E = []
    S = []

    O = [V[i].opening.tm for i in range(len(V))]
    F = [V[i].closing.tm for i in range(len(V))]
    T = [V[i].tko.tm for i in range(len(V))]
    pref = [V[i].preferences for i in range(len(V))]  # liste des rangées preferees par la comp pour le vol i
    print(pref)
    # l_rangee = [i for i in range(instance.rows)]  # liste des rangées numérotées  a partir de 0
    # nb_rangees = instance.rows  # nombre total de rangées dans l'aérogare
    # nb_compt_r = instance.booths // nb_rangees
    # nombre de comptoirs par rangée

    print("liste des rangees", l_rangee)
    print("nombre de rangees :", nb_rangees)
    print("nb compt par rangee :", nb_compt_r)

    # definition des ensembles incompatibles
    for i in range(len(V)):
        for j in range(len(V)):
            if i != j and O[j] < F[i] and F[j] > O[i]:
                E.append((i, j))
            if i != j and T[i] <= T[j] and F[i] <= O[j] < T[i]:
                S.append((i, j))
                S.append((j, i))

    Rvol = []
    P = [0] * len(V)
    for r in l_rangee:
        # print(r)
        L = []
        for v in V:
            # print(v)
            # print(v.preferences)
            if v.preferences[0] == r:
                L.append(v)
        Rvol.append(L)
    print("rvol :", Rvol)
    # T = [V[i].tko.tm for i in range(len(V))]
    # liste des vols deja triee par ordre croissant de to
    compt = 0

    D = [i * nb_compt_r + 1 for i in l_rangee]  # liste du premier comptoir dispo par rangée

    Fic = nb_rangees * nb_compt_r + 1  # le premier comptoir dispo dans la rangée imaginaire soit le nombre total de comptoirs + 1 à l'initialisation

    for L in Rvol:
        iprec = L[0]
        for j, i in enumerate(L):
            print(i)
            if j == 0:
                P[i.uid] = D[i.preferences[0]]
                D[i.preferences[0]] = P[i.uid] + i.booths

            last_c = nb_compt_r * (i.preferences[0] + 1)
            if j != 0:

                if (i.uid, iprec.uid) in E or (i.uid, iprec.uid) in S:
                    if (i.uid, iprec.uid) in E:  # or (i.uid, iprec.uid) in S:
                        if last_c - D[
                            i.preferences[0]] + 1 >= i.booths:  # and (i.uid, iprec.uid) in E and (i, iprec.uid) in S:
                            P[i.uid] = D[i.preferences[0]]
                            D[i.preferences[0]] = P[i.uid] + i.booths
                        else:
                            P[i.uid] = Fic
                            Fic = P[i.uid] + i.booths
                            compt = compt + 1
                    if (i.uid, iprec.uid) in S:
                        P[i.uid] = P[iprec.uid] + 1
                        D[i.preferences[0]] = P[i.uid] + i.booths

                elif last_c - i.preferences[
                    0] * nb_compt_r + 1 >= i.booths:  # elif last_c-D[i.preferences[0]]+1 >= i.booths:
                    P[i.uid] = P[iprec.uid]
                elif last_c - i.preferences[0] * nb_compt_r + 1 < i.booths:
                    P[i.uid] = F
                    Fic = P[i.uid] + i.booths
                    compt = compt + 1
                iprec = i
    Y0 = [P[i] for i in range(len(V))]

    f0 = sum([1 if i.preferences[0] != ((Y0[i] - 1) % nb_compt_r) else 0 for i in V]) + 100 * compt

    # affichage de vols
    display(Y0, O, T, V)

    """instance.solution([p - 1 for p in Y0], [r - 1 for r in Y0])
    instance.validate()
    instance.draw()
    instance._validate_overflow()
    instance._validate_conflicts()
    instance._validate_last()
    instance._validate_rows()"""
    return Y0, f0


Y0, f0 = get_solution_init()
print("solution : ", Y0, f0)

M = nb_compt_r
def glouton(instance, E, S, Y, i, j):  # Y : la liste des 1er comptoirs de chaque vol

    # V = instance._flights

    O = [V[i].opening.tm for i in range(len(V))]
    F = [V[i].closing.tm for i in range(len(V))]
    T = [V[i].tko.tm for i in range(len(V))]
    pref = [V[i].preferences for i in range(len(V))]  # liste des rangées preferees par la comp pour le vol i
    print(pref)
    l_rangee = [i for i in range(instance.rows)]  # liste des rangées numérotées  a partir de 0
    nb_comptoirs = instance.booths
    nb_rangees = instance.rows  # nombre total de rangées dans l'aérogare
    M = instance.booths // nb_rangees  # nb de comptoirs par rangée

    dep = 0
    chev_Rg = 0
    chev_E = 0
    chev_s = 0
    for e in E:
        if e[0] == i or e[0] == j:
            bool = (Y[e[0]] + V[e[0]].booths <= Y[e[1]] or Y[e[0]] + V[e[1]].booths <= Y[e[0]])
        if bool == False:
            chev_E += 1
    for s in S:
        if s[0] == i or s[0] == j:
            bool = (Y[s[0]] + 1 <= Y[S[1]] or Y[s[1]] + 1 <= Y[s[0]])
        if bool == False:
            chev_s += 1

    if ((Y[i] + V[i].booths - 1) / M) != (Y[i] / M):
        chev_Rg += 1
    if (Y[i] >= nb_comptoirs):
        dep += 1

    f = sum([1 if i.preferences[0] != ((Y[i] - 1) % M) else 0 for i in V] + (chev_E * 100) + (chev_s * 100) + (
            chev_Rg * 50) + (dep * 100))
    return f, Y


def voisinage(instance, E, S, f, Y):
    iter_max = 100
    iter_best = 0
    iter = 0
    while iter < iter_best + iter_max:
        iter += iter
        f_best, Y_best = f, Y
        for i in enumerate(L):
            last_c = M * (i.preferences[0] + 1)

        if iter % 2 == 0:
            for L in get_solution_init.Rvol:
                for i, j in L and (i!=j):

                    Y[i], Y[j] = Y[j], Y[i]
                    Y_prim = Y
        else:
            for L in get_solution_init.Rvol:
                for i,j in L:
                    Y[i] = last_c - V[i].booths  # mettre au plafond de cette rangee
                    if Y[j]>=0 and (Y[j] <= last_c - V[j].booths) and (i not in S):  #1er compoir pas dans la meme range, bon candidat
                        for r in l_rangee:
                            Y[j] = get_solution_init.D[r]



        f_prim, Y_prim = glouton(instance, E, S, Y, i, j)
        if f_prim <= f_best:
            if f_prim < f_best:
                iter_best = iter
                y_best, f_best = Y_prim, f_prim
        if y_best == y:
            return f
        else:
            y, f = y_best, f_best
    return f, y


