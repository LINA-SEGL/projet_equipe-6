import streamlit as st
import matplotlib.pyplot as plt

from main import *
# Initialisation
st.set_page_config(page_title="Interface NACA", layout="centered")
st.title("✈️ Interface Streamlit – Simulation profil NACA")
API_KEY = "955814a8002a56c995edec56283f7caf"  # à remplacer si besoin
gestion = GestionBase()

# Comparaison de deux profils avec conditions personnalisées
import os
import glob

chemins = ["data/profils_importes", "data/profils_manuels"]
noms_profils = []
for dossier in chemins:
    fichiers = glob.glob(os.path.join(dossier, "*_coord_profil.dat"))
    noms_profils += [os.path.basename(f).split("_coord")[0] for f in fichiers]
noms_profils = sorted(set(noms_profils))


# Session state init
if "profil" not in st.session_state:
    st.session_state.profil = None
    st.session_state.nom = ""
    st.session_state.chemin_dat = ""
    st.session_state.df_polaires = None

    for var in ["aero_import", "aero_manuel", "aero_base", "aero_volperso", "aero_volreel"]:
        if var not in st.session_state:
            st.session_state[var] = None

mode = st.radio("Choisissez la méthode :", ["Importer", "Générer", "Depuis la BaseDonnees"])
st.session_state["methode_utilisee"] = mode

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

    # Ajout : checkbox pour forcer la régénération
    forcer_xfoil = st.checkbox("🔄 Forcer la régénération XFOIL")

    if st.button("Lancer l'aero aérodynamique"):
        aero = Aerodynamique(st.session_state.nom)
        methode = st.session_state.get("methode_utilisee", "")

        if methode == "Importer":
            try:
                chemin = aero.telecharger_et_sauvegarder_txt(re=reynolds)
                df = aero.lire_txt_et_convertir_dataframe(chemin)
                st.success(" Données récupérées depuis AirfoilTools.")
            except Exception as e:
                st.error(f" Erreur AirfoilTools : {e}")
                df = None



        elif methode == "Générer":
            try:
                chemin_polaire = os.path.join("data", "polaires_xfoil", f"{st.session_state.nom}_polar.txt")
                if forcer_xfoil and os.path.exists(chemin_polaire):
                    os.remove(chemin_polaire)
                    st.info("Ancien fichier supprimé. Nouvelle analyse XFOIL en cours...")

                chemin = aero.run_xfoil(
                    dat_file=st.session_state.chemin_dat,
                    reynolds=reynolds,
                    mach=mach,
                    output_file=chemin_polaire
                )
                df = aero.lire_txt_et_convertir_dataframe(chemin)
                st.success("✅ Analyse XFOIL terminée.")
            except Exception as e:
                st.error(f"❌ Erreur XFOIL : {e}")
                df = None


        elif methode == "Depuis la BaseDonnees":
            try:
                chemin_polaire = os.path.join("data", "polaires_importees", f"{st.session_state.nom}_coef_aero.txt")

                if not os.path.exists(chemin_polaire):
                    raise FileNotFoundError(f"Fichier introuvable : {chemin_polaire}")

                df = aero.lire_txt_et_convertir_dataframe(chemin_polaire)
                st.success("✅ Données de la base récupérées avec succès.")
            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture depuis la base : {e}")

        else:
            st.error(f"❌ Méthode inconnue : {methode}")

            # Si on a des données valides : sauvegarde et affichage
        if df is not None:
            st.session_state.df_polaires = df
            st.success("📊 Données prêtes à tracer.")

