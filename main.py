from Airfoil import *
from aerodynamique import *
from ConditionVol import *
from VolOpenSkyAsync import *
import requests

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

"""
BOUCLE PRINCIPALE.
"""

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
        else:
            pass

        while True:
            recup_coef_aero = input("\nVoulez-vous récupérer les performances aérodynamiques de votre profil? (Oui / Non): ").strip().lower()
            if recup_coef_aero in ["oui", "non"]:
                break  # sortie de la boucle si la réponse est valide
            else:
                print("Réponse invalide. Veuillez écrire 'Oui' ou 'Non'.")

        if recup_coef_aero == "oui":

            reynolds = int(input("\nPour quel nombre de Reynolds? (50000/100000/1000000): "))

            aero = Aerodynamique(nom_profil)

            # Télécharger le fichier texte depuis AirfoilTools
            nom_fichier_txt = f"{nom_profil}_coef_aero.txt"
            aero.telecharger_et_sauvegarder_txt(nom_fichier_txt, reynolds)

            # Lire le fichier texte et convertir en DataFrame
            df = aero.lire_txt_et_convertir_dataframe(nom_fichier_txt)

            # Stocker dans l’objet et tracer
            aero.donnees = df

            while True:
                tracer_polaire = input("\nVoulez-vous afficher les courbes aérodynamiques de votre profil? (Oui / Non): ").strip().lower()
                if tracer_polaire in ["oui", "non"]:
                    break  # sortie de la boucle si la réponse est valide
                else:
                    print("Réponse invalide. Veuillez écrire 'Oui' ou 'Non'.")

            if tracer_polaire == "oui":
                aero.tracer_polaires_depuis_txt()
            else:
                pass

            perfo_pour_finesse = "importer"

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

        while True:
            tracer = input("\nVoulez-vous afficher le profil? (Oui / Non): ").strip().lower()
            if tracer in ["oui", "non"]:
                break  # sortie de la boucle si la réponse est valide
            else:
                print("Réponse invalide. Veuillez écrire 'Oui' ou 'Non'.")

        if tracer == "oui":
            profil_manuel.tracer_profil_manuel(x_up, y_up, x_low, y_low)

        elif tracer == "non":
            pass
        else:
            pass

        while True:
            lancement_xfoil = input("\nVoulez-vous calculer les performances de votre profil? (Oui / Non): ").strip().lower()
            if lancement_xfoil in ["oui", "non"]:
                break  # sortie de la boucle si la réponse est valide
            else:
                print("Réponse invalide. Veuillez écrire 'Oui' ou 'Non'.")

        if lancement_xfoil == "oui":
            aero = Aerodynamique(nom_profil)

            mach = float(input("\nRentrez une valeur de Mach (0 à 0.7): "))
            reynolds = int(input("\nRentrez un nombre de Reynolds: "))

            # Générer la polaire avec XFOIL
            aero.telecharger_et_sauvegarder_txtrun_xfoil(f"{nom_profil}_coord_profil.dat", reynolds, mach, alpha_start=-15, alpha_end=15, alpha_step=1, output_file=f"{nom_profil}_coef_aero.txt")
            coef_aero_generes = f"{nom_profil}_coef_aero.txt"
            data = aero.lire_txt_et_convertir_dataframe(coef_aero_generes)
            aero.donnees = data
            aero.tracer_polaires_depuis_txt()

            perfo_pour_finesse = "générer"

        elif lancement_xfoil == "non":
            pass

        else:
            pass

    while True:
        calcul_finesse = input("\nVoulez-vous calculer la finesse maximale? (Oui / Non): ").strip().lower()
        if calcul_finesse in ["oui", "non"]:
            break  # sortie de la boucle si la réponse est valide
        else:
            print("Réponse invalide. Veuillez écrire 'Oui' ou 'Non'.")

    if calcul_finesse == "oui":
        if perfo_pour_finesse == "générer":
            finesse, finesse_max = aero.calculer_finesse(f"{nom_profil}_coef_aero.txt")

        elif perfo_pour_finesse == "importer":
            finesse, finesse_max = aero.calculer_finesse(f"{nom_profil}_coef_aero.txt")

        print(f"\nLa finesse maximale de votre profil est : {finesse_max}")

    elif calcul_finesse == "non":
        pass

    else:
        pass

    #  MENU PRINCIPAL POUR LES CONDITIONS
    print("\nVoulez-vous tester les performances de votre profil ?")
    print("  0 - Non, passer cette étape")
    print("  1 - Conditions réelles (vol existant)")
    print("  2 - Conditions personnalisées")
    print("  3 - Les deux")

    while True:
        choix_mode = input("Entrez 0, 1, 2 ou 3 : ").strip()
        if choix_mode in ("0", "1", "2", "3"):
            break
        print("Réponse invalide, tapez 0, 1, 2 ou 3.")

    # Si l'utilisateur choisit 0, on skippe tout
    if choix_mode == "0":
        print("\nTest de performance ignoré. On passe à la suite.")
    else:
        # Conteneur des conditions choisies
        conditions_choisies = []

        #  Conditions réelles
        if choix_mode in ("1", "3"):
            vols = asyncio.run(fetch_vols(limit=10))
            afficher_liste(vols)
            try:
                sel = int(input("\nSélectionnez le vol (numéro) : ")) - 1
                if 0 <= sel < len(vols):
                    s = vols[sel]
                    alt = s.geo_altitude or 0
                    vit = s.velocity or 0
                    gamma, R = 1.4, 287.05
                    T_std = 288.15 - 0.0065 * alt
                    mach = vit / ((gamma * R * T_std) ** 0.5)
                    lat = s.latitude or 0.0
                    lon = s.longitude or 0.0
                    angle = float(input("Angle d'attaque pour ce vol (°) : "))
                    # Récupération des coordonnées
                    lat = s.latitude or 0.0
                    lon = s.longitude or 0.0
                    # On stocke désormais alt, mach, angle, lat et lon
                    conditions_choisies.append((alt, mach, angle, lat, lon))
                else:
                    print(" Sélection hors plage, on continue.")
            except ValueError:
                print(" Entrée non valide, on continue.")

        #  Conditions personnalisées
        if choix_mode in ("2", "3"):
            try:
                alt_u = float(input("\nAltitude personnalisée (m) : "))
                mach_u = float(input("Mach personnalisé : "))
                angle_u = float(input("Angle d'attaque personnalisé (°) : "))
                conditions_choisies.append((alt_u, mach_u, angle_u))
            except ValueError:
                print(" Valeur incorrecte, saisie ignorée.")

        #  Lancement XFoil pour chaque condition
        if not conditions_choisies:
            print("\nAucune condition définie, XFoil n’est pas lancé.")
        else:
            aero = Aerodynamique(nom_profil)
            for i, (alt, mach, angle, lat, lon) in enumerate(conditions_choisies, start=1):
                #  calculer ΔISA en fonction de lat/lon/alt
                delta = calcul_delta_isa(lat, lon, alt, API_KEY) or 0.0
                print(f"\nCondition choisie #{i} – ΔISA météo : {delta:+.1f} K")

                #  créer ConditionVol en lui passant ce ΔISA
                cond = ConditionVol(altitude_m=alt,
                                    mach=mach,
                                    angle_deg=angle,
                                    delta_isa=delta)
                cond.afficher()

                #  vitesse du son corrigée par la vraie température
                gamma, R = 1.4, 287.05
                vitesse_son = (gamma * R * cond.temperature_K) ** 0.5
                vitesse = mach * vitesse_son
                print(f"Vitesse ≈ {vitesse:.1f} m/s (mach×sons), son à {vitesse_son:.1f} m/s")

                #  calcul du Reynolds
                corde = 1.0
                reynolds = cond.calculer_reynolds(
                    vitesse_m_s=vitesse,
                    corde_m=corde,
                    viscosite_kgms=cond.viscosite_kgms,
                    densite_kgm3=cond.densite_kgm3
                )
                print(f"Reynolds (corde=1 m) : {reynolds:.2e}")

                #  lancement XFoil avec ce Reynolds
                aero.telecharger_et_sauvegarder_txtrun_xfoil(
                    f"{nom_profil}_coord_profil.dat",
                    reynolds,
                    mach,
                    alpha_start=-15,
                    alpha_end=15,
                    alpha_step=1,
                    output_file=f"{nom_profil}_coef_aero_{i}.txt"
                )

                # lecture + tracé…

                #  Lecture et tracé
                df = aero.lire_txt_et_convertir_dataframe(f"{nom_profil}_coef_aero_{i}.txt")
                aero.donnees = df
                aero.tracer_polaires_depuis_txt()

    while True:
        comparaison = input("\nVoulez-vous comparer deux profils d'aile? (Oui / Non): ").strip().lower()
        if comparaison in ["oui", "non"]:
            break  # sortie de la boucle si la réponse est valide
        else:
            print("Réponse invalide. Veuillez écrire 'Oui' ou 'Non'.")

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