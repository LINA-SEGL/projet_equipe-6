import streamlit as st
import matplotlib.pyplot as plt

from main import *
# Initialisation
st.set_page_config(page_title="Interface NACA", layout="centered")
st.title("✈️ Interface Streamlit – Simulation profil NACA")
API_KEY = "955814a8002a56c995edec56283f7caf"  # à remplacer si besoin
gestion = GestionBase()

# Session state init
if "profil" not in st.session_state:
    st.session_state.profil = None
    st.session_state.nom = ""
    st.session_state.chemin_dat = ""
    st.session_state.df_polaires = None

mode = st.radio("Choisissez la méthode :", ["Importer", "Générer", "Depuis la BaseDonnees"])

if mode == "Importer":
    code = st.text_input("Nom du profil (ex: naca2412-il)")

    if st.button("Importer le profil") and code:
        try:
            import os


            code = code.strip().lower()  # Pas d'ajout de suffixe automatique !

            st.write(f" Nom du profil demandé : {code}")

            # Étape 1 : Import depuis AirfoilTools
            profil = Airfoil.depuis_airfoiltools(code)

            # Étape 2 : Sauvegarder en CSV (chemin auto)
            chemin_csv = profil.sauvegarder_coordonnees()

            # Étape 3 : Convertir CSV -> DAT (comme dans main.py)
            chemin_dat = chemin_csv.replace("_coord_profil.csv", "_coord_profil.dat")
            with open(chemin_csv, "r") as f_csv, open(chemin_dat, "w") as f_dat:
                lignes = f_csv.readlines()
                f_dat.write(f"{code}\n")
                for ligne in lignes[1:]:  # Ignorer l'en-tête x,y
                    x_str, y_str = ligne.strip().split(",")
                    f_dat.write(f"{float(x_str):.6f} {float(y_str):.6f}\n")

            #  Étape 4 : Tracer dans Streamlit
            x = [pt[0] for pt in profil.coordonnees]
            y = [pt[1] for pt in profil.coordonnees]
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set_aspect("equal")
            ax.set_title(f"Contour du profil {code}")
            ax.grid(True)
            st.pyplot(fig)

            # Sauvegarde session
            st.success(" Profil importé, converti et tracé")
            st.session_state.profil = profil
            st.session_state.nom = code
            st.session_state.chemin_dat = chemin_dat

        except Exception as e:
            st.error(f"Erreur lors de l'import du profil {code} : {type(e).__name__} – {e}")




elif mode == "Générer":
    st.subheader(" Génération d'un profil NACA personnalisé")

    nom_profil = st.text_input("Nom du profil généré")
    m = st.slider("Cambrure (m)", 0.00, 0.10, 0.02, step=0.01)
    p = st.slider("Position (p)", 0.00, 1.00, 0.40, step=0.01)
    t = st.slider("Épaisseur (t)", 0.00, 0.20, 0.12, step=0.01)
    c = st.number_input("Longueur de corde", value=1.0)

    if st.button("Générer le profil"):
        if not nom_profil.strip():
            st.error(" Veuillez entrer un nom de profil.")
        else:
            try:
                import builtins

                #  1. On remplace temporairement l’interface graphique
                class FauxInterface:
                    def demander_parametres(self, _):
                        return {"m": m, "p": p, "t": t, "c": c}

                #  2. On remplace temporairement FenetreInteraction
                from projet_sessionE2025.airfoil import Airfoil

                Airfoil.FenetreInteraction = lambda: FauxInterface()

                # 3. Génération classique
                profil = Airfoil.Airfoil(nom_profil, coordonnees=[])
                x_up, y_up, x_low, y_low, _, c = profil.naca4_profil()

                # 4. Enregistrement
                dossier = "data/profils_manuels"
                os.makedirs(dossier, exist_ok=True)

                chemin_csv = profil.enregistrer_profil_manuel_csv(
                    x_up, y_up, x_low, y_low,
                    nom_fichier=f"{nom_profil}_coord_profil.csv"
                )

                chemin_dat = profil.enregistrer_profil_format_dat(
                    x_up, y_up, x_low, y_low, c,
                    nom_fichier=f"{nom_profil}_coord_profil.dat"
                )

                # 5. Stocker
                st.session_state.profil = profil
                st.session_state.nom = nom_profil
                st.session_state.chemin_dat = chemin_dat

                # 6. Affichage
                fig, ax = plt.subplots()
                ax.plot(x_up, y_up, label="Extrados")
                ax.plot(x_low, y_low, label="Intrados")
                ax.set_aspect("equal")
                ax.set_title(f"Contour du profil {nom_profil}")
                ax.grid(True)
                st.pyplot(fig)

                st.success(" Profil généré et enregistré")

            except Exception as e:
                st.error(f" Erreur : {type(e).__name__} – {e}")


