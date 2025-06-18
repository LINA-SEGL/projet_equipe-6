import requests
import matplotlib.pyplot as plt
import numpy as np
import csv
from gestion_base import *
import os
from interaction_graphique import *

class Airfoil:
    """
    Représente un profil aérodynamique (type NACA ou autre) à partir de ses coordonnées ou généré manuellement.

    Attributes:
        nom (str): Nom du profil.
        coordonnees (list of tuple): Liste de couples (x, y) représentant les points du contour.
    """
    def __init__(self, nom, coordonnees):
        """
        Initialise un objet Airfoil avec un nom et une liste de coordonnées.

        Args:
            nom (str): Nom du profil (ex: 'NACA2412').
            coordonnees (liste de tuples): Coordonnées (x, y) du contour.
        """
        self.nom = nom
        self.coordonnees = coordonnees

    @classmethod
    def depuis_airfoiltools(cls, code_naca: str):
        """
        Télécharge un profil NACA depuis le site AirfoilTools.

        Args:
            code_naca (str): Code NACA (ex: '2412').

        Returns:
            Airfoil: Instance du profil téléchargé.

        Raises:
            Exception: Si la récupération échoue.
        """
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

        return cls(nom=f"{code_naca}", coordonnees=coordonnees)

    def sauvegarder_coordonnees(self, nom_fichier=None):
        """
        Enregistre les coordonnées du profil importé dans data/profils_importes/.
        Args:
            nom_fichier (str, optionnel) : nom du fichier CSV à écrire.
        Returns:
            str : chemin complet du fichier écrit.
        """
        if nom_fichier is None:
            nom_fichier = f"{self.nom}_coord_profil.csv"

        chemin = os.path.join(profils_importes, nom_fichier)
        os.makedirs(profils_importes, exist_ok=True)

        with open(chemin, "w", newline="") as f:
            f.write("x,y\n")
            for x, y in self.coordonnees:
                f.write(f"{x},{y}\n")

        return chemin

    # Tracer le contour

    def tracer_contour(self, nom_profil):
        """
        Trace le contour du profil aérodynamique.

        Args:
            nom_profil (str): Titre du graphe affiché.
        """
        x_vals = [point[0] for point in self.coordonnees]
        y_vals = [point[1] for point in self.coordonnees]

        plt.figure(figsize=(8, 4))
        plt.plot(x_vals, y_vals, marker='o', linewidth=1)
        plt.title(f"Profil aérodynamique {nom_profil}")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.axis("equal")  # pour que l’échelle soit respectée
        plt.grid(True)
        plt.show()

    def naca4_profil(self):
        """
        Génère un profil NACA 4 chiffres à partir de formules analytiques.

        Returns:
            tuple: (x_upper, y_upper, x_lower, y_lower, x, c) — coordonnées des surfaces et paramètres.
        """
        interface = FenetreInteraction()

        params = interface.demander_parametres({
            "m": "Cambrure du profil (entre 0 et 1)",
            "p": "Position de la cambrure maximale (entre 0 et 1)",
            "t": "Épaisseur maximale (entre 0 et 1)",
            "c": "Longueur de corde du profil"
        })

        m = params["m"]
        p = params["p"]
        t = params["t"]
        c = params["c"]

        # m = float(input("Indiquer la cambrure du profil (entre 0 et 1): "))
        # p = float(input("Indiquer la position de la cambrure maximale du profil (entre 0 et 1): "))
        # t = float(input("Indiquer l'épaisseur maximale du profil (entre 0 et 1): "))
        # c = float(input("Indiquer la longueur de corde du profil: "))
        n_points = 18 #int(input("Indiquer le nombre de points souhaité pour le tracé du demi-profil: "))

        # m = 0.04
        # p = 0.6
        # t = 0.08
        # c = 1
        # n_points = 18

        # Discrétisation le long de x (on utilise un espacement cosinus pour affiner vers le bord d'attaque)
        beta = np.linspace(0.0, np.pi, n_points)
        x = c * (0.5 * (1 - np.cos(beta)))

        # Calcul de l'épaisseur relative yt(x)
        yt = (t / 0.2) * c * (0.2969 * np.sqrt(x / c)
                              - 0.1260 * (x / c)
                              - 0.3516 * (x / c) ** 2
                              + 0.2843 * (x / c) ** 3
                              - 0.1015 * (x / c) ** 4)

        # Calcul de la cambrure yc(x) et de dyc/dx
        yc = np.zeros_like(x)
        dyc_dx = np.zeros_like(x)
        coordonnees = []
        for i in range(len(x)):
            xi = x[i] / c
            if xi < p:  #Coordonnées profil sans cambrure
                yc[i] = (m / p ** 2) * (2 * p * xi - xi ** 2) * c
                dyc_dx[i] = (2 * m / p ** 2) * (p - xi)
            else:   #Coordonnées profil après la cambrure
                yc[i] = (m / (1 - p) ** 2) * (1 - 2 * p + 2 * p * xi - xi ** 2) * c
                dyc_dx[i] = (2 * m / (1 - p) ** 2) * (p - xi)

        # Calcul de theta(x)
        theta = np.arctan(dyc_dx)

        # Coordonnées des surfaces supérieure et inférieure
        x_upper = x - yt * np.sin(theta)
        y_upper = yc + yt * np.cos(theta)

        x_lower = x + yt * np.sin(theta)
        y_lower = yc - yt * np.cos(theta)

        return x_upper, y_upper, x_lower, y_lower, x, c

    def tracer_profil_manuel(self, x_upper, y_upper, x_lower, y_lower):
        """
       Fonction qui affiche graphiquement le profil NACA 2D généré manuellement.

       Args:
           x_upper, y_upper, x_lower, y_lower (array-like): Coordonnées des surfaces supérieure et inférieure.
       """
        plt.plot(x_upper, y_upper, marker='o', linewidth=1)
        plt.plot(x_lower, y_lower, marker='o', linewidth=1)
        plt.title(f"Profil aérodynamique {self.nom}")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.axis("equal")  # pour que l’échelle soit respectée
        plt.grid(True)
        plt.show()

    def enregistrer_profil_manuel_csv(self, x_up, y_up, x_low, y_low, nom_fichier= None):
        """
        Enregistre le profil manuel dans un fichier CSV.

        Args:
            x_up, y_up, x_low, y_low (array-like): Coordonnées.
            nom_fichier (str): Nom du fichier de sortie.
        """
        if nom_fichier is None:
            nom_fichier = f"{self.nom}_coord_profil.csv"

        chemin = os.path.join(profils_manuels, nom_fichier)
        os.makedirs(profils_manuels, exist_ok=True)

        with open(chemin, mode="w", newline="") as file:
            writer = csv.writer(file)

            # Écriture des propriétés du profil
            # writer.writerow(["Nom:", self.nom])
            # writer.writerow(["Cambrure (m):", m])
            # writer.writerow(["Position de cambrure (p):", p])
            # writer.writerow(["Epaisseur (t):", t])
            # writer.writerow(["Longueur de corde (c):", c])
            # writer.writerow([])  # ligne vide
            writer.writerow(["x", "y_haut", "y_bas"])

            for i in range(len(x_up)):
                writer.writerow([x_up[i], y_up[i], x_low[i], y_low[i]])  # supposant que x_up = x_low

        print(f"Les coordonnées du profil on été enregistré dans le fichier: {chemin}")
        return chemin

    def enregistrer_profil_format_dat(self, x_up, y_up, x_low, y_low, c, nom_fichier= None):

        """
        Enregistre le profil au format .dat compatible XFOIL/AirfoilTools.

        Args:
            x_up, y_up, x_low, y_low (array-like): Coordonnées.
            c (float): Longueur de la corde.
            nom_fichier (str): Nom du fichier de sortie.
        """
        if nom_fichier is None:
            nom_fichier = f"{self.nom}_coord_profil.dat"

        chemin = os.path.join(profils_manuels, nom_fichier)
        os.makedirs(profils_manuels, exist_ok=True)

        with open(chemin, mode='w') as file:
            file.write(f"{self.nom}\n")

            # Extrados : de 1 vers 0
            for i in reversed(range(len(x_up))):
                x = x_up[i] / c
                y = y_up[i] / c
                file.write(f"{x:.6f} {y:.6f}\n")

            # Intrados : de 0 vers 1
            for i in range(1, len(x_low)):
                x = x_low[i] / c
                y = y_low[i] / c
                file.write(f"{x:.6f} {y:.6f}\n")

        return chemin

    def tracer_comparaison(self, profil_2):
        """
        Trace le contour du profil courant et d’un autre profil sur un même graphe.

        Args:
            profil_2: Autre profil à comparer avec le profil courant.
            afficher_legend (bool): Si True, affiche la légende avec les noms des profils.
        """
        x1, y1 = zip(*self.coordonnees)
        x2, y2 = zip(*profil_2.coordonnees)

        nom_1 = self.nom
        nom_2 = profil_2.nom

        plt.figure(figsize=(8, 4))
        plt.plot(x1, y1, label=self.nom, linewidth=2)
        plt.plot(x2, y2, label=profil_2.nom, linewidth=2)

        plt.title(f"Comparaison : {nom_1} vs {nom_2}")
        plt.xlabel("Corde")
        plt.ylabel("épaisseur")
        plt.axis("equal")
        plt.grid(True)
        plt.show()

    def tracer_avec_bruit(self, amplitude=0.01, mode="gaussien", zone=(0.0, 0.3)):
        """
        Applique et affiche un bruit localisé sur l’extrados du profil.

        Args:
            amplitude (float): Amplitude maximale du bruit.
            mode (str): Type de bruit ('gaussien' ou 'uniforme').
            zone (tuple): Intervalle x où le bruit est appliqué.
        """
        from math import isfinite
        bruit = BruitProfil(amplitude=amplitude, mode=mode, zone=zone)
        coord_bruitees = bruit.appliquer(self.coordonnees)

        x0, y0 = zip(*self.coordonnees)
        x1, y1 = zip(*coord_bruitees)

        plt.figure(figsize=(8, 4))
        plt.plot(x0, y0, label="Original", linewidth=2)
        plt.plot(x1, y1, '--', label=f"Givré ({amplitude * 100:.1f} % corde)", alpha=0.8)
        plt.axis('equal')
        plt.grid(True)
        plt.legend()
        plt.xlabel("x")
        plt.ylabel("y")
        plt.title(f"{self.nom} — givrage zone {zone}")
        plt.show()

    def tracer_avec_rotation(self, angle_deg=5, centre=(0, 0)):
        from Airfoil import RotationProfil  # à enlever si déjà dans le fichier
        rotation = RotationProfil(angle_deg=angle_deg, centre=centre)
        coord_rot = rotation.appliquer(self.coordonnees)

        x1, y1 = zip(*self.coordonnees)
        x2, y2 = zip(*coord_rot)

        plt.figure(figsize=(8, 4))
        plt.plot(x1, y1, label="Profil original", linewidth=2)
        plt.plot(x2, y2, label=f"Rotation {angle_deg}°", linestyle="--")
        plt.title(f"Profil {self.nom} : original vs tourné")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.axis("equal")
        plt.grid(True)
        plt.legend()
        plt.show()

    def tracer_vrillage(self, angle_max_deg=20):
        from Airfoil import RotationVrillee
        vrilleur = RotationVrillee(angle_max_deg=angle_max_deg)
        coord_vrillees = vrilleur.appliquer(self.coordonnees)

        x1, y1 = zip(*self.coordonnees)
        x2, y2 = zip(*coord_vrillees)

        plt.figure(figsize=(8, 4))
        plt.plot(x1, y1, label="Profil original", linewidth=2)
        plt.plot(x2, y2, label=f"Vrillage {angle_max_deg}°", linestyle="--")
        plt.title(f"Vrillage progressif du profil {self.nom}")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.axis("equal")
        plt.grid(True)
        plt.legend()
        plt.show()

    def tracer_givrage(self, epaisseur=0.02, zone=(0.3, 0.45)):
        """
        Trace le profil original et une couche de givrage ajoutée sur l'extrados,
        enregistre les coordonnées givrées en CSV et en DAT (XFoil).

        epaisseur : épaisseur uniforme du givrage (en fraction de corde)
        zone      : intervalle x_min, x_max où le givrage est appliqué
        """
        import os, csv

        # ─── dossiers et chemins ───────────────────────────────────────────────────────
        dossier = os.path.join("data", "profils_givre")
        os.makedirs(dossier, exist_ok=True)
        fichier_csv = os.path.join(dossier, f"{self.nom}_coord_givre.csv")
        fichier_dat = os.path.join(dossier, f"{self.nom}_coord_givre.dat")

        # ───  extraction coords ──────────────────────────────────────────────────────
        coords = np.array(self.coordonnees)  # shape (N,2)
        x_vals, y_vals = coords[:, 0], coords[:, 1]

        # ───  normales ────────────────────────────────────────────────────────────────
        dx_ds, dy_ds = np.gradient(x_vals), np.gradient(y_vals)
        tangentes = np.vstack((dx_ds, dy_ds)).T
        longueurs = np.linalg.norm(tangentes, axis=1)
        normals = np.column_stack((-dy_ds / longueurs, dx_ds / longueurs))

        # ───  masque extrados + zone ─────────────────────────────────────────────────
        masque = (
                (x_vals >= zone[0]) &
                (x_vals <= zone[1]) &
                (y_vals >= 0)
        )

        # ───  calcul des points givrés ───────────────────────────────────────────────
        coords_givre = coords.copy()
        coords_givre[masque] -= normals[masque] * epaisseur

        # ───  écriture du CSV ─────────────────────────────────────────────────────────
        with open(fichier_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["x", "y"])
            for x, y in coords_givre:
                writer.writerow([f"{x:.6f}", f"{y:.6f}"])
        print(f" CSV givré : {fichier_csv}")

        # ───  écriture du DAT pour XFoil ──────────────────────────────────────────────
        with open(fichier_dat, "w", encoding="utf-8") as f:
            # entête XFoil
            f.write(f"{self.nom}-givre\n")
            for x, y in coords_givre:
                f.write(f"{x:.6f} {y:.6f}\n")
        print(f" DAT givré  : {fichier_dat}")

        # ───  tracé ───────────────────────────────────────────────────────────────────
        plt.figure(figsize=(8, 4))
        plt.plot(x_vals, y_vals, label="Original", linewidth=2)
        plt.plot(coords_givre[:, 0],
                 coords_givre[:, 1],
                 color="crimson",
                 linewidth=2,
                 label=f"Givré {epaisseur:.3f} zone {zone}")
        plt.title(f"Profil givré {self.nom}")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.axis("equal")
        plt.grid(True)
        plt.legend()
        plt.show()