# ───── Tracé des polaires si données présentes ─────
if "df_polaires" in st.session_state and st.session_state.df_polaires is not None:
    df = st.session_state.df_polaires
    st.subheader(" Courbes Cl, Cd et Cm")
    st.write("Aperçu des données :", df.head())  # Debug

    try:
        plt.clf()
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
    except Exception as e:
        st.error(f"Erreur dans le tracé : {e}")


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
            #dossier = "profils_importes" if "-il" in st.session_state.nom else "profils_manuels"
            dossier = "profils_importes"
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
                    st.session_state.aero_volreel = aero
                else:
                    st.session_state.aero_volperso = aero


            except Exception as e:
                st.error(f" Échec de la simulation XFoil : {e}")

    # 📊 Collecte des polaires disponibles
    # ============================
    polaires = {}

    # Polaire de base selon le mode choisi
    if mode == "Importer" and st.session_state.aero_import is not None:
        polaires["Importé"] = st.session_state.aero_import.donnees
    elif mode == "Générer" and st.session_state.aero_manuel is not None:
        polaires["Manuel"] = st.session_state.aero_manuel.donnees
    elif mode == "Depuis la base" and st.session_state.aero_base is not None:
        polaires["Base"] = st.session_state.aero_base.donnees

    # Ajout des polaires simulées
    if st.session_state.aero_volreel is not None:
        polaires["Vol réel"] = st.session_state.aero_volreel.donnees
    if st.session_state.aero_volperso is not None:
        polaires["Vol perso"] = st.session_state.aero_volperso.donnees

    # Superposition si au moins 2 polaires
    if len(polaires) >= 2:
        st.markdown("### Comparaison des polaires disponibles")
        if st.button("Afficher les courbes CL / CD / CM"):
            try:
                st.write(" Profils détectés pour comparaison :", list(polaires.keys()))
                for nom, df in polaires.items():
                    st.write(f" Aperçu du profil : {nom}")
                    st.write(df.head())
                fig = comparer_polaires(polaires)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Erreur lors de l'affichage : {e}")



st.markdown("## Comparaison de deux profils NACA")

choix_mode = st.radio("Méthode de simulation :", ["Conditions personnalisées", "VOL REEL OPENSKY"], key="choix_mode_comparaison")

# Chargement des noms disponibles
import os
import glob

chemins = ["data/profils_importes", "data/profils_manuels"]
noms_profils = []
for dossier in chemins:
    fichiers = glob.glob(os.path.join(dossier, "*_coord_profil.dat"))
    noms_profils += [os.path.basename(f).split("_coord")[0] for f in fichiers]
noms_profils = sorted(set(noms_profils))

# Sélection des profils à comparer
col1, col2 = st.columns(2)
with col1:
    profil1_nom = st.selectbox("Choisissez le 1er profil :", noms_profils, key="profil1_key")
with col2:
    profil2_nom = st.selectbox("Choisissez le 2e profil :", noms_profils, key="profil2_key")

# Contrôle pour éviter d'afficher l'erreur avant simulation
if "simulation_effectuee" not in st.session_state:
    st.session_state.simulation_effectuee = False

def charger_et_simuler(nom_profil, reynolds, mach, alpha_start, alpha_end, alpha_step, forcer=False):
    chemin =  None
    for dossier in chemins:
        test = os.path.join(dossier, f"{nom_profil}_coord_profil.dat")
        if os.path.exists(test):
            chemin = test
            break
    if not chemin:
        st.error(f"❌ Fichier .dat introuvable pour {nom_profil}")
        return None

    coordonnees = []
    with open(chemin, "r") as f:
        for ligne in f.readlines()[1:]:
            if ligne.strip():
                try:
                    x, y = map(float, ligne.strip().split())
                    coordonnees.append((x, y))
                except:
                    continue

    profil = Airfoil(nom_profil, coordonnees)
    aero = Aerodynamique(nom_profil)

    dossier = "profils_importes"
    txt_path = os.path.join("data", dossier, f"{nom_profil}_simule_coef_aero.txt")
    aero.fichier_resultat = txt_path

    if forcer and os.path.exists(txt_path):
        os.remove(txt_path)

    try:
        aero.run_xfoil(
            dat_file=chemin,
            reynolds=reynolds,
            mach=mach,
            alpha_start=alpha_start,
            alpha_end=alpha_end,
            alpha_step=alpha_step,
            output_file=txt_path
        )
        df = aero.lire_txt_et_convertir_dataframe(txt_path)
        aero.donnees = df
    except Exception as e:
        st.error(f"❌ Erreur XFOIL pour {nom_profil} : {e}")
        aero.donnees = None

    return aero