elif mode == "Depuis la BaseDonnees":
    import os

    fichiers = os.listdir("data/profils_manuels") + os.listdir("data/profils_importes")
    noms = sorted(set(f.split("_coord")[0] for f in fichiers if f.endswith(".dat")))

    choix = st.selectbox("Choisissez un profil disponible :", noms)

    if st.button("Charger"):
        chemin = None
        for dossier in ["data/profils_importes", "data/profils_manuels"]:
            chemin_test = os.path.join(dossier, f"{choix}_coord_profil.dat")
            if os.path.exists(chemin_test):
                chemin = chemin_test
                break

        if chemin:
            # Lire le fichier .dat pour extraire les coordonnées
            coordonnees = []
            with open(chemin, "r") as f:
                lignes = f.readlines()
                for ligne in lignes[1:]:  # ignorer le nom en première ligne
                    if ligne.strip():
                        x_str, y_str = ligne.strip().split()
                        coordonnees.append((float(x_str), float(y_str)))

            # Créer l'objet Airfoil avec les coordonnées
            profil = Airfoil(nom=choix, coordonnees=coordonnees)

            # Stocker dans session
            st.session_state.profil = profil
            st.session_state.nom = choix
            st.session_state.chemin_dat = chemin

            st.success(f" Profil {choix} chargé depuis la BaseDonnees")

            # Affichage du contour
            x = [pt[0] for pt in coordonnees]
            y = [pt[1] for pt in coordonnees]
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set_aspect("equal")
            ax.set_title(f"Contour du profil {choix}")
            ax.grid(True)
            st.pyplot(fig)
        else:
            st.error(" Fichier .dat introuvable dans les dossiers.")


# Étape 3 : Simulation aéro
# ───── Si un profil est chargé ─────
if st.session_state.profil and st.session_state.chemin_dat:
    st.subheader(" Tracer les polaires (Cl, Cd, Cm)")

    reynolds = st.number_input("Nombre de Reynolds", value=50000)
    mach = st.number_input("Nombre de Mach", value=0.1)

    if st.button("Lancer l'aero aérodynamique"):
        aero = Aerodynamique(st.session_state.nom)

        # CAS 1 : Profil importé depuis AirfoilTools
        if "-il" in st.session_state.nom:
            try:
                chemin = aero.telecharger_et_sauvegarder_txt(re=reynolds)
                df = aero.lire_txt_et_convertir_dataframe(chemin)
                st.success(" Données récupérées depuis AirfoilTools.")
            except Exception as e:
                st.error(f" Erreur AirfoilTools : {e}")
                df = None

        # CAS 2 : Profil généré ou CAS 3 : Profil chargé depuis la BaseDonnees
        else:
            try:
                chemin = aero.run_xfoil(
                    dat_file=st.session_state.chemin_dat,
                    reynolds=reynolds,
                    mach=mach,
                    output_file=os.path.join("data", "polaires_xfoil", f"{st.session_state.nom}_polar.txt")
                )
                df = aero.lire_txt_et_convertir_dataframe(chemin)
                st.success(" Analyse XFOIL terminée.")
            except Exception as e:
                st.error(f" Erreur XFOIL : {e}")
                df = None

        if df is not None:
            st.session_state.df_polaires = df
            st.success(" Données polaires prêtes à tracer")

# ───── Tracé des polaires si données présentes ─────
if "df_polaires" in st.session_state and st.session_state.df_polaires is not None:
    df = st.session_state.df_polaires
    st.subheader(" Courbes Cl, Cd et Cm")

    fig, axs = plt.subplots(3, 1, figsize=(8, 9), sharex=True)

    axs[0].plot(df["alpha"], df["CL"], color="blue")
    axs[0].set_ylabel("Cl")
    axs[0].grid(True)

    axs[1].plot(df["alpha"], df["CD"], color="red")
    axs[1].set_ylabel("Cd")
    axs[1].grid(True)

    axs[2].plot(df["alpha"], df["CM"], color="green")
    axs[2].set_ylabel("Cm")
    axs[2].set_xlabel("Angle d’attaque (°)")
    axs[2].grid(True)

    st.pyplot(fig)