class GivreProfil:
    """
    Applique une couche de givrage uniformément sur l'extrados,
    de x0 à x1, avec une épaisseur max ep_max.
    """
    def __init__(self, ep_max=0.02, zone=(0.2, 0.6), forme="gaussienne"):
        self.ep_max = ep_max
        self.x0, self.x1 = zone
        self.forme = forme

    def _epaisseur(self, x):
        """Retourne l'épaisseur de givrage en x."""
        # normalise x dans [0,1] sur la zone
        xi = (x - self.x0) / (self.x1 - self.x0)
        xi = np.clip(xi, 0, 1)
        if self.forme == "gaussienne":
            # pic en milieu de zone
            return self.ep_max * np.exp(-((xi - 0.5)**2)/(2*0.15**2))
        elif self.forme == "triangle":
            return self.ep_max * np.minimum(xi, 1 - xi) * 2
        else:  # uniforme
            return self.ep_max * np.ones_like(xi)

    def appliquer(self, coordonnees):
        coords = np.array(coordonnees)    # shape (N,2)
        x, y = coords[:,0], coords[:,1]

        # calcul des normales du profil
        dx_ds, dy_ds = np.gradient(x), np.gradient(y)
        tang = np.vstack((dx_ds, dy_ds)).T
        norms = np.linalg.norm(tang, axis=1, keepdims=True)
        normals = np.hstack((-dy_ds.reshape(-1,1), dx_ds.reshape(-1,1))) / norms

        # on ne givre que l'extrados (y>=0)
        masque = y >= 0

        # calcul de l'épaisseur en chaque point
        eps = self._epaisseur(x)

        # on applique uniquement sur la zone d'extrados
        decal = normals * (eps * masque)[:,None]

        # retourne les nouvelles coordonnées
        coords_givre = coords + decal
        return [tuple(pt) for pt in coords_givre]



