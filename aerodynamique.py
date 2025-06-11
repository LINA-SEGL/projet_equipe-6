import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO

class Aerodynamique:
    def __init__(self, nom):
        self.nom = nom  # ex: n2414-il
        self.url_csv = f"http://airfoiltools.com/polar/csv?polar=xf-{self.nom}-50000"
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

    def tracer_cd(self):
        plt.plot(self.donnees["alpha"], self.donnees["Cd"], label="Cd", color="red")
        plt.xlabel("Alpha (°)")
        plt.ylabel("Cd")
        plt.title(f"Cd vs Alpha – {self.nom}")
        plt.grid(True)
        plt.show()

if __name__ == "__main__":
    nom = input("Nom du profil (ex: n2414-il) : ").strip()
    aero = Aerodynamique(nom)

    aero.recuperer_donnees_csv()  #  Récupération des données
    aero.sauvegarder_donnees("polar_" + nom + ".csv")
