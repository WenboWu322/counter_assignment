"""
Ce fichier constitue un exemple très simple d'utilisation du module ccap.py fourni.
Il lit une instance et affiche pour chaque vol, son callsign, sa date TKO et le nombre de comptoirs
qu'il requiert

Pour exécuter le programme : python exemple_lecture_affichage.py chemin_vers_l_instance_a_tester
"""

import sys
from ccap import *



instance = Instance.from_file(sys.argv[1])
print("Vol\t TKO\t nombre de comptoirs requis")

#affichage de vols
for f in instance:
    print("{}\t {}\t {}".format(f.callsign,f.tko,f.booths))
