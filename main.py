from Airfoil import Airfoil  # Demander à l'utilisateur d’entrer le code du profil
from weather_api import get_delta_isa
from Airfoil import generer_pale_vrillee
from Airfoil import *
from aerodynamique import *
import subprocess
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# profil = Airfoil.depuis_airfoiltools("naca2412-il")
# pourcentage = float(input("Pourcentage de bruit (%): "))
# profil.tracer_avec_bruit(pourcentage_bruit=pourcentage)

# nom_profil = input("Nom du profil (ex: naca2412-il): ")
# profil = Airfoil.depuis_airfoiltools(nom_profil)
#
# angle = float(input("Angle de rotation (°): "))
# profil.tracer_avec_rotation(angle_deg=angle)


# nom_profil = input("Entrez le nom du profil (ex: naca2412-il): ")
# profil = Airfoil.depuis_airfoiltools(nom_profil)

# angle_max = float(input("Angle maximal de vrillage au bord de fuite (en degrés) : "))
# profil.tracer_vrillage(angle_max_deg=angle_max)
#
# profil = Airfoil.depuis_airfoiltools("naca4412-il")
# coords = np.array(profil.coordonnees)
#
# pale = generer_pale_vrillee(coords, angle_max_deg=45, z_max=1.0)
#
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.plot(pale[:, 0], pale[:, 1], pale[:, 2])
# plt.title("Pale vrillée (rotation selon Z)")
# plt.show()

###############################################################
import asyncio
from VolOpenSkyAsync import VolOpenSkyAsync
from VolOpenSkyAsync import charger_compagnies_depuis_csv

# # Charger les compagnies
# compagnies = charger_compagnies_depuis_csv("data/iata_airlines.csv")
#
# async def main():
#     api = VolOpenSkyAsync()
#     vols = await api.get_vols(limit=3)
#
#     for i, v in enumerate(vols):
#         code = v['callsign'][:3].upper().strip()
#         print(f" Recherche du code : {code}")
#
#         nom, pays = compagnies.get(code, ("Compagnie inconnue", "Pays inconnu"))
#
#         if (nom, pays) == ("Compagnie inconnue", "Pays inconnu"):
#             print(f" Code {code} non trouvé dans le fichier.")
#
#         print(f"{i+1}.  {v['callsign']} - {nom} ({pays})")
#         print(f"   Altitude: {v['altitude_m']:.1f} m - Vitesse: {v['vitesse_mps']:.1f} m/s")
#         lat, lon = v["position"]
#         alt = v["altitude_m"]
#         delta = get_delta_isa(lat, lon, alt, API_KEY)
#
#         # Met à jour le delta ISA dans ton objet
#         v["condition_vol"].delta_isa = delta
#         # Affiche tous les paramètres aérodynamiques
#         v["condition_vol"].afficher()
#         print()


if __name__ == "__main__":

    API_KEY = "c6bf5947268d141c6ca08f54c7d65b63"

    print("\n---- Début du programme Airfoil ----\n")

    generation = input("Voulez-vous importer ou générer un profil d'aile? ")

    if generation == "importer":
        nom_profil = input("Entrez le nom exact du profil NACA (ex : naca2412-il) : ")

        profil = Airfoil.depuis_airfoiltools(nom_profil)
        # Sauvegarde des coordonnées
        profil.sauvegarder_coordonnees(f"{nom_profil}.csv")
        # Affichage graphique
        profil.tracer_contour()

    elif generation == "générer":
        # Création d'un profil manuel:
        nom_profil_manuel = input("Entrez le nom de votre profil NACA: ")
        profil_manuel = Airfoil(nom_profil_manuel, [])
        x_up, y_up, x_low, y_low, x, c = profil_manuel.naca4_profil()
        profil_manuel.enregistrer_profil_manuel_csv(x_up, y_up, x_low, y_low, nom_fichier=f"{nom_profil_manuel}.csv")
        profil_manuel.enregistrer_profil_format_dat(x_up, y_up, x_low, y_low, c, nom_fichier=f"{nom_profil_manuel}.dat")

    aero = Aerodynamique(nom_profil_manuel)
    # Générer la polaire avec XFOIL
    aero.run_xfoil(f"{nom_profil_manuel}.dat", alpha_start=-5, alpha_end=15, alpha_step=1, output_file=f"{nom_profil_manuel}.txt")