import asyncio
from python_opensky import OpenSky, StatesResponse
from ConditionVol import ConditionVol
import pandas as pd

class VolOpenSkyAsync:
    def __init__(self):
        self.api = OpenSky()

    async def get_vols(self, limit=5):
        async with self.api as opensky:
            response: StatesResponse = await opensky.get_states()

            vols_info = []
            for s in response.states[:limit]:
                condition_temp = ConditionVol(s.geo_altitude or 0, mach=0, angle_deg=0)

                gamma = 1.4
                R = 287.05
                vitesse_son = (gamma * R * condition_temp.temperature_K) ** 0.5

                # Étape 2 : calcul du vrai Mach
                mach = (s.velocity or 0) / vitesse_son

                # Étape 3 : créer l’objet final avec le Mach calculé
                condition = ConditionVol(
                    altitude_m=s.geo_altitude or 0,
                    mach=mach,
                    angle_deg=5,  # tu peux le rendre variable
                    delta_isa=0  # ou tu peux estimer à partir de OpenWeather
                )

                vols_info.append({
                    "callsign": s.callsign.strip() if s.callsign else "N/A",
                    "altitude_m": s.geo_altitude or 0,
                    "vitesse_mps": s.velocity or 0,
                    "position": (s.latitude, s.longitude),
                    "heure": s.time_position,
                    "condition_vol": condition
                })

            return vols_info

def charger_compagnies_depuis_csv(fichier):
    df = pd.read_csv(fichier, sep="^")
    compagnies = {}

    for _, row in df.iterrows():
        icao = str(row.get("icao_code", "")).strip().upper()
        nom = str(row.get("name", "")).strip()

        if icao and icao != "nan":
            compagnies[icao] = (nom, "Pays inconnu")  # Le pays n'est pas dispo ici

    return compagnies