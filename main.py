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


import asyncio
from VolOpenSkyAsync import VolOpenSkyAsync
from VolOpenSkyAsync import charger_compagnies_depuis_csv

# Charger les compagnies
compagnies = charger_compagnies_depuis_csv("data/iata_airlines.csv")

async def main():
    api = VolOpenSkyAsync()
    vols = await api.get_vols(limit=3)

    for i, v in enumerate(vols):
        code = v['callsign'][:3].upper().strip()
        print(f" Recherche du code : {code}")

        nom, pays = compagnies.get(code, ("Compagnie inconnue", "Pays inconnu"))

        if (nom, pays) == ("Compagnie inconnue", "Pays inconnu"):
            print(f" Code {code} non trouvé dans le fichier.")

        print(f"{i+1}.  {v['callsign']} - {nom} ({pays})")
        print(f"   Altitude: {v['altitude_m']:.1f} m - Vitesse: {v['vitesse_mps']:.1f} m/s")
        v["condition_vol"].afficher()
        print()

if __name__ == "__main__":
    asyncio.run(main())