class RotationProfil:
    def __init__(self, angle_deg=0, centre=(0, 0)):
        self.angle_rad = np.radians(angle_deg)      #  conversion degrés = radians
        self.centre = np.array(centre)              #  point autour duquel on tourne

    def appliquer(self, coordonnees):
        coords = np.array(coordonnees)              #  convertit liste de tuples = array Nx2
        coords -= self.centre                        #  déplacement du centre vers l’origine (x - x0, y - y0)

        M = np.array([                               #  Matrice de rotation
            [np.cos(self.angle_rad), -np.sin(self.angle_rad)],
            [np.sin(self.angle_rad),  np.cos(self.angle_rad)]
        ])

        rot = coords @ M.T                           #  produit matriciel : rotation
        return (rot + self.centre).tolist()          #  on revient au repère initial (x + x0, y + y0)


# Classe pour appliquer du bruit (rugosité, givrage, etc.) sur une région du profil


class BruitProfil:
    def __init__(self, amplitude=0.01, mode="gaussien", zone=(0.0, 0.3)):
        """
        amplitude : déplacement max (en corde unité)
        mode      : "gaussien" ou "uniforme"
        zone      : (x_min, x_max) sur lequel on applique le bruit
        """
        self.amplitude = amplitude
        self.mode = mode
        self.zone = zone

    def appliquer(self, coordonnees):
        # conversion et extraction
        coords = np.array(coordonnees)       # shape (N,2)
        x_vals, y_vals = coords[:,0], coords[:,1]

        # calcul des tangentes et normales
        dx_ds, dy_ds = np.gradient(x_vals), np.gradient(y_vals)
        tangentes = np.vstack((dx_ds, dy_ds)).T
        norms = np.linalg.norm(tangentes, axis=1)
        normals = np.column_stack((-dy_ds/norms, dx_ds/norms))

        # on ne bruit que là où x dans la zone ET y >= 0 (extrados)
        masque = (
            (x_vals >= self.zone[0])
            & (x_vals <= self.zone[1])
            & (y_vals >= 0)
        )

        # génération du bruit scalaire
        if self.mode == "gaussien":
            eta = np.random.normal(0, self.amplitude, size=len(x_vals))
        else:
            eta = np.random.uniform(-self.amplitude, self.amplitude, size=len(x_vals))

        # on garde uniquement les eta pour lesquels masque=True
        eta *= masque

        # décalage suivant la normale
        coords_bruitees = coords + normals * eta[:, None]

        return [tuple(pt) for pt in coords_bruitees]


           #  ajout du bruit point par point


