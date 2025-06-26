import os
import pandas as pd
import asyncio
import matplotlib.pyplot as plt
import streamlit as st

from projet_sessionE2025.Interface.interaction_graphique import *
from projet_sessionE2025.airfoil.Airfoil import Airfoil
from projet_sessionE2025.BaseDonnees.gestion_base import GestionBase
from projet_sessionE2025.aero.aerodynamique import Aerodynamique
from projet_sessionE2025.donnees_vol.VolOpenSkyAsync import *
from projet_sessionE2025.donnees_vol.ConditionVol import *

def demande_profil(interface):
    nom_profil = interface.demander_texte("Entrez le nom du profil NACA (ex: naca2412)").strip().lower()

    if nom_profil:
        nom_profil = nom_profil.strip().lower()
    else:
        interface.msgbox("Aucun nom saisi. Veuillez réessayer.", titre="Erreur")
        return None, None  # Ajouter cette ligne pour gérer explicitement le cas vide

    nom_profil = f"{nom_profil}"

    profil_obj = Airfoil.depuis_airfoiltools(nom_profil)

    profil_obj.sauvegarder_coordonnees(f"{nom_profil}_coord_profil.csv")

    interface.msgbox(f"\nLes coordonnées du profil ont été enregistrées dans le fichier : {nom_profil}_coord_profil.csv", titre="Information")

    return profil_obj, nom_profil


def comparer_polaires(profiles: dict[str, pd.DataFrame]):
    """
    Compare plusieurs polaires en un seul graphique 2×2 :
      - CL(α)
      - CD(α)
      - CM(α)
      - CL(CD) (polar lift/drag)
    profiles : dictionnaire {label → DataFrame}, chaque DataFrame doit avoir les colonnes
               'alpha', 'CL', 'CD' et 'CM'.
    """
    if not profiles:
        st.warning("Aucun profil fourni à comparer_polaires().")
        return None

    colonnes_attendues = {"alpha", "CL", "CD", "CM"}
    for label, df in profiles.items():
        if df is None or df.empty:
            st.warning(f" Le DataFrame de {label} est vide.")
            return None
        if not colonnes_attendues.issubset(df.columns):
            st.error(f" Le DataFrame de {label} ne contient pas toutes les colonnes attendues.")
            return None
    # Prépare un 2×2
    fig, axs = plt.subplots(2, 2, figsize=(12, 10))
    ax_cl,   ax_cd   = axs[0]
    ax_cm,   ax_lvsd = axs[1]

    # Pour chaque profil, trace trois courbes
    for label, df in profiles.items():
        ax_cl.plot(   df["alpha"], df["CL"],   label=label)
        ax_cd.plot(   df["alpha"], df["CD"],   label=label)
        ax_cm.plot(   df["alpha"], df["CM"],   label=label)
        ax_lvsd.plot(df["CD"],    df["CL"],   label=label)

    # Titres, axes, légendes, grilles
    ax_cl  .set_title("CL vs α");   ax_cl  .set_ylabel("CL");    ax_cl  .legend(); ax_cl  .grid(True)
    ax_cd  .set_title("CD vs α");   ax_cd  .set_ylabel("CD");    ax_cd  .legend(); ax_cd  .grid(True)
    ax_cm  .set_title("CM vs α");   ax_cm  .set_ylabel("CM");    ax_cm  .legend(); ax_cm  .grid(True)
    ax_lvsd.set_title("CL vs CD");  ax_lvsd.set_xlabel("CD"); ax_lvsd.set_ylabel("CL"); ax_lvsd.legend(); ax_lvsd.grid(True)

    # Ajuste les espacements
    plt.tight_layout()
    #plt.show()
    return fig

