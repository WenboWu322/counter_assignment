"""Exemple de modèle PLNE à 2 variables construit avec PuLP et Resolu avec GLPK 

Ce code reprend ce qui a été vu en TP ROTA

executer la commande : python expl_PLNE.py
"""


import pulp
#1- DONNEES

#2- MODELE

# initialisation du modele
prob1 = pulp.LpProblem("Mon_premier_problème", pulp.LpMaximize)

#VARIABLES
x = pulp.LpVariable("x", lowBound=0, upBound=None, cat='Integer')
y = pulp.LpVariable("y", lowBound=0, cat='Integer')

#FONCTION OBJECTIF
prob1 += 3*x + 4*y, "ma_fonction_objectif"

#CONTRAINTES
prob1 +=   x + 2*y <= 10, "ma_contrainte_1"
prob1 +=  -x + 3*y <=  9, "ma_contrainte_2"
prob1 += 2*x +   y <= 13, "ma_contrainte_3"

#3- RESOLUTION

prob1.solve(pulp.GLPK_CMD(msg=1)) #Ici on décide de faire appel à GLPK
#prob1.solve(pulp.COIN_CMD(msg=1)) # si COIN-OR est installé l'utiliser plutôt que GLPK


#4- RECUPERATION et AFFICHAGE de la SOLUTION

print("Statut:{}\n".format (pulp.LpStatus[prob1.status]))

for v in prob1.variables():
    print(v.name, "=", v.varValue)

print("Valeur optimale de la fonction objectif = ", pulp.value(prob1.objective))
