import asyncio
import requests
from python_opensky import OpenSky, StatesResponse

API_KEY_OPENWEATHER = "VOTRE_API_KEY"  # pour ΔISA (optionnel)

def calcul_delta_isa(lat: float, lon: float, alt_m: float, api_key: str) -> float:
    """
    Calcule ΔISA ≈ T_obs(alt) – T_ISA(alt),
    en approximant T_obs(alt) à partir de T_surface – gradient × alt.
    """
    # 1. Récupère la température au sol via OpenWeatherMap
    resp = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params={"lat": lat, "lon": lon, "appid": api_key}
    )
    T_sol_K = resp.json()["main"]["temp"]  # en kelvin
    # 2. Gradient standard (6,5 K / km)
    lapse = 0.0065  # K/m
    # 3. Température observée approximée à l'altitude
    T_obs = T_sol_K - lapse * alt_m
    # 4. Température ISA à l'altitude : 288,15 K – lapse × alt
    T_isa = 288.15 - lapse * alt_m
    return T_obs - T_isa

async def fetch_vols(limit: int = 20):
    async with OpenSky() as api:
        states: StatesResponse = await api.get_states()
        return states.states[:limit]  # liste d'objets State

def afficher_liste(vols):
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
    try:
        delta = calcul_delta_isa(lat, lon, alt, API_KEY_OPENWEATHER)
    except Exception:
        delta = None

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
        print("ΔISA           : non calculé")

def main():
    vols = asyncio.run(fetch_vols(limit=100))
    afficher_liste(vols)
    choix = int(input("\nSélectionnez un vol (numéro) : ")) - 1
    if 0 <= choix < len(vols):
        afficher_details(vols[choix])
    else:
        print("Sélection invalide.")

if __name__ == "__main__":
    main()