def choisir_vols(limit: int = 100, sample_n: int = 20) -> pd.DataFrame:
    """
    Récupère via fetch_vols(limit), construit un DataFrame,
    filtre selon la troposphère/stratosphère, prélève un échantillon aléatoire,
    et répète jusqu'à ce que l'utilisateur valide la liste.
    """
    while True:
        # 1) fetch et DataFrame
        vols = asyncio.run(fetch_vols(limit=limit))
        rows = []
        for v in vols:
            rows.append({
                "icao24":          v.icao24,
                "callsign":        (v.callsign or "").strip(),
                "origin_country":  v.origin_country,
                "altitude_m":      v.geo_altitude or 0.0,
                "vitesse_m_s":     v.velocity or 0.0,
                "latitude":        v.latitude,
                "longitude":       v.longitude
            })
        df = pd.DataFrame(rows)

        # 2) choix du filtre — entrée robuste
        while True:
            print("\nFiltrer les vols par altitude :")
            print("  1 - Troposphère (< 11 000 m)")
            print("  2 - Stratosphère (≥ 11 000 m)")
            print("  3 - Aucun filtre")
            choix = input("Votre choix (1/2/3) : ").strip()
            if choix in ("1", "2", "3"):
                break
            print(" Entrée invalide. Veuillez entrer 1, 2 ou 3.")

        if choix == "1":
            df_filt = df[df["altitude_m"] < 11000]
        elif choix == "2":
            df_filt = df[df["altitude_m"] >= 11000]
        else:
            df_filt = df

        if df_filt.empty:
            print("Aucun vol ne correspond à ce filtre, on recommence.")
            continue

        # 3) prélèvement aléatoire
        n = min(sample_n, len(df_filt))
        df_sample = df_filt.sample(n=n).reset_index(drop=True)

        # 4) affichage
        print(df_sample[[
            "icao24", "callsign", "origin_country", "altitude_m", "vitesse_m_s"
        ]].to_string(index=True))

        # 5) validation — entrée robuste
        while True:
            rep = input("\nCette liste vous convient-elle ? (oui/non) ").strip().lower()
            if rep in ("oui", "non"):
                break
            print(" Veuillez répondre uniquement par 'oui' ou 'non'.")

        if rep == "oui":
            return df_sample
        # sinon on boucle



"""
BOUCLE PRINCIPALE.
"""