if choix_mode == "Conditions personnalisées":
    st.markdown("### Paramètres pour XFoil")
    Re = st.number_input("Nombre de Reynolds", value=1_000_000)
    Mach = st.number_input("Mach", value=0.1)
    alpha_start = st.number_input("Alpha début (°)", value=-5)
    alpha_end = st.number_input("Alpha fin (°)", value=15)
    alpha_step = st.number_input("Pas d’alpha (°)", value=1)
    corde = st.number_input("Longueur de corde (m)", value=1.0)
    forcer_xfoil = st.checkbox("🔄 Forcer la régénération des résultats XFOIL", value=False)

    if st.button("Simuler et comparer", key="simuler_comparer_btn"):
        aero1 = charger_et_simuler(profil1_nom, Re, Mach, alpha_start, alpha_end, alpha_step, forcer=forcer_xfoil)
        aero2 = charger_et_simuler(profil2_nom, Re, Mach, alpha_start, alpha_end, alpha_step, forcer=forcer_xfoil)
        st.session_state.simulation_effectuee = True

elif choix_mode == "VOL REEL OPENSKY":
    st.subheader(" Sélection d’un vol réel (via OpenSky)")

    couche = st.radio("Filtrer les vols par couche atmosphérique :", [
        "1 – Troposphère (< 11 000 m)",
        "2 – Stratosphère (≥ 11 000 m)",
        "3 – Aucun filtre"
    ], key="filtre_couche_opensky")
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
        st.success(f"Conditions extraites : Mach = {mach:.3f}, Altitude = {alt:.1f} m")

        alpha_start = -15
        alpha_end = +15
        alpha_step = 1
        Re = 1e6
        forcer_xfoil = st.checkbox("🔄 Forcer la régénération des résultats XFOIL", value=False)

        if st.button("Simuler et comparer", key="simuler_comparer_reel"):
            aero1 = charger_et_simuler(profil1_nom, Re, mach, alpha_start, alpha_end, alpha_step, forcer=forcer_xfoil)
            aero2 = charger_et_simuler(profil2_nom, Re, mach, alpha_start, alpha_end, alpha_step, forcer=forcer_xfoil)
            st.session_state.simulation_effectuee = True

if 'aero1' in locals() and 'aero2' in locals() and aero1 and aero2 and aero1.donnees is not None and aero2.donnees is not None:
    df1 = aero1.donnees
    df2 = aero2.donnees

    fig, axs = plt.subplots(2, 2, figsize=(10, 8))

    axs[0, 0].plot(df1["alpha"], df1["CL"], label=profil1_nom)
    axs[0, 0].plot(df2["alpha"], df2["CL"], label=profil2_nom)
    axs[0, 0].set_title("CL vs α")
    axs[0, 0].set_xlabel("α (°)")
    axs[0, 0].set_ylabel("Cl")
    axs[0, 0].grid(True)

    axs[0, 1].plot(df1["alpha"], df1["CD"], label=profil1_nom)
    axs[0, 1].plot(df2["alpha"], df2["CD"], label=profil2_nom)
    axs[0, 1].set_title("CD vs α")
    axs[0, 1].set_xlabel("α (°)")
    axs[0, 1].set_ylabel("Cd")
    axs[0, 1].grid(True)

    axs[1, 0].plot(df1["alpha"], df1["CM"], label=profil1_nom)
    axs[1, 0].plot(df2["alpha"], df2["CM"], label=profil2_nom)
    axs[1, 0].set_title("CM vs α")
    axs[1, 0].set_xlabel("α (°)")
    axs[1, 0].set_ylabel("Cm")
    axs[1, 0].grid(True)

    axs[1, 1].plot(df1["CD"], df1["CL"], label=profil1_nom)
    axs[1, 1].plot(df2["CD"], df2["CL"], label=profil2_nom)
    axs[1, 1].set_title("CL vs CD")
    axs[1, 1].set_xlabel("Cd")
    axs[1, 1].set_ylabel("Cl")
    axs[1, 1].grid(True)

    for ax in axs.flat:
        ax.legend()

    plt.tight_layout()
    st.pyplot(fig)
elif st.session_state.get("simulation_effectuee", False):
    st.error("❌ Données indisponibles pour l’un des profils. Vérifie si XFOIL a bien généré les résultats.")



# ============================================
    # SUPERPOSITION DE DEUX PROFILS NACA
    # ============================================

st.subheader("Comparaison de deux profils NACA")

profils_disponibles = sorted(set(f.split("_coord")[0] for dossier in ["data/profils_importes", "data/profils_manuels"]
                                 for f in os.listdir(dossier) if f.endswith(".dat")))

