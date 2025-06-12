import requests
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO
from Airfoil import Airfoil  #  importer ta classe existante
import subprocess
import os

class Aerodynamique:

    def __init__(self, nom):
        self.nom = nom  # Nom de profil

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

    def run_xfoil(self, dat_file, alpha_start=-5, alpha_end=15, alpha_step=1, output_file="polar_output.txt"):
        xfoil_path = os.path.join(os.getcwd(), "xfoil.exe")

        # Script pour XFOIL
        xfoil_input = f"""
    LOAD {dat_file}
    PANE
    OPER
    VISC 1000000
    ITER 100
    PACC
    {output_file}
    
    ASEQ {alpha_start} {alpha_end} {alpha_step}
    PACC
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
                print(f"✅ Analyse XFOIL terminée. Résultats dans : {output_file}")
        except FileNotFoundError:
            print("XFOIL introuvable. Vérifie le chemin ou l'existence de xfoil.exe.")