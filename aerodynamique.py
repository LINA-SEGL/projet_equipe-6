import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from Airfoil import Airfoil  #  importer ta classe existante

class Aerodynamique:
    def __init__(self, airfoil: Airfoil):
        self.nom_profil = airfoil.nom  # ex: "naca2412-il"


        @classmethod
        def depuis_airfoiltools(cls, code_naca: str):
            url = f"http: // airfoiltools.com / airfoil / details?airfoil ={code_naca.lower()}"
            reponse = requests.get(url)
            if reponse.status_code != 200:
                raise Exception(f"Erreur lors de la récupération du profil NACA {code_naca}")



                lignes = [l for l in response.text.splitlines() if not l.startswith("#")]
                self.donnees = pd.read_csv(StringIO("\n".join(lignes)))
                print(" Données récupérées.")

    def sauvegarder_csv(self, nom_fichier="polaire.csv"):
        if self.donnees is not None:
            self.donnees.to_csv(nom_fichier, index=False)
            print(f"Fichier sauvegardé : {nom_fichier}")

    def tracer_polaires(self):
        if self.donnees is None:
            print("Aucune donnée chargée.")
            return

        plt.figure(figsize=(10, 6))
        plt.plot(self.donnees["Alpha"], self.donnees["Cl"], label="Cl")
        plt.plot(self.donnees["Alpha"], self.donnees["Cd"], label="Cd")
        plt.plot(self.donnees["Alpha"], self.donnees["Cm"], label="Cm")
        plt.xlabel("Angle d'attaque (°)")
        plt.ylabel("Coefficients")
        plt.title(f"Polaires aérodynamiques - {self.nom_profil}")
        plt.legend()
        plt.grid(True)
        plt.show()



""" def recuperer_donnees(self):
        response = requests.get(self.url_csv)
        if response.status_code != 200:
            print("Erreur de récupération")
            return"""