# Étape 5 : Calcul finesse
    if st.checkbox("Calculer finesse (CL/CD max)"):
        df = st.session_state.df_polaires
        df["finesse"] = df["CL"] / df["CD"]
        max_f = df["finesse"].max()
        st.write(f"### Finesse max : {max_f:.2f}")







# Étape : Conditions de vol (si un profil est chargé)
if st.session_state.profil and st.session_state.chemin_dat:
    st.subheader("📡 Choix des conditions de vol")

    choix = st.selectbox(
        "Voulez-vous tester les performances de votre profil ?",
        [
            "0 - Non, passer cette étape",
            "1 - Conditions réelles (vol existant)",
            "2 - Conditions personnalisées",
            "3 - Les deux"
        ]
    )
    choix_mode = choix.split(" ")[0]
    conditions = []

    if choix_mode in ("1", "3"):
        st.subheader(" Sélection d’un vol réel (via OpenSky)")

        couche = st.radio("Filtrer les vols par couche atmosphérique :", [
            "1 - Troposphère (< 11 000 m)",
            "2 - Stratosphère (≥ 11 000 m)",
            "3 - Aucun filtre"
        ])
        couche_id = couche.split(" ")[0]

        if st.button(" Générer une nouvelle liste de vols filtrés") or "df_vols_ok" not in st.session_state:
            vols = asyncio.run(fetch_vols(limit=100))
            rows = [{
                "icao24": v.icao24,
                "callsign": (v.callsign or "").strip(),
                "origin_country": v.origin_country,
                "altitude_m": v.geo_altitude or 0.0,
                "vitesse_m_s": v.velocity or 0.0,
                "latitude": v.latitude,
                "longitude": v.longitude
            } for v in vols]
            df = pd.DataFrame(rows)

            if couche_id == "1":
                df_filt = df[df["altitude_m"] < 11000]
            elif couche_id == "2":
                df_filt = df[df["altitude_m"] >= 11000]
            else:
                df_filt = df

            if df_filt.empty:
                st.warning(" Aucun vol trouvé pour ce filtre. Essayez à nouveau.")
            else:
                df_sample = df_filt.sample(n=min(20, len(df_filt))).reset_index(drop=True)
                st.session_state.df_vols_proposee = df_sample
                st.session_state.df_vols_ok = False

        if "df_vols_proposee" in st.session_state:
            st.dataframe(st.session_state.df_vols_proposee)
            valider = st.radio(" Cette liste vous convient-elle ?", ["Oui", "Non"], key="valide_liste")
            if valider == "Oui":
                st.session_state.df_vols_ok = True

        if st.session_state.get("df_vols_ok", False):
            df_vols = st.session_state.df_vols_proposee
            idx = st.number_input("Sélectionnez le vol (index)", min_value=0, max_value=len(df_vols)-1, step=1, key="idx_vol")
            row = df_vols.loc[idx]
            alt = row["altitude_m"]
            vit = row["vitesse_m_s"]
            Tstd = 288.15 - 0.0065 * alt
            mach = vit / ((1.4 * 287.05 * Tstd) ** 0.5)
            angle = st.number_input("Angle d’attaque (°)", value=2.0, key="angle_reel")
            lat = row["latitude"]
            lon = row["longitude"]
            conditions.append(("vol_reel", alt, mach, angle, lat, lon))

    if choix_mode in ("2", "3"):
        st.subheader(" Conditions personnalisées")
        alt = st.number_input("Altitude (m)", value=1000.0, key="alt_perso")
        mach = st.number_input("Mach", value=0.2, key="mach_perso")
        angle = st.number_input("Angle d’attaque (°)", value=2.0, key="angle_perso")
        conditions.append(("vol_perso", alt, mach, angle, None, None))

    corde = st.number_input("Longueur de corde (m)", value=0.3)
    st.session_state.conditions_pretes = []

    for tag, alt, mach, angle, lat, lon in conditions:
        st.markdown(f"###  Résumé pour : **{'Vol réel' if tag == 'vol_reel' else 'Vol perso'}**")
        cond = ConditionVol(
            altitude_m=alt,
            mach=mach,
            angle_deg=angle,
            delta_isa=calcul_delta_isa(lat or 0, lon or 0, alt, API_KEY) or 0
        )
        vitesse = mach * (1.4 * 287.05 * cond.temperature_K) ** 0.5
        reynolds = cond.calculer_reynolds(
            vitesse_m_s=vitesse,
            corde_m=corde,
            viscosite_kgms=cond.viscosite_kgms,
            densite_kgm3=cond.densite_kgm3
        )

        st.markdown(f"""
        - Altitude : {alt:.1f} m  
        - Mach : {mach:.3f}  
        - Angle d'attaque : {angle:.1f}°  
        - Température : {cond.temperature_K:.2f} K  
        - Densité : {cond.densite_kgm3:.4f} kg/m³  
        - Viscosité : {cond.viscosite_kgms:.6e} kg/m·s  
        - Reynolds : {reynolds:.2e}  
        - ΔISA : {cond.delta_isa:.1f} K  
        - Corde : {corde:.2f} m
        """)

        st.session_state.conditions_pretes.append({
            "tag": tag,
            "cond": cond,
            "re": reynolds,
            "mach": mach
        })

    if st.button(" Lancer XFOIL avec ces conditions"):
        polaires = {}
        aero_volreel, aero_volperso = None, None

        for item in st.session_state.conditions_pretes:
            tag = item["tag"]
            cond = item["cond"]
            reynolds = item["re"]
            mach = item["mach"]

            aero = Aerodynamique(st.session_state.nom)
            suffix = "_vol_reel" if tag == "vol_reel" else "_vol_perso"
            dossier = "profils_importes" if "-il" in st.session_state.nom else "profils_manuels"
            txt_out = os.path.join("data", dossier, f"{st.session_state.nom}{suffix}.txt")

            try:
                aero.run_xfoil(
                    dat_file=st.session_state.chemin_dat,
                    reynolds=reynolds,
                    mach=mach,
                    alpha_start=-15,
                    alpha_end=15,
                    alpha_step=1,
                    output_file=txt_out
                )
                df = aero.lire_txt_et_convertir_dataframe(txt_out)
                aero.donnees = df

                #  Affichage séparé
                st.markdown(f"### Résultats : **{'Vol réel' if tag == 'vol_reel' else 'Vol perso'}**")
                st.dataframe(df)
                fig = aero.tracer_polaires_depuis_txt()
                if fig:
                    st.pyplot(fig, clear_figure=True)

                if tag == "vol_reel":
                    aero_volreel = aero
                else:
                    aero_volperso = aero

            except Exception as e:
                st.error(f" Échec de la simulation XFoil : {e}")

        #  Collecte globale des polaires disponibles
        polaires = {}
        if 'aero_import' in locals() and aero_import:
            polaires["Importé"] = aero_import.donnees
        if 'aero_manuel' in locals() and aero_manuel:
            polaires["Manuel"] = aero_manuel.donnees
        if aero_volreel:
            polaires["Vol réel"] = aero_volreel.donnees
        if aero_volperso:
            polaires["Vol perso"] = aero_volperso.donnees

        if len(polaires) >= 2:
            st.markdown("###  Comparaison des polaires disponibles")
            if st.button("Afficher les courbes Cl / Cd / Cm"):
                st.write("→ Données prêtes :", list(polaires.keys()))
                fig = comparer_polaires(polaires)
                st.pyplot(fig, clear_figure=True)

