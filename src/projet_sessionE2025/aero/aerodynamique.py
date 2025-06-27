import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
import subprocess
import os
from pathlib import Path

# ─────────── dossier pour les imports AirfoilTools ───────────
# (tous les .txt générés par telecharger_et_sauvegarder_txt iront ici)
dossier_data = "data/"
sous_dossier_data_import = os.path.join("data", "profils_importes")
sous_dossier_data_genere = os.path.join("data", "profils_manuels")

os.makedirs(sous_dossier_data_import, exist_ok=True)
# ─────────────────────────────────────────────────────────────

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
            chemin = os.path.join(dossier_data, "profils_importes", nom_fichier)
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

    def telecharger_et_sauvegarder_txt(self, re=50000):
        """
        Télécharge la polaire aérodynamique (format .txt) depuis AirfoilTools.
        Teste toutes les combinaisons possibles de nom de profil jusqu'à trouver un fichier valide.
        """
        suffixes = ['', '-il', '-sa', '-sm', 'h-sa', 'sm-il', '-jf','a-il']
        prefixes = ['naca', 'n']
        lettres_variante = ['h', 'sm']

        code_brut = self.nom.lower().replace("naca", "").replace("n", "")

        essais = []

        # Patterns classiques
        for prefix in prefixes:
            for suffix in suffixes:
                essais.append(f"{prefix}{code_brut}{suffix}")
        essais.append(code_brut)  # Tester aussi le code brut seul

        # Ajout de variantes avec 'h' et 'sm' pour les profils à 4 chiffres
        if code_brut.isdigit() and len(code_brut) == 4:
            for prefix in prefixes:
                for lettre in lettres_variante:
                    for suffix in suffixes:
                        essais.append(f"{prefix}{code_brut}{lettre}{suffix}")
            for lettre in lettres_variante:
                essais.append(f"{code_brut}{lettre}")
                for suffix in suffixes:
                    essais.append(f"{code_brut}{lettre}{suffix}")

        dossier = os.path.join("data", "polaires_importees")
        os.makedirs(dossier, exist_ok=True)

        for code_url in essais:
            url_txt = f"http://airfoiltools.com/polar/text?polar=xf-{code_url}-{re}.txt"
            response = requests.get(url_txt)
            contenu = response.text
            # Robustesse : ne prendre que les vrais fichiers contenant des données
            if (response.status_code == 200 and
                    "Invalid airfoil name" not in contenu and
                    "Error" not in contenu and
                    "Unknown polar file" not in contenu and
                    len(contenu.splitlines()) > 5):
                nom_fichier = f"{code_url}_coef_aero.txt"
                chemin = os.path.join(dossier, nom_fichier)
                with open(chemin, "w", encoding="utf-8") as fichier:
                    fichier.write(contenu)
                print(f"[INFO] Polaire trouvée et enregistrée: {url_txt}")
                return chemin

        raise Exception(f"Aucune version de polaire trouvée pour le profil {self.nom} (Re={re})")

    def lire_txt_et_convertir_dataframe(self, nom_fichier_txt):
        """
        Convertit un fichier TXT brut AirfoilTools en DataFrame.

        Args:
            nom_fichier_txt (str): Fichier .txt contenant les données.

        Returns:
            pd.DataFrame: Tableau structuré des performances.
        """
        import os
        lignes = []
        commencer = False
        chemin = nom_fichier_txt

        # 1. Vérifie que le fichier existe AVANT d'ouvrir
        if not os.path.exists(chemin):
            print(f"[ERREUR] Fichier non trouvé : {chemin}")
            # Affiche le contenu du dossier parent pour debug
            print("Fichiers disponibles :", os.listdir(os.path.dirname(chemin)))
            return None

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

        # 2. Vérifie qu'il y a des données à parser
        if not lignes:
            print(f"[ERREUR] Aucun bloc de données détecté dans : {chemin}")
            return None

        try:
            colonnes = lignes[0].split()
            data = [l.split() for l in lignes[1:]]

            # 3. Check cohérence colonnes/données
            if not data or len(data[0]) != len(colonnes):
                print(f"[ERREUR] Données mal formatées dans : {chemin}")
                print("En-tête :", colonnes)
                print("Première ligne de data :", data[0] if data else "Aucune donnée")
                return None

            df = pd.DataFrame(data, columns=colonnes)
            df = df.astype(float)
            print(f"[OK] Données extraites : {len(df)} lignes, colonnes : {df.columns.tolist()}")
            return df

        except Exception as e:
            print(f"[ERREUR] Exception lors du parsing du fichier {chemin} : {e}")
            return None

    def tracer_polaires_depuis_txt(self):
        """
        Trace les courbes Cl, Cd et Cm à partir des données TXT déjà chargées.
        """
        if self.donnees is None:
            print("Aucune donnée à tracer.")
            return
        plt.clf()  # <-- Nettoie explicitement la figure précédente

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

        return fig

    def run_xfoil(self, dat_file, reynolds, mach, alpha_start=-6, alpha_end=15, alpha_step=0.5, output_file="polar_output.txt"):
        """
        Exécute XFOIL issu d'un fichier .dat et enregistre les résultats dans un fichier texte.

           Args:More actions
            dat_file (str): Chemin vers le fichier .dat du profil.
            reynolds (float): Nombre de Reynolds.
            mach (float): Nombre de Mach.
            alpha_start (float): Angle de départ (°).
            alpha_end (float): Angle de fin (°).
            alpha_step (float): Incrément d’angle (°).
            output_file (str): Fichier de sortie des résultats.
        """
        #xfoil_path = Path(__file__).parent.parent.parent / "xfoil.exe"  # Remonte jusqu'à la racine
        xfoil_path = os.path.join(os.getcwd(), "xfoil.exe")

        # Script pour XFOIL
        xfoil_input = f"""
        LOAD {dat_file}
        MDES
        FILT
        EXEC
        
        PANE
        OPER
        ITER 70
        RE {reynolds}
        VISC {reynolds}
        MACH {mach}
        PACCMore actions
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
