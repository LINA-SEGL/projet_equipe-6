#On importe la bibliothèque requests pour faire une requête HTTP vers le site AirfoilTools
import requests
import matplotlib.pyplot as plt
## Class Airfoil va représenter un profil NACA avec ses cordonnées
class Airfoil:
    def __init__(self, nom, coordonnees):
        self.nom = nom # Nom de profile
        self.coordonnees = coordonnees # une liste de tuples (x, y) représentant les points du contour de l’aile

    @classmethod
    def depuis_airfoiltools(cls, code_naca: str):
        url = f"http://airfoiltools.com/airfoil/seligdatfile?airfoil={code_naca.lower()}"
        reponse = requests.get(url)

        if reponse.status_code != 200:
            raise Exception(f"Erreur lors de la récupération du profil NACA {code_naca}")

        lignes = reponse.text.strip().splitlines()
        coordonnees = []

        for ligne in lignes[1:]:  # ignorer la première ligne (titre)
            try:
                parties = ligne.strip().split()
                x = float(parties[0])
                y = float(parties[1])
                coordonnees.append((x, y))
            except (IndexError, ValueError):
                continue  # ignorer les lignes mal formatées

        return cls(nom=f"NACA{code_naca}", coordonnees=coordonnees)

    # affichade d'un petit résumé nom + nmbr de points
   # def afficher_resume(self):
       # print(f"Profil : {self._nom} | Nombre de points : {len(self.coordonnees)}")

    #  Stocker les coordonnées
    def sauvegarder_coordonnees(self, nom_fichier="coordonnees.csv"):
        with open(nom_fichier, "w") as fichier:
            fichier.write("x,y\n")
            for x, y in self.coordonnees:
                fichier.write(f"{x},{y}\n")

    # Tracer le contoour
    def tracer_conteur(self):
        x_vals = [point[0] for point in self.coordonnees]
        y_vals = [point[1] for point in self.coordonnees]

        plt.figure(figsize=(8, 4))
        plt.plot(x_vals, y_vals, marker='o', linewidth=1)
        plt.title(f"Profil aérodynamique {self.nom}")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.axis("equal")  # pour que l’échelle soit respectée
        plt.grid(True)
        plt.show()

