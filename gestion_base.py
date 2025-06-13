import os
import pandas as pd
from datetime import datetime

class GestionBase:
      """
      Classe pour gérer la base de données centrale des profils d'ailes elle crée automatiquement un dossier 'data/' et 
      un fichier CSV qui contient un historique des profils enregistrés.
      """

     def __init__(self):
         self.chemin_dossier ="data/"
         self.chemin_fichier = os.path.join(self.chemin_dossier, "donnees_profils.csv")
         self.colonnes = [
             "nom_profil",
             "type_profil", # importé ou manuel
             "date_creation",
             "fihchier_coord_csv",
             "fichier_coord_dat",
             "fichier_polaire_txt",
             "fichier_polaire_csv"
         ]
         self.initialiser_fichier