from Airfoil import *
from aerodynamique import *
from ConditionVol import *

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


# profil = Airfoil.depuis_airfoiltools("naca2412-il")
# aero = Aerodynamique(profil)

# Étape 2 : Créer l’objet aérodynamique à partir du profil
# aero = Aerodynamique(profil)

# Étape 3 : Récupérer les données depuis AirfoilTools
# aero.recuperer_donnees()

# Étape 4 : Sauvegarder dans un fichier CSV
# aero.sauvegarder_csv("polaire_naca2412.csv")

# Étape 5 : Tracer les courbes Cl, Cd, Cm
# aero.tracer_polaires()
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

def demande_profil():

    nom_profil = input("\nEntrez le nom du profil NACA (format : naca2412) : ").strip().lower()
    nom_profil = f"{nom_profil}-il"

    #Vérifier si le profil est déjà dans la base de données!
    #sinon:
    profil_obj = Airfoil.depuis_airfoiltools(nom_profil)

    # Sauvegarde des coordonnées
    profil_obj.sauvegarder_coordonnees(f"{nom_profil}_coord_profil.csv")

    print(f"\nLes coordonnées du profil ont été enregistrés dans le fichier: {nom_profil}_coord_profil.csv")
    return profil_obj, nom_profil

if __name__ == "__main__":

    API_KEY = "c6bf5947268d141c6ca08f54c7d65b63"

    print("\n---- Début du programme Airfoil ----\n")

    #On demande à l'utilisateur s'il veut créer ou importer un profil
    while True:
        generation = input("Voulez-vous importer ou générer un profil d'aile? ").strip().lower()
        if generation in ["importer", "générer"]:
            break  # OK : on sort de la boucle
        else:
            print("Réponse invalide. Veuillez taper 'importer' ou 'générer'.\n")

    """
    DANS LE CAS D'UNE IMPORTATION.
    """
    if generation == "importer":

        profil_obj_import, nom_profil = demande_profil()

        tracer = input("\nVoulez-vous afficher le profil? (Oui / Non): ").strip().lower()

        if tracer == "oui":
            # Affichage graphique
            profil_obj_import.tracer_contour(nom_profil)
        elif tracer == "non":
            pass
        else:
            pass

        recup_coef_aero = input("\nVoulez-vous récupérer les performances aérodynamiques de votre profil? (Oui / Non): ").strip().lower()

        if recup_coef_aero == "oui":

            aero = Aerodynamique(nom_profil)

            # Télécharger le fichier texte depuis AirfoilTools
            nom_fichier_txt = f"polar_{nom_profil}.txt"
            aero.telecharger_et_sauvegarder_txt(nom_fichier_txt)

            # Lire le fichier texte et convertir en DataFrame
            df = aero.lire_txt_et_convertir_dataframe(nom_fichier_txt)

            # Stocker dans l’objet et tracer
            aero.donnees = df

            tracer_polaire = input("\nVoulez-vous afficher les courbes aérodynamiques de votre profil? (Oui / Non): ").strip().lower()

            if tracer_polaire == "oui":
                aero.tracer_polaires_depuis_txt()
            else:
                pass

            perfo_pour_finesse = "importer"

        elif recup_coef_aero == "non":
            pass

        else:
            pass

        """
        DANS LE CAS D'UNE CRÉATION MANUELLE.
        """
    elif generation == "générer":

        # Création d'un profil manuel:
        while True:
            #demande un nom au fichier/profil
            nom_profil = input("\nEntrez le nom de votre profil NACA: ").strip().lower()
            nom_profil = f"{nom_profil}-il"
            #Boucle pour vérifier si le fichier existe déjà
            verif_fichier = f"{nom_profil}_coord_profil.csv"

            if os.path.exists(verif_fichier):
                print(f"Le fichier '{verif_fichier}' existe déjà.")
                choix = input("\nVoulez-vous écraser le fichier ? (Oui/Non) : ").strip().lower()

                if choix == "oui":
                    print(f"Suppression du fichier '{verif_fichier}'...")
                    os.remove(f"{verif_fichier}")
                    break  # On sort de la boucle, on continue avec ce nom
                elif choix == "non":
                    print("\nVeuillez entrer un autre nom de profil.")
            else:
                break

        profil_manuel = Airfoil(nom_profil, [])
        x_up, y_up, x_low, y_low, x, c = profil_manuel.naca4_profil()

        profil_manuel.enregistrer_profil_manuel_csv(x_up, y_up, x_low, y_low, nom_fichier=f"{nom_profil}_coord_profil.csv")
        profil_manuel.enregistrer_profil_format_dat(x_up, y_up, x_low, y_low, c, nom_fichier=f"{nom_profil}_coord_profil.dat")

        tracer = input("\nVoulez-vous afficher le profil? (Oui / Non): ").strip().lower()

        if tracer == "oui":
            profil_manuel.tracer_profil_manuel(x_up, y_up, x_low, y_low)

        elif tracer == "non":
            pass
        else:
            pass

        lancement_xfoil = input("\nVoulez-vous calculer les performances de votre profil? (Oui / Non): ").strip().lower()

        if lancement_xfoil == "oui":
            aero = Aerodynamique(nom_profil)

            mach = float(input("\nRentrez une valeur de Mach (0 à 0.7): "))
            reynolds = int(input("\nRentrez un nombre de Reynolds: "))

            # Générer la polaire avec XFOIL
            aero.run_xfoil(f"{nom_profil}_coord_profil.dat", reynolds, mach, alpha_start=-15, alpha_end=15, alpha_step=1, output_file=f"{nom_profil}_coef_aero.txt")
            coef_aero_generes = f"{nom_profil}_coef_aero.txt"
            data = aero.lire_txt_et_convertir_dataframe(coef_aero_generes)
            aero.donnees = data
            aero.tracer_polaires_depuis_txt()

            perfo_pour_finesse = "générer"

        elif lancement_xfoil == "non":
            pass

        else:
            pass

    calcul_finesse = input("\nVoulez-vous calculer la finesse maximale? (Oui / Non): ").strip().lower()

    if calcul_finesse == "oui":
        if perfo_pour_finesse == "générer":
            finesse, finesse_max = aero.calculer_finesse(f"{nom_profil}_coef_aero.txt")

        elif perfo_pour_finesse == "importer":
            finesse, finesse_max = aero.calculer_finesse(f"polar_{nom_profil}.txt")

        print(f"\nLa finesse maximale de votre profil est : {finesse_max}")

    elif calcul_finesse == "non":
        pass

    else:
        pass

    obtenir_vol = input("\nVoulez-vous choisir un vol existant? (Oui / Non): ").strip().lower()

    if obtenir_vol == "oui":
        pass
    elif obtenir_vol == "non":
        pass
    else:
        pass

    obtenir_conditions_vol = input("\nVoulez-vous obtenir les conditions de vol? (Oui / Non): ").strip().lower()

    if obtenir_conditions_vol == "oui":

        altitude = float(input("\nAltitude (en mètres):"))
        mach = float(input("Nombre de mach:"))
        angle = float(input("Angle d'attaque (en °):"))

        conditions_vol = ConditionVol(altitude, mach, angle)
        conditions_vol.afficher()

        """
        Il est proposé de croiser le profil avec les conditions de vol obtenues.
        """
        calculer_perfo_vol = input("\nVoulez-vous obtenir les performances de votre profil selon les conditions de vol choisies? (Oui / Non): ").strip().lower()

        if calculer_perfo_vol == "oui":
            #Le programme lance XFoil avec les données du profil et les conditions atmosphériques du vol.
            aero = Aerodynamique(nom_profil)

            # mach = float(input("\nRentrez une valeur de Mach (0 à 0.7): "))
            # reynolds = int(input("\nRentrez un nombre de Reynolds: "))

            # Générer la polaire avec XFOIL
            aero.run_xfoil(f"{nom_profil}_coord_profil.dat", reynolds, mach, alpha_start=-15, alpha_end=15,
                           alpha_step=1, output_file=f"{nom_profil}_coef_aero.txt")
            coef_aero_generes = f"{nom_profil}_coef_aero.txt"
            data = aero.lire_txt_et_convertir_dataframe(coef_aero_generes)
            aero.donnees = data
            aero.tracer_polaires_depuis_txt()

            perfo_pour_finesse = "générer"

        elif calculer_perfo_vol == "non":
            pass

    elif obtenir_conditions_vol == "non":
        pass

    comparaison = input("\nVoulez-vous comparer deux profils d'aile? (Oui / Non): ").strip().lower()

    if comparaison == "oui":

        print("\nCHOIX 1:")
        profil_1_obj, profil_1_nom = demande_profil()
        print("\nCHOIX 2:")
        profil_2_obj, profil_2_nom = demande_profil()

        p_1 = Airfoil.depuis_airfoiltools(profil_1_nom)
        p_2 = Airfoil.depuis_airfoiltools(profil_2_nom)

        p_1.tracer_comparaison(p_2)

    elif comparaison == "non":
        pass
    else:
        pass

    print("\n---- Fin du programme ----\n")

    # nom = input("Nom du profil (ex: n2414-il) : ").strip()
    # aero = Aerodynamique(nom)
    #
    # # Télécharger le fichier texte depuis AirfoilTools
    # nom_fichier_txt = f"polar_{nom}.txt"
    # aero.telecharger_et_sauvegarder_txt(nom_fichier_txt)
    #
    # # Lire le fichier texte et convertir en DataFrame
    # df = aero.lire_txt_et_convertir_dataframe(nom_fichier_txt)
    #
    # # Stocker dans l’objet et tracer
    # aero.donnees = df
    # aero.tracer_polaires_depuis_txt()
    # # Lina branchel
    #
    # """ def recuperer_donnees(self):
    #         response = requests.get(self.url_csv)
    #         if response.status_code != 200:
    #             print("Erreur de récupération")
    #             return"""
    #
    # """
    #     lancement de Xfoil pour calculer les polaires
    # """

