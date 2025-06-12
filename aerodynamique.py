import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

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

        print(f" Fichier texte sauvegardé sous : {nom_fichier}")

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


if __name__ == "__main__":
    nom = input("Nom du profil (ex: n2414-il) : ").strip()
    aero = Aerodynamique(nom)

    # Télécharger le fichier texte depuis AirfoilTools
    nom_fichier_txt = f"polar_{nom}.txt"
    aero.telecharger_et_sauvegarder_txt(nom_fichier_txt)

    # Lire le fichier texte et convertir en DataFrame
    df = aero.lire_txt_et_convertir_dataframe(nom_fichier_txt)

    # Stocker dans l’objet et tracer
    aero.donnees = df
    aero.tracer_polaires_depuis_txt()
    #Lina branche



