import requests

def distance_coord_to_string(lat1, lon1, location):
    headers = {"User-Agent": "test-app"}

    #lat1, lon1 = 57.4481, 9.9650

    # Geocode
    geo = requests.get(
        "https://nominatim.openstreetmap.org/search",
        params={"q": location, "format": "json"},
        headers=headers
    ).json()

    lat2 = float(geo[0]["lat"])
    lon2 = float(geo[0]["lon"])

    # Route
    route_res = requests.get(
        f"https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}",
        params={"overview": "false"}
    )

    route = route_res.json()

    distance_km = route["routes"][0]["distance"] / 1000
    return distance_km

