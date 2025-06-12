import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from Airfoil import Airfoil
import subprocess
import os

class Aerodynamique:

    def __init__(self, nom):
        self.nom = nom  # ex: n2414-il
        self.url_csv = f"http://airfoiltools.com/polar/csv?polar=xf-{self.nom}-50000.csv"
       # xf - naca4412 - il - 50000.csv
        self.donnees = None

    def recuperer_donnees_csv(self):
        response = requests.get(self.url_csv)
        if response.status_code != 200:
            raise Exception(f"Erreur d'accès au fichier CSV : {self.url_csv}")

        lignes = [l for l in response.text.splitlines() if not l.startswith("#")]
        colonnes = ["alpha", "Cl", "Cd", "Cdp", "Cm", "Top_Xtr", "Bot_Xtr"]
        self.donnees = pd.read_csv(StringIO("\n".join(lignes)), names=colonnes, skiprows=1)
        print(" Données CSV récupérées.")

    def sauvegarder_donnees(self, nom_fichier="polar_airfoil.csv"):
        if self.donnees is not None:
            with open(nom_fichier, "w") as fichier:
                fichier.write(",".join(self.donnees.columns) + "\n")  # ligne d'en-tête
                for _, ligne in self.donnees.iterrows():
                    valeurs = ",".join([str(val) for val in ligne])
                    fichier.write(valeurs + "\n")
            print(f" Données sauvegardées dans {nom_fichier}")
        else:
            print(" Aucune donnée à sauvegarder.")

    def tracer_depuis_csv(self, nom_fichier):
        try:
            # Lire le fichier brut ligne par ligne
            with open(nom_fichier, "r", encoding="utf-8") as f:
                lignes = f.readlines()

            # Trouver l'index de la vraie ligne d'en-tête (celle qui commence par Alpha ou alpha)
            index_en_tete = -1
            for i, ligne in enumerate(lignes):
                if ligne.strip().lower().startswith("alpha"):
                    index_en_tete = i
                    break

            if index_en_tete == -1:
                print(" Ligne d'en-tête non trouvée.")
                return

            # Lire dans pandas à partir de la bonne ligne
            from io import StringIO
            contenu_utilisable = "".join(lignes[index_en_tete:])
            df = pd.read_csv(StringIO(contenu_utilisable))

            # Nettoyage si besoin
            df.columns = [c.strip().lower() for c in df.columns]  # ex: alpha, cl, cd, cm...
            df = df.astype(float)

            # Tracer
            fig, axs = plt.subplots(3, 1, figsize=(10, 9), sharex=True)

            axs[0].plot(df["alpha"], df["cl"], label="Cl", color="blue")
            axs[0].set_ylabel("Cl")
            axs[0].legend()
            axs[0].grid(True)

            axs[1].plot(df["alpha"], df["cd"], label="Cd", color="red")
            axs[1].set_ylabel("Cd")
            axs[1].legend()
            axs[1].grid(True)

            axs[2].plot(df["alpha"], df["cm"], label="Cm", color="green")
            axs[2].set_xlabel("Angle d'attaque α (°)")
            axs[2].set_ylabel("Cm")
            axs[2].legend()
            axs[2].grid(True)

            fig.suptitle(f"Polaires depuis : {nom_fichier}")
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f" Erreur : {e}")

    def telecharger_et_sauvegarder_txt(self, nom_fichier="polar_airfoil.txt"):

        url_txt = f"http://airfoiltools.com/polar/text?polar=xf-{self.nom}-50000.txt"
        #xf - naca4412 - il - 50000.txt
        response = requests.get(url_txt)

        if response.status_code != 200:
            raise Exception(f"Erreur d'accès au fichier TXT : {url_txt}")

        with open(nom_fichier, "w", encoding="utf-8") as fichier:
            fichier.write(response.text)

        print(f"Performances aérodynamiques enregistrés dans le fichier: {nom_fichier}")

    def lire_txt_et_convertir_dataframe(self, nom_fichier_txt):
        lignes = []
        commencer = False

        with open(nom_fichier_txt, "r", encoding="utf-8") as f:
            for ligne in f:
                ligne = ligne.strip()
                if not ligne:
                    continue  # ignorer les lignes vides
                if ligne.lower().startswith("alpha"):
                    commencer = True
                    lignes.append(ligne)
                elif commencer:
                    if all(c in "- " for c in ligne):
                        continue  # ignorer ligne de séparation visuelle
                    lignes.append(ligne)

        # Transformation en DataFrame
        colonnes = lignes[0].split()
        data = [l.split() for l in lignes[1:]]

        df = pd.DataFrame(data, columns=colonnes)
        df = df.astype(float)
        return df

    def tracer_polaires_depuis_txt(self):
        if self.donnees is None:
            print("Aucune donnée à tracer.")
            return

        fig, axes = plt.subplots(3, 1, figsize=(5, 7), sharex=True)  # 3 lignes, 1 colonne

        # 1. Cl
        axes[0].plot(self.donnees["alpha"], self.donnees["CL"], color="blue")
        axes[0].set_ylabel("Cl")
        axes[0].set_title(f"Polaires du profil : {self.nom}")
        axes[0].grid(True)

        # 2. Cd
        axes[1].plot(self.donnees["alpha"], self.donnees["CD"], color="red")
        axes[1].set_ylabel("Cd")
        axes[1].grid(True)

        # 3. Cm
        axes[2].plot(self.donnees["alpha"], self.donnees["CM"], color="green")
        axes[2].set_ylabel("Cm")
        axes[2].set_xlabel("Angle d'attaque α (°)")
        axes[2].grid(True)

        plt.tight_layout()
        plt.show()

    def run_xfoil(self, dat_file, reynolds, mach, alpha_start=-5, alpha_end=15, alpha_step=1, output_file="polar_output.txt"):
        xfoil_path = os.path.join(os.getcwd(), "xfoil.exe")

        # Script pour XFOIL
        xfoil_input = f"""
    LOAD {dat_file}
    PANE
    OPER
    VISC {reynolds}
    MACH {mach}
    ITER 100
    PACC
    {output_file}
    
    ASEQ {alpha_start} {alpha_end} {alpha_step}
    QUIT
    """

        try:
            result = subprocess.run(
                [xfoil_path],
                input=xfoil_input.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=r"C:\Users\train\Documents\Cours\ETS\MGA802\projet_sessionE2025"
            )
            if result.returncode != 0:
                print("Erreur XFOIL :", result.stderr.decode())
            else:
                print(f"Analyse XFOIL terminée. Résultats dans : {output_file}")
        except FileNotFoundError:
            print("XFOIL introuvable. Vérifie le chemin ou l'existence de xfoil.exe.")

    def calculer_finesse(self, nom_fichier):

        data = self.lire_txt_et_convertir_dataframe(nom_fichier)

        finesse = (data["CL"] / data["CD"]).tolist()

        finesse_max = max(finesse)

        return finesse, finesse_max