#  givrage...
# ============================
#         SIMULATION GIVRAGE
# ============================

st.subheader("❄️ Simulation de givrage")

faire_givrage = st.radio(
    "Voulez-vous simuler un givrage sur un profil ?",
    ["Non", "Oui"], index=0
)

if faire_givrage == "Oui":
    profil_givre_label = st.radio(
        "Sur quel type de profil veux-tu simuler le givrage ?",
        ["Profil importé actuel", "Profil depuis la BaseDonnees"]
    )

    profil_a_givrer = None
    nom_profil_givre = ""
    chemin_dat_givre = ""
    aero_normale = None

    if profil_givre_label == "Profil importé actuel" and "aero_import" in st.session_state:
        profil_a_givrer = st.session_state.profil_obj_import
        nom_profil_givre = st.session_state.nom
        chemin_dat_givre = st.session_state.chemin_dat
        aero_normale = st.session_state.aero_import

    elif profil_givre_label == "Profil depuis la BaseDonnees":
        nom_profil_base = st.text_input("Nom du profil de la BaseDonnees à givrer (ex: naca2412)").strip().lower()
        if nom_profil_base:
            nom_profil_givre = f"{nom_profil_base}-il"
            coord_profil_base = f"{nom_profil_givre}_coord_profil.dat"
            chemin_dat_givre = None

            for dossier in ["data/profils_importes", "data/profils_manuels"]:
                chemin_test = os.path.join(dossier, coord_profil_base)
                if os.path.exists(chemin_test):
                    chemin_dat_givre = chemin_test
                    break

            if chemin_dat_givre:
                profil_a_givrer = Airfoil.depuis_airfoiltools(nom_profil_givre)
                polaire_txt = f"{nom_profil_givre}_coef_aero.txt"
                chemin_polaire_base = None

                for dossier in ["data/polaires_importees", "data/polaires_xfoil"]:
                    test = os.path.join(dossier, polaire_txt)
                    if os.path.exists(test):
                        chemin_polaire_base = test
                        break

                if chemin_polaire_base:
                    aero_normale = Aerodynamique(nom_profil_givre)
                    aero_normale.donnees = aero_normale.lire_txt_et_convertir_dataframe(chemin_polaire_base)

    if profil_a_givrer:
        ep = st.number_input("Épaisseur du givrage (fraction corde)", value=0.02, step=0.01)
        zone_txt = st.text_input("Zone de givrage x0,x1 (ex : 0.3,0.45)", value="0.3,0.45")

        try:
            z0, z1 = map(float, zone_txt.replace(" ", "").split(","))
        except:
            st.warning("Format de zone invalide, valeurs par défaut utilisées.")
            z0, z1 = 0.3, 0.45

        mode_cond = st.radio(
            "Conditions pour le givrage :",
            ["Conditions de vol réelles", "Saisie manuelle"]
        )

        if mode_cond == "Conditions de vol réelles":
            if st.button(" Sélectionner un vol réel pour givrage"):
                df_vols = asyncio.run(fetch_vols(100))
                df_vols = pd.DataFrame([{
                    "icao24": v.icao24,
                    "altitude_m": v.geo_altitude or 0.0,
                    "vitesse_m_s": v.velocity or 0.0
                } for v in df_vols])

                if not df_vols.empty:
                    st.session_state.df_vols_givre = df_vols.sample(n=min(20, len(df_vols)))

        if "df_vols_givre" in st.session_state:
            st.dataframe(st.session_state.df_vols_givre)
            idx = st.number_input("Index du vol", min_value=0, max_value=len(st.session_state.df_vols_givre)-1)
            row = st.session_state.df_vols_givre.loc[idx]
            alt = row["altitude_m"]
            vit = row["vitesse_m_s"]
            corde = st.number_input("Longueur de corde (m)", value=0.3)
            Tstd = 288.15 - 0.0065 * alt
            mach_givre = vit / ((1.4 * 287.05 * Tstd) ** 0.5)
            rho = 1.225 * (1 - 2.25577e-5 * alt) ** 5.25588
            mu = 1.7894e-5
            reynolds_givre = (rho * vit * corde) / mu

        else:
            reynolds_givre = st.number_input("Reynolds pour givrage", value=50000)
            mach_givre = st.number_input("Mach pour givrage", value=0.1)

        if st.button(" Lancer la simulation givrée"):
            profil_a_givrer.tracer_givrage(epaisseur=ep, zone=(z0, z1))
            dir_givre = os.path.join("data", "profils_givre")
            dat_givre = os.path.join(dir_givre, f"{nom_profil_givre}_coord_givre.dat")
            txt_givre = os.path.join(dir_givre, f"{nom_profil_givre}_givree.txt")

            aero_givre = Aerodynamique(nom_profil_givre + "-givre")
            try:
                aero_givre.run_xfoil(
                    dat_file=dat_givre,
                    reynolds=reynolds_givre,
                    mach=mach_givre,
                    alpha_start=-5, alpha_end=12, alpha_step=1,
                    output_file=txt_givre
                )

                if os.path.exists(txt_givre):
                    df_givre = aero_givre.lire_txt_et_convertir_dataframe(txt_givre)
                    if not df_givre.empty:
                        aero_givre.donnees = df_givre
                        polaires = {}
                        if aero_normale and getattr(aero_normale, "donnees", None) is not None:
                            polaires["Normal"] = aero_normale.donnees
                        polaires["Givré"] = aero_givre.donnees

                        if len(polaires) >= 2:
                            fig = comparer_polaires(polaires)
                            st.pyplot(fig)
                        else:
                            fig = aero_givre.tracer_polaires_depuis_txt()
                            if fig:
                                st.pyplot(fig)
                    else:
                        st.error("Données de la simulation givrée sont vides.")
                else:
                    st.error("Fichier de données givrées introuvable.")
            except Exception as e:
                st.error(f"Erreur durant la simulation givrée : {e}")
