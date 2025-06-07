from Airfoil import Airfoil  # Demander à l'utilisateur d’entrer le code du profil
nom_profil = input("Entrez le nom exact du profil NACA (ex : naca2412-il) : ")

# Création du profil
profil =Airfoil.depuis_airfoiltools(nom_profil)

# Affichage d’infos
#profil.afficher_resume()

# Sauvegarde des coordonnées
profil.sauvegarder_coordonnees(f"{nom_profil}.csv")

# Affichage graphique
profil.tracer_conteur()