import streamlit as st
import asyncio
import os
import pandas as pd
import matplotlib.pyplot as plt

from gestion_base import GestionBase
from Airfoil import Airfoil
from aerodynamique import Aerodynamique
from VolOpenSkyAsync import fetch_vols, calcul_delta_isa
from ConditionVol import ConditionVol

st.set_page_config(page_title="Projet MGA802 – Interface", layout="centered")
st.title("✈️ Simulation Profile NACA 2D")

API_KEY = "c6bf5947268d141c6ca08f54c7d65b63"
gestion = GestionBase()

# ÉTAPE 1 : Choix du mode
mode = st.radio("1. Choisissez une méthode de création de profil :", ["Importer", "Générer", "Base"])
profil = None

# ÉTAPE 2 : Chargement ou génération du profil
if mode == "Importer":
    code = st.text_input("Code NACA à importer (ex: naca2412-il)")
    if st.button("Importer"):
        profil = Airfoil.depuis_airfoiltools(code)
        csv = profil.sauvegarder_coordonnees(f"data/{code}_coord_profil.csv")
        dat = csv.replace(".csv", ".dat")
        with open(csv) as f1, open(dat, "w") as f2:
            lignes = f1.readlines()
            f2.write(code + "\n")
            for l in lignes[1:]:
                x, y = l.strip().split(",")
                f2.write(f"{float(x):.6f} {float(y):.6f}\n")
        profil.tracer_contour(code)
        st.success("Profil importé et tracé.")
        st.session_state.nom_profil = code
        st.session_state.chemin_dat = dat

elif mode == "Générer":
    nom = st.text_input("Nom du profil")
    m = st.slider("Cambrure m", 0.00, 0.10, 0.02)
    p = st.slider("Position p", 0.00, 1.00, 0.4)
    t = st.slider("Épaisseur t", 0.00, 0.20, 0.12)
    if st.button("Générer"):
        profil = Airfoil(nom, [])
        x1, y1, x2, y2, x, c = profil.naca4_profil()
        csv = profil.enregistrer_profil_manuel_csv(x1, y1, x2, y2, f"data/{nom}_coord_profil.csv")
        dat = profil.enregistrer_profil_format_dat(x1, y1, x2, y2, c, f"data/{nom}_coord_profil.dat")
        profil.tracer_profil_manuel(x1, y1, x2, y2)
        st.success("Profil généré.")
        st.session_state.nom_profil = nom
        st.session_state.chemin_dat = dat

else:
    fichiers = os.listdir("data/profils_manuels") + os.listdir("data/profils_importes")
    noms = sorted(set(f.split("_coord")[0] for f in fichiers if f.endswith(".dat")))
    choix = st.selectbox("Choisissez un profil :", noms)
    if st.button("Charger depuis base"):
        for dossier in ["data/profils_importes", "data/profils_manuels"]:
            chemin = os.path.join(dossier, f"{choix}_coord_profil.dat")
            if os.path.exists(chemin):
                st.session_state.nom_profil = choix
                st.session_state.chemin_dat = chemin
                st.success("Profil chargé.")
                break

# ÉTAPE 3 : Simulation XFOIL
if "chemin_dat" in st.session_state:
    st.divider()
    st.subheader("2. Simulation XFoil")
    mach = st.number_input("Mach", value=0.1)
    re = st.number_input("Reynolds", value=50000)
    alpha_min = st.number_input("Alpha min", value=-5)
    alpha_max = st.number_input("Alpha max", value=15)
    alpha_step = st.number_input("Pas", value=1)

    if st.button("Lancer XFoil"):
        aero = Aerodynamique(st.session_state.nom_profil)
        sortie = f"data/{st.session_state.nom_profil}_xfoil.txt"
        aero.run_xfoil(
            dat_file=st.session_state.chemin_dat,
            reynolds=re,
            mach=mach,
            alpha_start=alpha_min,
            alpha_end=alpha_max,
            alpha_step=alpha_step,
            output_file=sortie
        )
        df = aero.lire_txt_et_convertir_dataframe(sortie)
        aero.donnees = df
        st.session_state.df_polaire = df

        fig, axs = plt.subplots(3, 1, figsize=(6, 8), sharex=True)
        axs[0].plot(df["alpha"], df["CL"]); axs[0].set_ylabel("CL")
        axs[1].plot(df["alpha"], df["CD"]); axs[1].set_ylabel("CD")
        axs[2].plot(df["alpha"], df["CM"]); axs[2].set_ylabel("CM")
        axs[0].set_title("Polaires")
        for ax in axs: ax.grid(True)
        st.pyplot(fig)

# ÉTAPE 4 : Conditions de vol
st.divider()
st.subheader("3. Conditions de vol")

