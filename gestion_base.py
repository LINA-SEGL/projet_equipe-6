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

        def ajouter_profil(self, nom_profil, type_profil,
                           fichier_coord_csv=None, fichier_coord_dat=None,fichier_polaire_txt=None,fichier_polaire_csv=None):

           """
           Ajoute un nouveau profil à la base de données avec les chemins associés aux fichiersgénérés

           :param nom_profil: nom du profil
           :param type_profil: manuel ou importé
           :param fichier_coord_csv: chemin vers le fichier csv des coordonnées
           :param fichier_coord_dat: chemins vers le fichier .dat de XFOIL
           :param fichier_polaire_txt:chemin vers le fichier texte , résultats de XFOIL
           :param fichier_polaire_csv: chemin vers le fichier csv des polaires de AirfoilTools
           """

           df=pd.read_csv(self.chemin_fichier)