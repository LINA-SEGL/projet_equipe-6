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
             "fichier_coord_csv",
             "fichier_coord_dat",
             "fichier_polaire_txt",
             "fichier_polaire_csv"
         ]
         self.initialiser_fichier()

        def _initialiser_fichier(self):
             """
             Creé le dossier 'data' et le fichier 'donnees_profils.csv' s'ils n'existent pas.
             """
             os.makedirs(self.chemin_dossier,exist_ok=True) #on crée le dossier que il n'est pas déja présent

             if not os.path.exists(self.chemin_fichier):  #dans ce cas on creer un tableau vide avec les bonnes colonnes
                 df=pd.DataFrame(columns=self.colonnes)
                 df.to_csv(self.chemin_fichier, index=False)