choix_cond = st.radio("Mode de condition de vol", ["Manuel", "Vol réel", "Les deux"])
donnees_vols = []

if choix_cond != "Manuel":
    vols = asyncio.run(fetch_vols(limit=30))
    for i, v in enumerate(vols):
        st.write(f"**{i+1}** - {v.callsign or 'N/A'} | Alt {v.geo_altitude or 0} m | V {v.velocity or 0:.1f} m/s")
    idx = st.number_input("Choix du vol (index)", min_value=1, max_value=len(vols)) - 1
    v = vols[idx]
    alt = v.geo_altitude or 0
    vit = v.velocity or 0
    Tstd = 288.15 - 0.0065 * alt
    mach = vit / ((1.4 * 287.05 * Tstd) ** 0.5)
    rho = 1.225 * (1 - 2.25577e-5 * alt) ** 5.25588
    mu = 1.7894e-5
    corde = 1.0
    reynolds = (rho * vit * corde) / mu
    donnees_vols.append((mach, reynolds))

if choix_cond != "Vol réel":
    mach = st.number_input("Mach (manuel)", value=0.1, key="m1")
    reynolds = st.number_input("Reynolds (manuel)", value=50000, key="r1")
    donnees_vols.append((mach, reynolds))

if st.button("Simuler conditions de vol") and donnees_vols:
    for i, (mach, re) in enumerate(donnees_vols):
        aero = Aerodynamique(f"{st.session_state.nom_profil}_cond_{i}")
        txt = f"data/{st.session_state.nom_profil}_cond_{i}.txt"
        aero.run_xfoil(
            dat_file=st.session_state.chemin_dat,
            reynolds=re,
            mach=mach,
            alpha_start=-5, alpha_end=12, alpha_step=1,
            output_file=txt
        )
        df = aero.lire_txt_et_convertir_dataframe(txt)
        aero.donnees = df
        st.write(f"### Simulation {i+1}")
        st.line_chart(df[["alpha", "CL"]].set_index("alpha"))

# ÉTAPE 5 : Givrage
st.divider()
st.subheader("4. Simulation de givrage")

ep = st.number_input("Épaisseur de givre", value=0.02)
z0, z1 = st.slider("Zone de givrage x0-x1", 0.0, 1.0, (0.3, 0.45))

mode_givre = st.radio("Méthode de condition pour givrage", ["Réelle", "Manuelle"])
if mode_givre == "Réelle":
    vols = asyncio.run(fetch_vols(limit=20))
    for i, v in enumerate(vols):
        st.write(f"{i+1} - {v.callsign or 'N/A'} | Alt {v.geo_altitude or 0:.0f} m | V {v.velocity or 0:.0f} m/s")
    i = st.number_input("Choix vol", min_value=1, max_value=len(vols)) - 1
    v = vols[i]
    alt = v.geo_altitude or 0
    vit = v.velocity or 0
    Tstd = 288.15 - 0.0065 * alt
    mach = vit / ((1.4 * 287.05 * Tstd) ** 0.5)
    rho = 1.225 * (1 - 2.25577e-5 * alt) ** 5.25588
    mu = 1.7894e-5
    corde = 1.0
    reynolds = (rho * vit * corde) / mu
else:
    mach = st.number_input("Mach givré", value=0.1, key="mg")
    reynolds = st.number_input("Reynolds givré", value=50000, key="rg")

if st.button("Lancer givrage"):
    profil_givre = Airfoil.depuis_airfoiltools(st.session_state.nom_profil)
    profil_givre.tracer_givrage(epaisseur=ep, zone=(z0, z1))
    dat_givre = f"data/{st.session_state.nom_profil}_coord_givre.dat"
    txt_givre = f"data/{st.session_state.nom_profil}_givree.txt"
    aero = Aerodynamique(st.session_state.nom_profil + "-givre")
    aero.run_xfoil(
        dat_file=dat_givre,
        reynolds=reynolds,
        mach=mach,
        alpha_start=-5,
        alpha_end=12,
        alpha_step=1,
        output_file=txt_givre
    )
    df = aero.lire_txt_et_convertir_dataframe(txt_givre)
    aero.donnees = df
    fig, axs = plt.subplots(2, 2, figsize=(10, 8))
    axs[0, 0].plot(df["alpha"], df["CL"]); axs[0, 0].set_title("CL")
    axs[0, 1].plot(df["alpha"], df["CD"]); axs[0, 1].set_title("CD")
    axs[1, 0].plot(df["alpha"], df["CM"]); axs[1, 0].set_title("CM")
    axs[1, 1].plot(df["CD"], df["CL"]); axs[1, 1].set_title("CL/CD")
    for ax in axs.flat: ax.grid(True)
    st.pyplot(fig)
