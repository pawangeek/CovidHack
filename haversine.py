import numpy as np

R = 6378137.0
R_km = R/1000

def haversine(points_a, points_b):

    lat1, lon1 = np.radians(points_a[0]), np.radians(points_a[1])
    lat2, lon2 = np.radians(points_b[0]), np.radians(points_b[1])

    lat = lat2 - lat1
    lon = lon2 - lon1

    d = np.sin(lat * 0.5) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(lon * 0.5) ** 2
    h = 2 * R_km * np.arcsin(np.sqrt(d))

    return h