profil_1 = st.selectbox("Choisissez le 1er profil", profils_disponibles, key="profil1")
profil_2 = st.selectbox("Choisissez le 2e profil", profils_disponibles, key="profil2")

if st.button("Comparer les deux profils"):
    try:
        def charger_coord(nom):
            for dossier in ["data/profils_importes", "data/profils_manuels"]:
                chemin = os.path.join(dossier, f"{nom}_coord_profil.dat")
                if os.path.exists(chemin):
                    with open(chemin, "r") as f:
                        lignes = f.readlines()[1:]  # sauter la première ligne
                        return [(float(x), float(y)) for x, y in (ligne.strip().split() for ligne in lignes)]
            return None

        coords1 = charger_coord(profil_1)
        coords2 = charger_coord(profil_2)

        if coords1 and coords2:
            fig, ax = plt.subplots()
            x1, y1 = zip(*coords1)
            x2, y2 = zip(*coords2)
            ax.plot(x1, y1, label=profil_1, linewidth=2)
            ax.plot(x2, y2, label=profil_2, linestyle="--", linewidth=2)
            ax.set_title("Superposition des contours des profils")
            ax.set_aspect("equal")
            ax.grid(True)
            ax.legend()
            st.pyplot(fig)
        else:
            st.error("Impossible de charger les deux profils sélectionnés.")

    except Exception as e:
        st.error(f"Erreur lors de la comparaison : {e}")





# ===================================
#         SIMULATION GIVRAGE
# ===================================
import os
import glob

st.subheader("❄️ Simulation de givrage sur un profil NACA")
choix = st.radio("Choix du profil :", ["Profil importé actuel", "Profil depuis la base"])

# Chargement des noms de profils depuis les dossiers
chemins = ['data/profils_importes', 'data/profils_manuels']
noms_profils = []
for dossier in chemins:
    fichiers = glob.glob(os.path.join(dossier, "*_coord_profil.dat"))
    noms_profils += [os.path.basename(f).split("_coord")[0] for f in fichiers]
noms_profils = sorted(set(noms_profils))

# Interface de sélection
if choix == "Profil depuis la base":
    nom_profil = st.selectbox("Nom du profil dans la base :", noms_profils)
else:
    nom_profil = st.session_state.nom

epaisseur = st.text_input("Épaisseur du givrage (ex: 0.02)", "0.02").replace(",", ".")
z0 = st.text_input("x0 (zone de givrage)", "0.30").replace(",", ".")
z1 = st.text_input("x1 (zone de givrage)", "0.45").replace(",", ".")
reynolds_givre = st.text_input("Reynolds pour givrage", "50000")
mach_givre = st.text_input("Mach pour givrage", "0.30")

# ✅ Ajout : option pour forcer XFOIL
forcer_xfoil = st.checkbox("🔄 Forcer la régénération XFOIL", key="forcer_xfoil_givre")

