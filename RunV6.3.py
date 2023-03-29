from sklearn.neighbors import *
import numpy as np
from sklearn.pipeline import *
from sklearn.preprocessing import *
from sklearn.linear_model import *
from sklearn import svm

import pywifi
from pywifi import const
import time

##### INIT_WIFIS
# Initialise l'ensemble des wifis
def  init_wifis(data_base, wifis):
    for point in data_base:
        for key in point.keys():
            if not (key in wifis) and key != "salle" :
                wifis.update({key: len(wifis)})
    return

##### REPERTORIE_WIFIS
# Rajouter les nouvelles wifis trouvées par un "point" (type : dictionnaire) à l'ensemble "wifis" (type : dictionnaire)
def repertorie_wifis(point, wifis, total_points):
    for key in point.keys():
        if not (key in wifis) and key != "salle" :
            wifis.update({key: len(wifis)})
            plus_point(total_points)
    return

##### PLUS_POINT
# Augmente la dimention du model de 1
def plus_point(total_points) :
    total_point = np.hstack((total_points, np.zeros((total_points.shape[0], 1))))
    return

##### MAJ
# Ajoute un nouveau point aux connsaissances totales
def maj(point, total_points, total_salles, wifis):
    xtemp = np.empty((1, len(wifis)), dtype=int)
    for key in wifis:
        if key in point :
            xtemp[0,wifis.get(key)] = point.get(key)
    print("nombre de wifis", len(wifis),"taille point", len(point),"taille xtemp", len(xtemp[0]))
    total_points = np.concatenate((total_points, xtemp))
    total_salles = np.append(total_salles, point.get("salle"))
    return(total_points, total_salles)

##### ACTUALISE
# Mets à jour les wifis puis ajoute un nouveau point aux connsaissances totales
def actualise(point, total_points, total_salles, wifis):
        repertorie_wifis(point, wifis, total_points)
        total_points, total_salles = maj(point, total_points, total_salles, wifis)
        return(total_points, total_salles)

##### APPRENDS
# Apprends au model a partir de nos points connus
def apprends(ML, total_points, total_salles):
    print("total_point : ", total_points, "de taille", len(total_points), "\n total_salle : ", total_salles, "de taille", len(total_salles))
    ML.fit(total_points, total_salles)
    return

##### PARTAGER
# L'utilisateur peut renseigner un nouveau point
def partager(ML, total_points, total_salles, wifis):
    point = position_wifis()
    print("Dans quelle salle es tu?")
    place = input()
    point.update({"salle" : place})
    total_points, total_salles = actualise(point, total_points, total_salles, wifis)
    apprends(ML, total_points, total_salles)
    return

##### SAVOIR
# Renseigne à l'utilisateur ou il se trouve
def savoir(ML, total_points, total_salles, wifis):
    point = position_wifis()
    p2 = transfo(point, wifis)
    place2 = ML.predict([p2])
    place2 = place2[0]
    print("Le modèle pense que tu es dans la salle : ", place2, ", non? (Tape OUI pour valider)")
    answer = input() 
    if answer == "OUI":
        point.update({"salle": place2})
        actualise(point, total_points, total_salles, wifis)
        apprends(ML, total_points, total_salles)
    return

##### TRANSFO
# Transforme un point (type Dictionnaire) en un point (type np.Array)
def transfo(point, wifis):
    xtemp = np.array([0]*len(wifis))
    for key in wifis:
        if key in point :
            xtemp[wifis.get(key)] = point.get(key)
    return(xtemp)

##### SCAN_WIFI
# Scan l'ensemble de nos wifis captées
def scan_wifi():
    wifi = pywifi.PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    #time.sleep(5)
    bessis = iface.scan_results()
    wifi_dict = {}
    for data in bessis:
        wifi_dict[data.bssid] = 10**((data.signal)/10)*1000000000
    return wifi_dict

##### REMOVE_DUPLICATES
# Supprime les wifis en double
def remove_duplicates(wifi_dict):
    seen = set()
    unique_dict = {}
    for bssid, signal in wifi_dict.items():
        if bssid not in seen:
            seen.add(bssid)
            unique_dict[bssid] = signal
        else:
            if wifi_dict[bssid] > unique_dict[bssid]:
                unique_dict[bssid] = wifi_dict[bssid]
    return unique_dict

##### POSITION_WIFI
# Donne la position wifi de l'utilisateur
def position_wifis():
    return(remove_duplicates(scan_wifi()))

##### DONNEES INITIALISATION
# Crée l'ensemble des données de base
def donnes_initialisation(nb_pieces):
    datas = np.array([])
    for numero in range(1,nb_pieces+1):
        print("Nous allons commencer la pièce ", numero, ". ")
        salle = input("Quelle est son nom ?")
        print("Nous allons te demander de prendre 5 positions dans cette pièce, une au centre et les autres dans 4 coins opposés. Tu peux prendre ces points dans l'odre que tu souhaites.")
        for i in range(1, 6):
            point = position_wifis()
            point.update({"salle" : salle})
            print("Plus que ", 5-i, " points.")
            datas = np.append(datas, point)
            suivant = input("Change de position, tape entrée pour continuer.")
    return(datas)

##### LECTURE INITIALISATION
# Prend l'ensemble des données de base (data_base np.Array) et apprends
def lecture_initialisation(data_base, ML, total_points, total_salles, wifis):
    for point in data_base :
        total_points, total_salles = actualise(point, total_points, total_salles, wifis)
    total_points = np.delete(total_points, 0, 0)
    apprends(ML, total_points, total_salles)
    return


# >>>>>>>>> RUN <<<<<<<<<< #
def run(nb_pieces):
    datas = donnes_initialisation(nb_pieces)
    wifis = {}
    init_wifis(datas, wifis)
    ML = svm.SVC(kernel='poly')
    total_points = np.ones((1, len(wifis)))
    total_salles = np.array([])

    lecture_initialisation(datas, ML, total_points, total_salles, wifis)
    print(" \n Bonjour et bienvenue sur Flaxe! \n As tu quelque chose pour nous ? ")
    print("Pour sortir -> Non")
    print("Pour savoir ou tu es -> Savoir")
    print("Pour nous indiquer une nouvelle position -> Partager")
    answer = input()
    while (answer != "Non"):
        if answer == "Partager" :
            partager(ML, total_points, total_salles, wifis)
        if answer == "Savoir" :
            print("D'après notre prédiction..")
            savoir(ML, total_points, total_salles, wifis)
        print("Quelque chose de plus à nous dire?")
        print("Pour sortir -> Non")
        print("Pour savoir ou tu es -> Savoir")
        print("Pour nous indiquer une nouvelle position -> Partager")
        answer = input()
    print("Flaxe te remercie <3 !")
    return


run(2)