class RotationVrillee:
    def __init__(self, angle_max_deg=20, axe="x", centre_y=0.0):
        self.angle_max = np.radians(angle_max_deg)
        self.axe = axe
        self.centre_y = centre_y  # centre de rotation en y

    def appliquer(self, coordonnees):
        coords = np.array(coordonnees)
        nouvelles_coords = []

        for x, y in coords:
            # Angle de rotation en fonction de x (linéaire)
            alpha = self.angle_max * x

            # Rotation autour de (x, centre_y)
            dy = y - self.centre_y
            y_rot = self.centre_y + dy * np.cos(alpha)

            nouvelles_coords.append((x, y_rot))

        return nouvelles_coords

def generer_pale_vrillee(profil_2d, angle_max_deg=30, z_max=1.0, sections=50):
    pale = []
    for i in range(sections):
        z = z_max * i / (sections - 1)
        angle_local = angle_max_deg * z / z_max  # rotation linéaire selon Z
        rotation = RotationProfil(angle_deg=angle_local, centre=(0.25, 0))  # tu peux changer le centre
        section = rotation.appliquer(profil_2d)
        for x, y in section:
            pale.append((x, y, z))
    return np.array(pale)

if __name__ == "__main__":
    from main import demande_profil, comparer_polaires
    from aerodynamique import Aerodynamique
    import os

    from interaction_graphique import *

    # 1) importer et afficher le profil brut
    interface = FenetreInteraction()
    profil_obj, nom = demande_profil(interface)  # correction ici
    profil_obj.tracer_contour(nom)

    # 2) paramètres de givrage
    ep = float(input("Épaisseur du givrage [0.02] : ") or 0.02)
    z0, z1 = map(
        float,
        (input("Zone givrage x0,x1 [0.3,0.45] : ") or "0.3,0.45").split(",")
    )

    # 3) tracer + sauvegarder le profil givré (CSV + DAT)
    profil_obj.tracer_givrage(epaisseur=ep, zone=(z0, z1))

    # 4) préparer Mach/Reynolds
    reynolds = float(input("Reynolds (ex: 50000) : ") or 50000)
    mach = float(input("Mach     (ex: 0.1)    : ") or 0.1)

    # 5) créer les dossiers
    dir_import = os.path.join("data", "profils_importes")
    dir_givre = os.path.join("data", "profils_givre")
    os.makedirs(dir_import, exist_ok=True)
    os.makedirs(dir_givre, exist_ok=True)

    # 6) lancer XFoil sur le profil normal
    aero_norm = Aerodynamique(nom)
    dat_norm = os.path.join(dir_import, f"{nom}_coord_profil.dat")

    txt_norm = os.path.join(dir_import, f"{nom}_normale.txt")
    txt_norm = aero_norm.run_xfoil(
        dat_file=dat_norm, reynolds=reynolds, mach=mach,
        alpha_start=-5, alpha_end=12, alpha_step=1,
        output_file=txt_norm
    )
    if txt_norm and os.path.exists(txt_norm):
        aero_norm.donnees = aero_norm.lire_txt_et_convertir_dataframe(txt_norm)
    else:
        aero_norm.donnees = None

    # 7) lancer XFoil sur le profil givré
    aero_givre = Aerodynamique(nom + "-givre")
    dat_givre = os.path.join(dir_givre, f"{nom}_coord_givre.dat")
    txt_givre = os.path.join(dir_givre, f"{nom}_givree.txt")
    txt_givre = aero_givre.run_xfoil(
        dat_file=dat_givre, reynolds=reynolds, mach=mach,
        alpha_start=-5, alpha_end=12, alpha_step=1,
        output_file=txt_givre
    )
    if txt_givre and os.path.exists(txt_givre):
        aero_givre.donnees = aero_givre.lire_txt_et_convertir_dataframe(txt_givre)
    else:
        aero_givre.donnees = None

    # 8) tracer chaque polaire séparément
    if aero_norm.donnees is not None:
        aero_norm.tracer_polaires_depuis_txt()
    if aero_givre.donnees is not None:
        aero_givre.tracer_polaires_depuis_txt()

    # 9) superposer les deux dans la même figure
    polaires = {}
    if aero_norm.donnees is not None:
        polaires["Normal"] = aero_norm.donnees
    if aero_givre.donnees is not None:
        polaires["Givré"] = aero_givre.donnees

    if len(polaires) >= 2:
        comparer_polaires(polaires)
    else:
        print("Pas assez de données pour superposer les polaires.")
