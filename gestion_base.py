import os
import pandas as pd
from datetime import datetime

class GestionBase:
    """
    Classe pour gérer la base de données centrale des profils d'ailes elle crée automatiquement un dossier 'data/' et
    un fichier CSV qui contient un historique des profils enregistrés.
    """

    def __init__(self):

         self.chemin_dossier = "data/"
         self.chemin_fichier = os.path.join(self.chemin_dossier, "donnees_profils.csv")
         self.colonnes = [
              "nom_profil",
              "type_profil",  # importé ou manuel
              "date_creation",
              "fichier_coord_csv",
              "fichier_coord_dat",
              "fichier_polaire_txt",
              "fichier_polaire_csv"
         ]
         self._initialiser_fichier()


    def _initialiser_fichier(self):
        """
        Creé le dossier 'data' et le fichier 'donnees_profils.csv' s'ils n'existent pas.
        """
        os.makedirs(self.chemin_dossier, exist_ok=True)  # on crée le dossier que il n'est pas déja présent

        if not os.path.exists(self.chemin_fichier):  # dans ce cas on creer un tableau vide avec les bonnes colonnes
            df = pd.DataFrame(columns=self.colonnes)
            df.to_csv(self.chemin_fichier, index=False)


    def ajouter_profil(self, nom_profil, type_profil,
                       fichier_coord_csv=None, fichier_coord_dat=None, fichier_polaire_txt=None, fichier_polaire_csv=None):
        """
        Ajoute un nouveau profil à la base de données avec les chemins associés aux fichiersgénérés

        :param nom_profil: nom du profil
        :param type_profil: manuel ou importé
        :param fichier_coord_csv: chemin vers le fichier csv des coordonnées
        :param fichier_coord_dat: chemins vers le fichier .dat de XFOIL
        :param fichier_polaire_txt:chemin vers le fichier texte , résultats de XFOIL
        :param fichier_polaire_csv: chemin vers le fichier csv des polaires de AirfoilTools
        """

        df = pd.read_csv(self.chemin_fichier)

        # création d'un dictionnaire pour la nouvelle ligne

        nouvelle_entree = {
            "nom_profil": nom_profil,
            "type_profil": type_profil,
            "date_creation": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),  # afin de standarisé la date stocké
            "fichier_coord_csv": fichier_coord_csv,
            "fichier_coord_dat": fichier_coord_dat,
            "fichier_polaire_txt": fichier_polaire_txt,
            "fichier_polaire_csv": fichier_polaire_csv
        }

        df = pd.concat([df, pd.DataFrame([nouvelle_entree])],ignore_index=True)  # on ajoute la nouvelle entree a la base de donnée
        df.to_csv(self.chemin_fichier, index=False)  # on retire les index automatique
        print(f"[info] Profil '{nom_profil}' ajouté à la base de données.")


    def afficher_base(self):
        """
        Affiche le contenu actuel de la base de données
        """
        df = pd.read_csv(self.chemin_fichier)
        print(df)

