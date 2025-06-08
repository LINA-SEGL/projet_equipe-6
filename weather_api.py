import requests

def get_delta_isa(lat, lon, altitude_m, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code != 200:
        print("Erreur API OpenWeather")
        return 0

    data = response.json()
    temp_sol_C = data["main"]["temp"]
    altitude_sol_m = data["main"].get("sea_level", 0)

    temp_alt_C = temp_sol_C - 0.0065 * (altitude_m - altitude_sol_m)
    temp_alt_K = temp_alt_C + 273.15

    T_ISA = 288.15 - 0.0065 * altitude_m if altitude_m <= 11000 else 216.65
    delta_isa = temp_alt_K - T_ISA

    return delta_isa
