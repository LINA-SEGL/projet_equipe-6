#import sys
#print("Python exécuté :", sys.executable)
import asyncio
import requests
from python_opensky import OpenSky, StatesResponse
import os
"""
Script pour récupérer les données de vols en temps réel via l’API OpenSky 
et afficher les détails aérodynamiques, incluant le calcul du delta ISA 
via l’API OpenWeather.

Fonctionnalités :
- Connexion asynchrone à OpenSky pour récupérer les vols en temps réel.
- Affichage d'une liste de vols avec altitude et vitesse.
- Calcul du Mach et du delta ISA basé sur la température atmosphérique réelle.
- Utilisation de l’API OpenWeather pour estimer la température observée.

Constantes :
    API_KEY_OPENWEATHER (str): Clé d’authentification pour accéder à OpenWeather.
"""
#  Définissez votre clé ici :
API_KEY_OPENWEATHER =""

def calcul_delta_isa(lat: float, lon: float, alt_m: float, api_key: str) -> float | None:
    """
       Calcule l'écart de température entre l’atmosphère réelle et l’atmosphère standard (ΔISA).

       Cette fonction interroge OpenWeather pour obtenir la température au sol, puis extrapole
       la température à l’altitude donnée selon un gradient thermique standard (0.0065 K/m).

       Args:
           lat (float): Latitude du vol.
           lon (float): Longitude du vol.
           alt_m (float): Altitude en mètres.
           api_key (str): Clé API OpenWeather.

       Returns:
           float | None: Écart ΔISA en Kelvin si calcul réussi, sinon None.
       """
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key}
    resp = requests.get(url, params=params)

    # Vérifier le statut HTTP
    if resp.status_code != 200:
        print(f"[OPENWEATHER ERROR] HTTP {resp.status_code} — {resp.text}")
        return None

    data = resp.json()
    #  Vérifier que main.temp existe
    if "main" not in data or "temp" not in data["main"]:
        print(f"[OPENWEATHER ERROR] réponse inattendue : {data}")
        return None

    T_sol_K = data["main"]["temp"]
    lapse = 0.0065  # K/m
    T_obs = T_sol_K - lapse * alt_m
    T_isa = 288.15 - lapse * alt_m
    return T_obs - T_isa

async def fetch_vols(limit: int = 20):
    """
       Récupère une liste de vols en temps réel depuis l’API OpenSky.

       Args:
           limit (int): Nombre maximum de vols à récupérer.

       Returns:
           list[State]: Liste d'objets représentant les vols (appareils en vol).
       """
    async with OpenSky() as api:
        states: StatesResponse = await api.get_states()
        return states.states[:limit]  # liste d'objets State

def afficher_liste(vols):
    """
       Affiche une liste formatée des vols récupérés : callsign, pays d’origine,
       altitude géométrique et vitesse.

       Args:
           vols (list[State]): Liste des objets vols issus d’OpenSky.
       """
    for i, s in enumerate(vols, 1):
        cs = (s.callsign or "N/A").strip()
        pays = s.origin_country or "Inconnu"
        print(f"{i:2d}. {cs:8s} | {pays:12s} | Alt : {s.geo_altitude or 0:7.0f} m | Vit : {s.velocity or 0:6.1f} m/s")

def afficher_details(s):
    lat, lon = s.latitude, s.longitude
    alt = s.geo_altitude or 0
    # Mach
    gamma, R = 1.4, 287.05
    T_std = 288.15 - 0.0065 * alt
    vitesse_son = (gamma * R * T_std) ** 0.5
    mach = (s.velocity or 0) / vitesse_son
    # ΔISA (optionnel)
    delta = calcul_delta_isa(lat, lon, alt, API_KEY_OPENWEATHER)

    print("\n--- Détails du vol sélectionné ---")
    print(f"Callsign       : {(s.callsign or 'N/A').strip()}")
    print(f"ICAO24          : {s.icao24}")
    print(f"Pays d’origine : {s.origin_country}")
    print(f"Position        : lat {lat:.4f}, lon {lon:.4f}")
    print(f"Temps position  : {s.time_position}")
    print(f"Altitude (GPS)  : {alt:.1f} m")
    print(f"Vitesse         : {(s.velocity or 0):.1f} m/s")
    print(f"Mach            : {mach:.2f}")
    if delta is not None:
        print(f"ΔISA ≈ {delta:.1f} K (approx.)")
    else:
        print("ΔISA          : non calculé")

def main():
    vols = asyncio.run(fetch_vols(limit=2000))
    afficher_liste(vols)
    choix = int(input("\nSélectionnez un vol (numéro) : ")) - 1
    if 0 <= choix < len(vols):
        afficher_details(vols[choix])
    else:
        print("Sélection invalide.")

if __name__ == "__main__":
    main()

