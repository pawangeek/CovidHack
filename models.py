import requests

def get_coords(ip_address):
    try:
        response = requests.get("http://ip-api.com/json/{}".format(ip_address))
        js = response.json()
        latitude = js['lat']
        longitude = js['lon']
        place = [latitude, longitude]

        return place

    except Exception as e:
        return "Unknown"