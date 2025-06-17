import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from Airfoil import Airfoil
import subprocess
import os

Dossier_data = "data/"
os.makedirs(Dossier_data, exist_ok=True) # crée le dossier si il n'existe pas

class Aerodynamique:
    """
    Classe pour analyser les performances aérodynamiques d’un profil via AirfoilTools ou XFOIL.

    Attributes:
       nom (str): Nom du profil (ex: 'naca2414-il').
       url_csv (str): URL d’accès au fichier CSV des polaires.
       donnees (pd.DataFrame): Données aérodynamiques extraites ou téléchargées.
    """
    def __init__(self, nom):
        """
        Initialise une instance de la classe avec un nom de profil.

        Args:
            nom (str): Nom du profil AirfoilTools (ex: 'naca4412-il').
        """
        self.nom = nom  # ex: n2414-il
        self.url_csv = f"http://airfoiltools.com/polar/csv?polar=xf-{self.nom}-50000.csv"
        # xf - naca4412 - il - 50000.csv
        self.donnees = None

    def recuperer_donnees_csv(self):
        """
        Télécharge les données polaires (CSV) depuis AirfoilTools et les stocke dans un DataFrame.

        Raises:
            Exception: Si l’URL est invalide ou inaccessible.
        """
        response = requests.get(self.url_csv)
        if response.status_code != 200:
            raise Exception(f"Erreur d'accès au fichier CSV : {self.url_csv}")

        lignes = [l for l in response.text.splitlines() if not l.startswith("#")]
        colonnes = ["alpha", "Cl", "Cd", "Cdp", "Cm", "Top_Xtr", "Bot_Xtr"]
        self.donnees = pd.read_csv(StringIO("\n".join(lignes)), names=colonnes, skiprows=1)
        print(" Données CSV récupérées.")

    def sauvegarder_donnees(self, nom_fichier="polar_airfoil.csv"):
        """
        Sauvegarde les données polaires dans un fichier CSV.

        Args:
            nom_fichier (str): Nom du fichier de sortie.
        """
        if self.donnees is not None:
            chemin = os.path.join(Dossier_data, nom_fichier)
            with open(chemin, "w") as fichier:
                fichier.write(",".join(self.donnees.columns) + "\n")  # ligne d'en-tête
                for _, ligne in self.donnees.iterrows():
                    valeurs = ",".join([str(val) for val in ligne])
                    fichier.write(valeurs + "\n")
            print(f" Données sauvegardées dans {chemin}")

            return chemin

        else:
            print(" Aucune donnée à sauvegarder.")

    def tracer_depuis_csv(self, nom_fichier):
        """
        Lit un fichier CSV brut et trace les courbes Cl, Cd et Cm en fonction de l’angle d’attaque.

        Args:
            nom_fichier (str): Nom du fichier CSV brut.
        """
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

    def telecharger_et_sauvegarder_txt(self, nom_fichier="airfoil_coef_aero.txt", re = 50000):
        """
        Télécharge les performances depuis AirfoilTools (format .txt) et les enregistre.

        Args:
            nom_fichier (str): Nom du fichier de sortie.
        """
        url_txt = f"http://airfoiltools.com/polar/text?polar=xf-{self.nom}-{re}.txt"
        #xf - naca4412 - il - 50000.txt
        response = requests.get(url_txt)

        if response.status_code != 200:
            raise Exception(f"Erreur d'accès au fichier TXT : {url_txt}")

        nom_fichier=f"polar_{self.nom}.txt"
        chemin = os.path.join(Dossier_data, nom_fichier)

        with open(chemin, "w", encoding="utf-8") as fichier:
            fichier.write(response.text)


        print(f"Performances aérodynamiques enregistrés dans le fichier: {chemin}")

        return chemin


    def lire_txt_et_convertir_dataframe(self, nom_fichier_txt):
        """
        Convertit un fichier TXT brut AirfoilTools en DataFrame.

        Args:
            nom_fichier_txt (str): Fichier .txt contenant les données.

        Returns:
            pd.DataFrame: Tableau structuré des performances.
        """
        lignes = []
        commencer = False
        chemin = nom_fichier_txt

        with open(chemin, "r", encoding="utf-8") as f:
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
        """
        Trace les courbes Cl, Cd et Cm à partir des données TXT déjà chargées.
        """
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
        """
        Exécute XFOIL issu d'un fichier .dat et enregistre les résultats dans un fichier texte.

        Args:
            dat_file (str): Chemin vers le fichier .dat du profil.
            reynolds (float): Nombre de Reynolds.
            mach (float): Nombre de Mach.
            alpha_start (float): Angle de départ (°).
            alpha_end (float): Angle de fin (°).
            alpha_step (float): Incrément d’angle (°).
            output_file (str): Fichier de sortie des résultats.
        """
        xfoil_path = os.path.join(os.getcwd(), "xfoil.exe")

        # Script pour XFOIL
        xfoil_input = f"""
        LOAD {dat_file}
        PANE
        OPER
        VISC {reynolds}
        MACH {mach}
        ITER 200
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
                cwd = os.getcwd() # Utilise le dossier actuel automatiquement
            )
            if result.returncode != 0:
                print("Erreur XFOIL :", result.stderr.decode())
            else:
                print(f"Analyse XFOIL terminée. Résultats dans : {output_file}")
                return output_file
        except FileNotFoundError:
            print("XFOIL introuvable. Vérifie le chemin ou l'existence de xfoil.exe.")

    def calculer_finesse(self, nom_fichier):
        """
        Calcule la finesse aérodynamique maximale à partir d’un fichier texte.

        Args:
            nom_fichier (str): Chemin vers le fichier de résultats TXT.

        Returns:
            tuple: (liste des finesses, finesse maximale)
        """
        data = self.lire_txt_et_convertir_dataframe(nom_fichier)

        finesse = (data["CL"] / data["CD"]).tolist()

        finesse_max = max(finesse)

        return finesse, finesse_max
