import os
import pandas as pd
from datetime import datetime

classe GestionBase:
      """
      Classe pour gérer la base de données centrale des profils d'ailes elle crée automatiquement un dossier 'data/' et 
      un fichier CSV qui contient un historique des profils enregistrés.
      """