if st.button("Lancer simulation givrage"):
    try:
        ep = float(epaisseur)
        z0, z1 = float(z0), float(z1)
        reynolds_givre = float(reynolds_givre)
        mach_givre = float(mach_givre)

        # === Récupérer le profil à givrer ===
        if choix == "Profil depuis la base":
            essais = gestion.chercher_nom(nom_profil)
            profil_a_givrer = None
            for noms in essais:
                chemin = f"data/profils_importes/{noms}_coord_profil.dat"
                if os.path.exists(chemin):
                    with open(chemin, "r") as f:
                        coord = [(float(x), float(y)) for x, y in [line.strip().split() for line in f.readlines()[1:]]]
                        profil_a_givrer = Airfoil(nom_profil, coord)
                        chemin_dat = chemin
                        break
        else:
            profil_a_givrer = st.session_state.profil
            chemin_dat = st.session_state.chemin_dat

        if profil_a_givrer is None:
            st.error("Profil non trouvé.")
        else:
            # === Givrer le profil ===
            csv_givre, dat_givre = profil_a_givrer.tracer_givrage(epaisseur=ep, zone=(z0, z1))

            # === Simulation du profil givré ===
            txt_givre = os.path.join("data", "polaires_importees", f"{nom_profil}_coef_aero_givre.txt")
            aero_givre = Aerodynamique(nom_profil + "-givre")
            if forcer_xfoil and os.path.exists(txt_givre):
                os.remove(txt_givre)

            aero_givre.run_xfoil(dat_file=dat_givre, reynolds=reynolds_givre, mach=mach_givre,
                                 alpha_start=-15, alpha_end=15, alpha_step=1, output_file=txt_givre)

            # === Simulation du profil normal ===
            txt_normal = os.path.join("data", "polaires_importees", f"{nom_profil}_coef_aero_normal.txt")
            aero_normal = Aerodynamique(nom_profil + "-normal")
            if forcer_xfoil and os.path.exists(txt_normal):
                os.remove(txt_normal)

            aero_normal.run_xfoil(dat_file=chemin_dat, reynolds=reynolds_givre, mach=mach_givre,
                                      alpha_start=-15, alpha_end=15, alpha_step=1, output_file=txt_normal)
            if not os.path.exists(txt_normal):
                st.error("⚠️ Le fichier XFoil normal n’a pas été généré.")
            else:
                st.success("✅ Fichier XFoil normal bien généré.")
            # === Tracer les contours ===
            import matplotlib.pyplot as plt
            with open(chemin_dat, "r") as f:
                coords_norm = [(float(x), float(y)) for x, y in [l.strip().split() for l in f.readlines()[1:]]]
            with open(dat_givre, "r") as f:
                coords_givre = [(float(x), float(y)) for x, y in [l.strip().split() for l in f.readlines()[1:]]]

            x_norm, y_norm = zip(*coords_norm)
            x_givre, y_givre = zip(*coords_givre)

            plt.figure(figsize=(8, 3))
            plt.plot(x_norm, y_norm, label="Profil normal", linewidth=2)
            plt.plot(x_givre, y_givre, label="Profil givré", linestyle="--", linewidth=2)
            plt.xlabel("x")
            plt.ylabel("y")
            plt.title(f"Comparaison des contours – {nom_profil}")
            plt.legend()
            plt.axis("equal")
            st.pyplot(plt)

            # === Lecture et comparaison des polaires ===
            df_norm = aero_normal.lire_txt_et_convertir_dataframe(txt_normal)
            df_givre = aero_givre.lire_txt_et_convertir_dataframe(txt_givre)

            #  Vérification que les deux objets sont bien des DataFrame et non None
            if isinstance(df_norm, pd.DataFrame) and not df_norm.empty and isinstance(df_givre,
                                                                                      pd.DataFrame) and not df_givre.empty:
                aero_normal.donnees = df_norm
                aero_givre.donnees = df_givre

                fig, axs = plt.subplots(2, 2, figsize=(12, 8))
                axs[0, 0].plot(df_norm["alpha"], df_norm["CL"], label="Normal")
                axs[0, 0].plot(df_givre["alpha"], df_givre["CL"], label="Givré")
                axs[0, 0].set_title("CL vs Alpha")

                axs[0, 1].plot(df_norm["alpha"], df_norm["CD"], label="Normal")
                axs[0, 1].plot(df_givre["alpha"], df_givre["CD"], label="Givré")
                axs[0, 1].set_title("CD vs Alpha")

                axs[1, 0].plot(df_norm["alpha"], df_norm["CM"], label="Normal")
                axs[1, 0].plot(df_givre["alpha"], df_givre["CM"], label="Givré")
                axs[1, 0].set_title("CM vs Alpha")

                finesse_norm = df_norm["CL"] / df_norm["CD"]
                finesse_givre = df_givre["CL"] / df_givre["CD"]
                axs[1, 1].plot(df_norm["alpha"], finesse_norm, label="Normal")
                axs[1, 1].plot(df_givre["alpha"], finesse_givre, label="Givré")
                axs[1, 1].set_title("Finesse (CL/CD) vs Alpha")

                for ax in axs.flat:
                    ax.set_xlabel("α")
                    ax.legend()
                    ax.grid(True)

                plt.tight_layout()
                st.pyplot(fig)

                st.success("Simulation givrage terminée. Résultats générés et comparés.")
            else:
                st.error("Données givrées ou normales invalides.")
    except Exception as e:
        st.error(f"Erreur pendant la simulation : {e}")