if __name__ == "__main__":
    """
    Initialisation des variables nécessaires.
    """

    interface = FenetreInteraction()

    API_KEY = "c6bf5947268d141c6ca08f54c7d65b63"
    #Initialisation de la BaseDonnees de données des profils
    gestion = GestionBase()
    # on réserve les variables pour stocker chacun des trois objets Aerodynamique
    aero_import = None
    aero_manuel = None
    aero_base = None
    aero_volreel = None
    aero_volperso = None

    df_import = None
    df_manuel = None
    df_base = None
    df_volreel = None
    df_volperso = None
    # Initialisation des chemins et objets
    chemin_dat = None  # localisation du .dat
    """
    Fin de l'initialisation des variables nécessaires.
    """
    print("\n---- Lancement du programme Airfoil ----\n")

    generation = interface.demander_choix("Voulez-vous importer de AirfoilTools, de votre BaseDonnees ou générer un profil ?", ["importer", "générer", "BaseDonnees"])

    """
    DANS LE CAS D'UNE IMPORTATION.
    """
    if generation == "importer":

        profil_obj_import, nom_profil = demande_profil(interface)

        chemin_csv = profil_obj_import.sauvegarder_coordonnees(f"{nom_profil}_coord_profil.csv")

        # Construire le chemin .dat à partir du même nom
        chemin_dat = chemin_csv.replace("_coord_profil.csv", "_coord_profil.dat")

        # Ouvrir le CSV, lire x,y puis écrire le .dat
        with open(chemin_csv, "r") as f_csv, open(chemin_dat, "w") as f_dat:
            lignes = f_csv.readlines()
            # la première ligne est l'en-tête "x,y", on l'ignore :
            f_dat.write(f"{nom_profil}\n")
            for ligne in lignes[1:]:
                x_str, y_str = ligne.strip().split(",")
                f_dat.write(f"{float(x_str):.6f} {float(y_str):.6f}\n")

        tracer = interface.demander_choix("Voulez-vous afficher le profil ?", ["Oui", "Non"])

        if tracer.lower() == "oui":
            profil_obj_import.tracer_contour(nom_profil)
        else:
            pass

        recup_coef_aero = interface.demander_choix("Voulez-vous récupérer les performances aérodynamiques de votre profil?", ["Oui", "Non"])

        if recup_coef_aero.lower() == "oui":

            reynolds = int(interface.demander_choix("Pour quel nombre de Reynolds? (50000/100000/1000000)?", ["50000", "100000", "1000000"]))

            aero_import = Aerodynamique(nom_profil)

            # Télécharger le fichier texte depuis AirfoilTools
            chemin_txt_airfoiltools = aero_import.telecharger_et_sauvegarder_txt(reynolds)

            # Lire le fichier texte et convertir en DataFrame
            df_import = aero_import.lire_txt_et_convertir_dataframe(chemin_txt_airfoiltools)
            # **Nouvelle ligne :** on stocke le DataFrame pour le tracer
            aero_import.donnees = df_import

            # Stocker dans l’objet et tracer
            chemin_txt = chemin_txt_airfoiltools

            tracer_polaire = interface.demander_choix("Voulez-vous afficher les courbes aérodynamiques de votre profil?", ["Oui", "Non"])

            if tracer_polaire.lower() == "oui":
                aero_import.tracer_polaires_depuis_txt()
            else:
                pass

            perfo_pour_finesse = "importer"

        else:
            chemin_txt = None

            # on enregistre le profil dans la BaseDonnees et on deplace les fichiers
        gestion.ajouter_profil(
            nom_profil,
            "importé",
            chemin_csv,
            None,  # pas de .dat
            chemin_txt,
            None
            )

        # On normalise l'objet
        aero = aero_import
        profil_obj = profil_obj_import
        nom_profil = nom_profil
        chemin_dat = chemin_dat
        chemin_txt = chemin_txt

        print("nom_profil_import = ", nom_profil)

        """
        DANS LE CAS D'UNE CRÉATION MANUELLE.
        """

    elif generation == "générer":

        profil_manuel, nom_profil = None, None

        while True:
            # Demande un nom au fichier/profil
            nom_profil = interface.demander_texte("Entrez le nom de votre profil NACA :")

            if not nom_profil:
                interface.msgbox("Aucun nom saisi. Veuillez réessayer.", titre="Erreur")
                continue

            nom_profil = f"{nom_profil.strip().lower()}"
            verif_fichier = f"{nom_profil}_coord_profil.csv"

            # Vérifie si le fichier existe déjà
            if os.path.exists(verif_fichier):
                interface.msgbox(f"Le fichier '{verif_fichier}' existe déjà.", titre="Fichier existant")
                choix = interface.demander_choix("Voulez-vous écraser le fichier existant ?", ["Oui", "Non"])
                if choix.lower() == "oui":
                    os.remove(verif_fichier)
                    interface.msgbox(f"Le fichier '{verif_fichier}' a été supprimé.", titre="Information")
                    break  # nom accepté
                else:
                    interface.msgbox("Veuillez entrer un autre nom de profil.")
            else:
                break  # nom accepté

        profil_manuel = Airfoil(nom_profil, [])

        #générer un profil Naca à 4 chiffres.
        x_up, y_up, x_low, y_low, x, c = profil_manuel.naca4_profil()

        #enregistrer les coordonnées du profil en .csv et .dat
        chemin_csv = profil_manuel.enregistrer_profil_manuel_csv(x_up, y_up, x_low, y_low, nom_fichier=f"{nom_profil}_coord_profil.csv")
        chemin_dat = profil_manuel.enregistrer_profil_format_dat(x_up, y_up, x_low, y_low, c, nom_fichier=f"{nom_profil}_coord_profil.dat")

        gestion.ajouter_profil(
            nom_profil,
            "manuel",
            fichier_coord_csv=chemin_csv,
            fichier_coord_dat=chemin_dat,
            #fichier_polaire_txt=chemin_txt,
            fichier_polaire_csv=None
        )

        # Demander à l'utilisateur s'il veut afficher le profil
        tracer = interface.demander_choix("Voulez-vous afficher le profil ?", ["Oui", "Non"]).strip().lower()

        if tracer == "oui":
            profil_manuel.tracer_profil_manuel(x_up, y_up, x_low, y_low)
        elif tracer == "non":
            pass
        else:
            pass

        lancement_xfoil = interface.demander_choix("Voulez-vous calculer les performances de votre profil?", ["Oui", "Non"])

        if lancement_xfoil.lower() == "oui":
            aero_manuel = Aerodynamique(nom_profil)

            params = interface.demander_parametres({
                "mach": "Rentrez une valeur de Mach (0 à 0.7)",
                "reynolds": "Rentrez un nombre de Reynolds"
            })
            mach = params["mach"]
            reynolds = params["reynolds"]

            # Générer la polaire avec XFOIL
            output_file = os.path.join("data", "polaires_xfoil", f"{nom_profil}_coef_aero.txt")

            acces_fichier_dat = os.path.join("data", "profils_manuels", f"{nom_profil}_coord_profil.dat")

            #aero.telecharger_et_sauvegarder_txtrun_xfoil(f"{nom_profil}_coord_profil.dat", reynolds, mach, alpha_start=-15, alpha_end=15, alpha_step=1, output_file=output_file)
            output_file = aero_manuel.run_xfoil(acces_fichier_dat, reynolds, mach, alpha_start=-10, alpha_end=10, alpha_step=0.25,output_file=output_file)

            chemin_txt = output_file

            #Lire fichier output
            df_manuel = aero_manuel.lire_txt_et_convertir_dataframe(output_file)
            aero_manuel.donnees = df_manuel
            aero_manuel.tracer_polaires_depuis_txt()

            #Variable qui enregistre l'existence de courbes aéro nécessaires pour connaitre la finesse.
            perfo_pour_finesse = "générer"

        elif lancement_xfoil.lower() == "non":
            chemint_txt = None
            pass

        chemin_pol_csv = None

        # on enregistre le profil dans la BaseDonnees et on deplace les fichiers
        # gestion.ajouter_profil(nom_profil, "manuel",
        #                        chemin_csv, chemin_dat, chemin_txt, chemin_pol_csv)

        # On normalise l'objet
        aero = aero_manuel
        profil_obj = profil_manuel
        nom_profil = nom_profil
        chemin_dat = chemin_dat
        chemin_txt = chemin_txt
        df = df_manuel

    elif generation == "BaseDonnees":

        #Lecture des dossiers de la BaseDonnees pour lister leur contenu
        dossier_database_import = "data/profils_importes"  #
        dossier_database_genere = "data/profils_manuels"   #

        try:
            contenu_import = os.listdir(dossier_database_import)
            contenu_genere = os.listdir(dossier_database_genere)

            # Vérifier si les deux dossiers sont vides
            if not contenu_import and not contenu_genere:
                interface.msgbox("Aucun profil NACA trouvé dans la BaseDonnees de données.", titre="Base vide")
                base_vide = True
            else:
                base_vide = False

        except FileNotFoundError:
            print(f"Erreur : Le dossier n'existe pas.")
        except PermissionError:
            print(f"Erreur : Accès refusé au dossier.")

        if base_vide == True:
            pass
        elif base_vide == False:
            print("Les fichiers de profils NACA existants dans la BaseDonnees sont listés ci-dessous:\n")

            for element in contenu_import:
                print(element)
            for element in contenu_genere:
                print(element)

            nom_profil = interface.demander_texte("Rentrez le nom du profil NACA que vous souhaitez utiliser").strip().lower()

            essais = gestion.chercher_nom(nom_profil)

            for noms in essais:
                chemin_fichier = f"data/profils_importes/{noms}_coord_profil.dat"
                if os.path.exists(chemin_fichier):
                    for nom_polaire in essais:
                        if os.path.exists(f"data/polaires_importees/{nom_polaire}_coef_aero.txt"):
                            polaire_profil_base = f"{nom_polaire}_coef_aero.txt"
                    coord_profil_base = f"{noms}_coord_profil.dat"
                else:
                    chemin_fichier = f"data/profils_manuels/{noms}_coord_profil.dat"
                    if os.path.exists(chemin_fichier):
                        polaire_profil_base = f"{noms}_coef_aero.txt"
                        coord_profil_base = f"{noms}_coord_profil.dat"
                    else:
                        pass

            dossiers_possibles = [
                "data/profils_importes",
                "data/profils_manuels"
            ]

            # On va cherche le chemin qui mène au fichier : coord_profil_base
            chemin_dat = None
            for dossier in dossiers_possibles:
                chemin_possible = os.path.join(dossier, coord_profil_base)
                if os.path.exists(chemin_possible):
                    chemin_dat = chemin_possible
                    break

            # On refait la même chose pour avoir les fichiers de performances aero
            dossiers_possibles = [
                "data/polaires_importees",
                "data/polaires_xfoil",
            ]
            # On va cherche le chemin qui mène au fichier : polaire_profil_base
            chemin_txt = None
            for dossier in dossiers_possibles:
                chemin_possible = os.path.join(dossier, polaire_profil_base)
                if os.path.exists(chemin_possible):
                    chemin_txt = chemin_possible
                    break

            if chemin_txt is None:
                interface.msgbox(f"Le fichier '{polaire_profil_base}' n'a pas été trouvé dans la BaseDonnees de données, les performances n'ont peut être pas été générées.")

            aero_base = Aerodynamique(nom_profil)

        profil_base = Airfoil(nom_profil, [])

        # Lire fichier dat pour les polaires
        df_base = aero_base.lire_txt_et_convertir_dataframe(chemin_txt)
        aero_base.donnees = df_base
        aero_base.tracer_polaires_depuis_txt()

        perfo_pour_finesse = "BaseDonnees"

        # On normalise l'objet
        aero = aero_base
        profil_obj = profil_base
        nom_profil = nom_profil
        chemin_dat = chemin_dat
        chemin_txt = chemin_txt
        aero.donnees = aero_base.donnees


    calcul_finesse = interface.demander_choix("Voulez-vous calculer la finesse maximale?",["Oui", "Non"])

    if calcul_finesse.lower() == "oui":

        # if perfo_pour_finesse == "générer":
        #     aero = aero_manuel
        # elif perfo_pour_finesse == "importer":
        #     aero = aero_import
        # elif perfo_pour_finesse == "BaseDonnees":
        #     aero = aero_base

        if chemin_txt is None or not os.path.exists(chemin_txt):
            interface.msgbox(f"\nAucun fichier polaire importé trouvé : {chemin_txt}", titre="Erreur")
            #print(f"\nAucun fichier polaire importé trouvé : {chemin_txt}")
        else:
            finesse, finesse_max = aero.calculer_finesse(chemin_txt)
            interface.msgbox(f"\nLa finesse maximale de votre profil est : {finesse_max}", titre="Finesse maximale")

    elif calcul_finesse.lower() == "non":
        pass
    else:
        pass

    # MENU PRINCIPAL POUR LES CONDITIONS
    message = "Voulez-vous tester les performances de votre profil ?"
    options = [
        "0 - Non, passer cette étape",
        "1 - Conditions réelles (vol existant)",
        "2 - Conditions personnalisées",
        "3 - Les deux"
    ]

    reponse = interface.demander_choix(message, options)
    choix_mode = reponse.split(" ")[0]

    # 1) On collecte les conditions dans une liste
    conditions = []
    if choix_mode in ("1", "3"):
        df_vols = choisir_vols(limit=100, sample_n=20)
        # l'index en tête de chaque ligne est déjà celui qu'on affichera
        sel = int(input("\nSélectionnez le vol (numéro) : ").strip())
        row = df_vols.loc[sel]
        alt =row["altitude_m"]
        vit =row["vitesse_m_s"]
        Tstd = 288.15 - 0.0065 * alt
        mach = vit / ((1.4 * 287.05 * Tstd) ** 0.5)
        lat = row["latitude"]
        lon = row["longitude"]
        angle = 2  # ou input()
        conditions.append(("vol_reel", alt, mach, angle, lat, lon))

    if choix_mode in ("2", "3"):
        alt = float(input("\nAltitude personnalisée (m) : "))
        mach = float(input("Mach personnalisé : "))
        angle = float(input("Angle d’attaque perso (°) : "))
        conditions.append(("vol_perso", alt, mach, angle, None, None))

    # Exécution XFoil pour chaque condition
    for tag, alt, mach, angle, lat, lon in conditions:
        cond = ConditionVol(altitude_m=alt, mach=mach, angle_deg=angle,
                            delta_isa=calcul_delta_isa(lat or 0, lon or 0, alt, API_KEY) or 0)
        cond.afficher()
        corde = float(input('Corde (m): '))
        reynolds = cond.calculer_reynolds(vitesse_m_s=mach * (1.4 * 287.05 * cond.temperature_K) ** 0.5, corde_m=corde,
                                          viscosite_kgms=cond.viscosite_kgms, densite_kgm3=cond.densite_kgm3)
        aero_cond = Aerodynamique(nom_profil)
        suffix = '_vol_reel' if tag == 'vol_reel' else '_vol_perso'

        txt_out = os.path.join('data', 'profils_importes' if generation == 'importer' else 'profils_manuels',
                               f"{nom_profil}{suffix}.txt")
        print(' XFoil', tag, txt_out)
        aero_cond.run_xfoil(chemin_dat, reynolds, mach, alpha_start=-15, alpha_end=15, alpha_step=1, output_file=txt_out)
        df_cond = aero_cond.lire_txt_et_convertir_dataframe(txt_out)
        aero_cond.donnees = df_cond
        if tag == 'vol_reel':
            aero_volreel, df_volreel = aero_cond, df_cond
        else:
            aero_volperso, df_volperso = aero_cond, df_cond
        if input('Afficher polaire X ? (Oui/Non) ').strip().lower() == 'oui':
            aero_cond.tracer_polaires_depuis_txt()

    # Collecte des polaires pour comparaison
    polaires = {}
    if aero_import:   polaires['Importé'] = aero_import.donnees
    if aero_manuel:   polaires['Manuel'] = aero_manuel.donnees
    if aero_volreel:  polaires['Vol réel'] = aero_volreel.donnees
    if aero_volperso: polaires['Vol perso'] = aero_volperso.donnees
    if aero_base:   polaires['Base'] = aero_base.donnees

    if len(polaires) >= 2 and input('Superposer polaires ? (Oui/Non) ').strip().lower() == 'oui':
        comparer_polaires(polaires)

    # ===================================
    #         COMPARAISON PROFILS
    # ===================================

    comparaison = interface.demander_choix("Voulez-vous comparer deux profils d'aile?", ["Oui", "Non"])

    if comparaison.lower() == "oui":

        print("\nCHOIX 1:")
        profil_1_obj, profil_1_nom = demande_profil(interface)
        print("\nCHOIX 2:")
        profil_2_obj, profil_2_nom = demande_profil(interface)

        p_1 = Airfoil.depuis_airfoiltools(profil_1_nom)
        p_2 = Airfoil.depuis_airfoiltools(profil_2_nom)

        p_1.tracer_comparaison(p_2)

    elif comparaison.lower() == "non":
        pass
    else:
        pass

    # ===================================
    #         SIMULATION GIVRAGE
    # ===================================

    while True:
        faire_givrage = interface.demander_choix(
            "Voulez-vous simuler un givrage sur un profil ?", ["Oui", "Non"]).strip().lower()
        if faire_givrage in ("oui", "non"):
            break

    if faire_givrage == "oui":
        # 1. Sélection du profil à givrer
        profil_givre_label = interface.demander_choix("Sur quel type de profil veux-tu simuler le givrage?",["Profil importé actuel", "Profil depuis la BaseDonnees"]).strip().lower()

        # --- Profil importé/généré ---
        if profil_givre_label == "profil importé actuel" and aero is not None:
            if generation == "importer":
                profil_a_givrer = profil_obj
                nom_profil_givre = nom_profil
                aero = aero_import
                chemin_dat_givre = chemin_dat

            elif generation == "générer":
                profil_a_givrer = profil_manuel
                nom_profil_givre = nom_profil
                aero = aero_manuel
                chemin_dat_givre = chemin_dat

        # --- Profil depuis la BaseDonnees ---
        elif profil_givre_label == "profil depuis la basedonnees":

            #demander le nom
            nom_profil = interface.demander_texte("Rentrez le nom du profil de la BaseDonnees à givrer (ex : naca2412)").strip().lower()

            essais = gestion.chercher_nom(nom_profil)

            for noms in essais:
                chemin_fichier = f"data/profils_importes/{noms}_coord_profil.dat"
                if os.path.exists(chemin_fichier):
                    for nom_polaire in essais:
                        if os.path.exists(f"data/polaires_importees/{nom_polaire}_coef_aero.txt"):
                            polaire_profil_base = f"{nom_polaire}_coef_aero.txt"
                    coord_profil_base = f"{noms}_coord_profil.dat"
                else:
                    chemin_fichier = f"data/profils_manuels/{noms}_coord_profil.dat"
                    if os.path.exists(chemin_fichier):
                        polaire_profil_base = f"{noms}_coef_aero.txt"
                        coord_profil_base = f"{noms}_coord_profil.dat"
                    else:
                        pass

            # ON a normalement récupéré le nom du fichier pour les coord du profil et sa polaire

            # print("coord_profil_base",coord_profil_base)
            # print("polaire_profil_base",polaire_profil_base)
            #Donne les bons chemins

            dossiers_possibles = [
                "data/profils_importes",
                "data/profils_manuels"
            ]

            # On va cherche le chemin qui mène au fichier : coord_profil_base
            chemin_dat = None
            for dossier in dossiers_possibles:
                chemin_possible = os.path.join(dossier, coord_profil_base)
                #print(chemin_possible)
                if os.path.exists(chemin_possible):
                    chemin_dat = chemin_possible
                    break

            # Charger les coordonnées depuis le fichier .dat
            coordonnees_profil = []
            with open(chemin_dat, "r") as f_dat:
                lignes = f_dat.readlines()[1:]  # Ignorer l'entête (nom du profil)
                for ligne in lignes:
                    parts = ligne.strip().split()
                    if len(parts) == 2:
                        x_str, y_str = parts
                        coordonnees_profil.append((float(x_str), float(y_str)))

            # Création de l'objet Airfoil avec les coordonnées récupérées
            profil_a_givrer = Airfoil(nom_profil, coordonnees_profil)
            nom_profil_givre = nom_profil

            # On refait la même chose pour avoir les fichiers de performances aero
            dossiers_possibles = [
                "data/polaires_importees",
                "data/polaires_xfoil",
            ]
            # On va cherche le chemin qui mène au fichier : polaire_profil_base
            chemin_txt = None
            for dossier in dossiers_possibles:
                chemin_possible = os.path.join(dossier, polaire_profil_base)
                if os.path.exists(chemin_possible):
                    chemin_txt = chemin_possible
                    break

            if chemin_txt is None:
                interface.msgbox(
                    f"Le fichier '{polaire_profil_base}' n'a pas été trouvé dans la BaseDonnees de données, les performances n'ont peut être pas été générées.")

            aero_base = Aerodynamique(nom_profil)
            df_base = aero_base.lire_txt_et_convertir_dataframe(chemin_txt)
            aero_base.donnees = df_base

            aero = aero_base
            aero.donnees = aero_base.donnees

        else:
            interface.msgbox("Aucun profil à givrer sélectionné !", titre="Erreur")
            raise SystemExit

        #  Demande des paramètres de givrage
        ep = float(interface.demander_texte("Épaisseur du givrage (ex : 0.02)").replace(",", ".") or 0.02)
        zone_txt = interface.demander_texte("Zone de givrage x0,x1 (ex : 0.3,0.45)")
        if zone_txt:
            z0, z1 = map(float, zone_txt.replace(" ", "").split(","))
        else:
            z0, z1 = 0.3, 0.45

        #  Choix du mode de conditions pour le givrage
        mode_cond = interface.demander_choix(
            "Pour la simulation givrée, veux-tu :\n- Récupérer des conditions réelles de vol (OpenSky)\n- Saisir manuellement Mach et Reynolds ?",
            ["Conditions de vol réelles", "Saisie manuelle"]
        ).strip().lower()

        """
        if mode_cond == "conditions de vol réelles":
            # == Sélectionner un vol réel
            df_vols = choisir_vols(limit=100, sample_n=20)
            sel = int(input("\nSélectionne le vol (numéro) : ").strip())
            row = df_vols.loc[sel]
            alt = row["altitude_m"]
            vit = row["vitesse_m_s"]
            Tstd = 288.15 - 0.0065 * alt
            mach_givre = vit / ((1.4 * 287.05 * Tstd) ** 0.5)
            corde = float(input("Corde du profil (m) : "))
            # Calcul Reynolds
            rho = 1.225 * (1 - 2.25577e-5 * alt) ** 5.25588  # densité ISA approx
            mu = 1.7894e-5  # viscosité air (kg/ms) approx
            reynolds_givre = (rho * vit * corde) / mu
            print(f"Mach utilisé pour givrage : {mach_givre:.4f}")
            print(f"Reynolds utilisé pour givrage : {reynolds_givre:.0f}")
        
        else:
        """
        # == Saisie manuelle
        reynolds_givre = float(interface.demander_texte("Reynolds pour givrage ? (ex : 50000)") or 50000)
        mach_givre = float(interface.demander_texte("Mach pour givrage ? (ex : 0.1)") or 0.1)

        # Optionnel : afficher immédiatement le profil chargé pour vérifier
        profil_a_givrer.tracer_contour(nom_profil_givre)

        csv_givre, dat_givre = profil_a_givrer.tracer_givrage(epaisseur=ep, zone=(z0, z1))

        txt_givre = f"{nom_profil_givre}_coef_aero_givre.txt"

        txt_givre = os.path.join("data", "polaires_importees", f"{nom_profil_givre}_coef_aero_givre.txt")

        #  Simulation XFoil sur profil givré
        aero_givre = Aerodynamique(nom_profil_givre + "-givre")
        aero_givre.run_xfoil(dat_file=dat_givre, reynolds=reynolds_givre, mach=mach_givre, alpha_start=-5, alpha_end=12, alpha_step=1,output_file=txt_givre)

        # df_givre = aero_givre.lire_txt_et_convertir_dataframe(txt_givre)
        # aero_givre.donnees = df_givre

        # gestion.ajouter_profil(
        #     nom_profil=nom_profil_givre + "-givre",
        #     type_profil="givre",
        #     fichier_coord_csv=None,  # Ne pas redéplacer !
        #     fichier_coord_dat=None,
        #     fichier_polaire_txt=txt_givre,
        #     fichier_polaire_csv=None
        # )

        while True:
            affiche_polaire = interface.demander_choix(
                "Voulez-vous afficher les performances avec le givrage?", ["Oui", "Non"]
            ).strip().lower()
            if affiche_polaire in ("oui", "non"):
                break

        if affiche_polaire == "oui":
            #  Charger la polaire givrée
            if os.path.exists(txt_givre):
                df_givre = aero_givre.lire_txt_et_convertir_dataframe(txt_givre)
                if not df_givre.empty:
                    aero_givre.donnees = df_givre
                    polaires = {}
                    if aero and getattr(aero, "donnees", None) is not None:
                        polaires["Normal"] = aero.donnees
                    polaires["Givré"] = aero_givre.donnees

                    if len(polaires) >= 2:
                        comparer_polaires(polaires)
                    else:
                        aero_givre.tracer_polaires_depuis_txt()

                    print("Courbes normalement affichées")
                else:
                    print("Données givrées vides ou invalides!")
            else:
                print("Fichier givré non trouvé ou erreur.")
        elif affiche_polaire == "non":
            pass

    else:
        print("Fin du programme, sans simulation de givrage.")


