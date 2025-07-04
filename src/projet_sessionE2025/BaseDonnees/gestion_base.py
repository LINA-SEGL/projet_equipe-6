# ce module sert à etablir une data BaseDonnees avec des profils déjà manipuler et de la manipuler
import os
import pandas as pd
from datetime import datetime
import os

# chemins globaux pour l'organisation des fichiers

# Dossier contenant le fichier gestion_base.py
MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dossier "projet_sessionE2025" = deux niveaux au-dessus de gestion_base.py
PACKAGE_ROOT = os.path.abspath(os.path.join(MODULE_DIR, ".."))

# On définit le dossier data à l’intérieur de "projet_sessionE2025"
Dossier_data = os.path.join(PACKAGE_ROOT, "data")

#Dossier_data = "data"

profils_importes = os.path.join(Dossier_data, "profils_importes")
profils_manuels = os.path.join(Dossier_data, "profils_manuels")
polaires_xfoil = os.path.join(Dossier_data, "polaires_xfoil")
polaires_importees = os.path.join(Dossier_data, "polaires_importees")
profils_givre = os.path.join(Dossier_data, "profils_givre")


class GestionBase:
    """
    Classe pour gérer la BaseDonnees de données centrale des profils d'ailes elle crée automatiquement un dossier 'data/' et
    un fichier CSV qui contient un historique des profils enregistrés.
    """
    def __init__(self):
        self.chemin_dossier = Dossier_data
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
        self._creer_dossiers_utiles()

    def _initialiser_fichier(self):

        """
        Creé le dossier 'data' et le fichier 'donnees_profils.csv' s'ils n'existent pas.
        """
        os.makedirs(self.chemin_dossier, exist_ok=True)  # on crée le dossier que il n'est pas déja présent

        if not os.path.exists(self.chemin_fichier):  # dans ce cas on creer un tableau vide avec les bonnes colonnes
            df = pd.DataFrame(columns=self.colonnes)
            df.to_csv(self.chemin_fichier, index=False)

    def _creer_dossiers_utiles(self):

        """
        Crée les sous-dossiers nécessaires dans 'data/' pour organiser les fichiers.
        """
        sous_dossiers = [
            "profils_importes",
            "profils_manuels",
            "polaires_xfoil",
            "polaires_importees",
            "profils_givre"

        ]
        for dossier in sous_dossiers:
            os.makedirs(os.path.join(self.chemin_dossier, dossier), exist_ok=True)

    # def _deplacer_fichier(self, chemin_fichier, dossier_cible):
    #
    #     """
    #     Déplace un fichiers vers un sous-dossier spécifique de 'data/'
    #     :param chemin_fichier: chemin initial du fichier
    #     :param dossier_cible: nom du sous dossier (ex: 'profils_manuels')
    #     :return: chemin du fichier déplacé
    #     """
    #
    #     if chemin_fichier is None:
    #         return None
    #
    #     if not os.path.exists(chemin_fichier):
    #         print(f"[alerte] Fichier introuvable : {chemin_fichier}")
    #         return None
    #
    #     nom_fichier = os.path.basename(chemin_fichier)
    #     nouveau_chemin = os.path.join(self.chemin_dossier, dossier_cible, nom_fichier)
    #
    #     if os.path.abspath(chemin_fichier) == os.path.abspath(nouveau_chemin):
    #         return nouveau_chemin  # déjà à la bonne place
    #
    #     os.replace(chemin_fichier, nouveau_chemin)
    #     return nouveau_chemin
    #
    #     return None

    # def ajouter_profil(self, nom_profil, type_profil,
    #                    fichier_coord_csv=None, fichier_coord_dat=None,
    #                    fichier_polaire_txt=None, fichier_polaire_csv=None):
    #
    #     """
    #     Ajoute un nouveau profil à la BaseDonnees de données avec les chemins associés aux fichiersgénérés
    #
    #     :param nom_profil: nom du profil
    #     :param type_profil: manuel ou importé et givre
    #     :param fichier_coord_csv: chemin vers le fichier csv des coordonnées
    #     :param fichier_coord_dat: chemins vers le fichier .dat de XFOIL
    #     :param fichier_polaire_txt:chemin vers le fichier texte , résultats de XFOIL
    #     :param fichier_polaire_csv: chemin vers le fichier csv des polaires de AirfoilTools
    #     """
    #
    #     df = pd.read_csv(self.chemin_fichier)
    #
    #     # on déplace chaque fichier dans son sous-dossier
    #
    #     if type_profil == "manuel":
    #         dossier_coords = "profils_manuels"
    #     elif type_profil == "importé":
    #         dossier_coords = "profils_importes"
    #     elif type_profil == "givre":
    #         dossier_coords = "profils_givre"
    #     else:
    #         dossier_coords = "profils_importes"  # par défaut
    #     chemin_coord_csv = self._deplacer_fichier(fichier_coord_csv, dossier_coords)
    #     chemin_coord_dat = self._deplacer_fichier(fichier_coord_dat, dossier_coords)
    #     chemin_polaire_txt = self._deplacer_fichier(fichier_polaire_txt, "polaires_importees")
    #     chemin_polaire_csv = self._deplacer_fichier(fichier_polaire_csv, "polaires_xfoil")
    #
    #
    #     # création d'un dictionnaire pour la nouvelle ligne
    #
    #     nouvelle_entree = {
    #         "nom_profil": nom_profil,
    #         "type_profil": type_profil,
    #         "date_creation": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),  # afin de standarisé la date stocké
    #         "fichier_coord_csv": chemin_coord_csv,
    #         "fichier_coord_dat": chemin_coord_dat,
    #         "fichier_polaire_txt": chemin_polaire_txt,
    #         "fichier_polaire_csv": chemin_polaire_csv
    #     }
    #
    #     df = pd.concat([df, pd.DataFrame([nouvelle_entree])],ignore_index=True)  # on ajoute la nouvelle entree a la BaseDonnees de donnée
    #     df.to_csv(self.chemin_fichier, index=False)  # on retire les index automatique
    #     #print(f"[info] Profil '{nom_profil}' ajouté à la BaseDonnees de données.")


    # def afficher_base(self):
    #     """
    #     Affiche le contenu actuel de la BaseDonnees de données
    #     """
    #     df = pd.read_csv(self.chemin_fichier)
    #     print(df)
    #
    #
    # def charger_base(self):
    #     """
    #     Charge et retourne la BaseDonnees de données des profils sous forme de DataFrame.
    #     """
    #     return pd.read_csv(self.chemin_fichier)


    # def supprimer_profil(self, nom_profil):
    #     """
    #     Supprime un profil de la BaseDonnees de données et ses fichiers associers
    #     :param nom_profil: Nom du profil à supprimer
    #     """
    #     df = pd.read_csv(self.chemin_fichier)
    #
    #     #On verifie si le profil est dans la BaseDonnees
    #     filtre = df["nom_profil"] == nom_profil
    #     if not filtre.any():
    #         print(f"[alerte] Aucun profil nommé '{nom_profil}' trouvé dans la BaseDonnees.")
    #         return False
    #
    #     #recuperation des fichiers à supprimer
    #     fichiers_a_supprimer = df.loc[filtre,[   # pour selectionner les bonnes lignes et colonnes
    #          "fichier_coord_csv",
    #          "fichier_coord_dat",
    #          "fichier_polaire_txt",
    #          "fichier_polaire_csv"
    #     ]].values.flatten() #retourne un tableau NumPy et le rend unidimensionnel
    #
    #     for chemin in fichiers_a_supprimer:
    #         if isinstance(chemin, str) and os.path.exists(chemin):   #pour verifier que la variable chemin est bien un chemin de fichier valide
    #             try:
    #                 os.remove(chemin)
    #             except Exception as e:
    #                 print(f"[alerte] Erreur lors de la suppression du fichier '{chemin}': {e}")
    #
    #
    #     #mise à jour de la BaseDonnees
    #     df = df[~filtre]
    #     df.to_csv(self.chemin_fichier, index=False)
    #     print(f"[info] Profil '{nom_profil}' supprimé de la BaseDonnees et fichiers associés supprimés")


    #rechercher si un profil existe deja

    # def profil_existe(self, nom_profil):
    #     """
    #     Vérifie si un profil existe deja dans la BaseDonnees de données
    #     :param nom_profil: Nom du profil a rechercher
    #     :return: True s'il est present falsie sinon
    #     """
    #
    #     df = pd.read_csv(self.chemin_fichier)
    #     return nom_profil in df ["nom_profil"].values

    def chercher_nom(self, nom_profil):

        # Nettoyage de l'entrée utilisateur
        code_naca = nom_profil.strip().lower()
        suffixes = ['', '-il', '-sa', '-sm', 'h-sa', 'sm-il', '-jf', 'a-il']
        prefixes = ['naca', 'n']
        lettres_variante = ['h', 'sm']

        # On retire tous les préfixes pour garder le cœur numérique
        code_brut = code_naca.replace("naca", "").replace("n", "")
        essais = set()

        # 1. Patterns classiques
        for prefix in prefixes:
            for suffix in suffixes:
                essais.add(f"{prefix}{code_brut}{suffix}")
        essais.add(code_brut)  # Ex : '2412' ou '22112'

        # 2. Si code brut 4 ou 5 chiffres, on tente des variantes avec 'h', 'sm'
        if code_brut.isdigit() and len(code_brut) in (4, 5):
            for prefix in prefixes:
                for lettre in lettres_variante:
                    for suffix in suffixes:
                        essais.add(f"{prefix}{code_brut}{lettre}{suffix}")
            for lettre in lettres_variante:
                essais.add(f"{code_brut}{lettre}")
                for suffix in suffixes:
                    essais.add(f"{code_brut}{lettre}{suffix}")

        # 3. On tente aussi le code NACA original (en cas d'entrée custom)
        essais.add(code_naca)

        return essais