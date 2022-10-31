"""Exemple de modèle PLNE à NxM variables construit avec PuLP et Resolu avec GLPK 
Ce code reprend ce qui a été vu en TP ROTA

executer la commande : python expl_PLNE_bis.py
"""

import pulp
#1- DONNEES

N = 10
M = 5
idx = [(i, j) for i in range(N) for j in range(M)]

#2- MODELE

# initialisation du modele
pb_binaire = pulp.LpProblem("un exemple de modèle binaire", pulp.LpMaximize)

#VARIABLES
x = pulp.LpVariable.dicts("x", idx, cat="Binary")

#FONCTION OBJECTIF
pb_binaire += sum(x[i,j] for (i,j) in idx) #maximiser la somme des xij

#CONTRAINTES
for j in range(M):
    pb_binaire += sum(x[i,j] for i in range(N))<= 3 #pas plus de 3 "1" par colonne
pb_binaire += x[1,1]==1 #x11 =1


#3- RESOLUTION, avec un temps limite de 100 secondes
pb_binaire.solve(pulp.GLPK_CMD(msg=1,options=["--tmlim", "100"]))


#4- RECUPERATION et AFFICHAGE de la SOLUTION
print("Statut:", pulp.LpStatus[pb_binaire.status]) 


for x in pb_binaire.variables():
    if (x.varValue):
        print(x.name, "=", x.varValue)
print("Fonction objectif optimale = ", pulp.value(pb_binaire.objective))

