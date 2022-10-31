"""
Ce fichier donne un squelette d'implémentation de vos modèles pour le livrable L1. 
Il reprend les éléments donnés dans expl_PLNE.py, expl_PLNE_bis.py et exemple_lecture_affichage.py

Ne pas oublier de le renommer selon les consignes du sujet avant de le rendre. 

Pour exécuter le programme : python template_modele_L1.py fichier-de-l-instance
"""

import sys
from ccap import *

import pulp

#1- DONNEES

instance = Instance.from_file(sys.argv[1])
print("Vol\t TKO\t nombre de comptoirs requis\t rangées préférées")

#affichage des vols
#for f in instance:
#    print("{}\t {}\t {}\t\t\t\t{}".format(f.callsign,f.tko,f.booths,f.preferences))

#2- MODELE

# initialisation du modele
prob_L1 = pulp.LpProblem("premier modele pour affectation de comptoirs", pulp.LpMinimize)

#VARIABLES


#FONCTION OBJECTIF


#CONTRAINTES


#3- RESOLUTION

prob_L1.solve(pulp.GLPK_CMD(msg=1, options=["--tmlim", "120"])) # Time limit fixé à 120 secondes
#prob_L1.solve(pulp.COIN_CMD(msg=1)) # si COIN-OR est installé l'utiliser plutôt que GLPK


#4- RECUPERATION et AFFICHAGE de la SOLUTION

print("Statut:{}\n".format (pulp.LpStatus[prob_L1.status]))

#Ci-dessous un affichage generique de la solution, a adapter et ameliorer si besoin, en fonction de votre modele
for v in prob_L1.variables():
    print(v.name, "=", v.varValue)

print("Valeur optimale de la fonction objectif = ", pulp.value(prob_L1.objective))


