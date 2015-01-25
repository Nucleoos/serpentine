#coding: utf-8
""" Set de fonctions utilisant les services geonames
"""
import urllib
import json  #simplejson as json


def getClosestTown(lat, lon):
    """ retourne la ville la plus proche du point lat,lon
    Essaye d'abord NearByPostalCodes puis Nearby (notamment pour le Chili)
    """
    #api nearbyPostalCode fonctionne bien en europe 
    url = 'http://api.geonames.org/findNearbyPostalCodesJSON?lat=' + str(lat) + '&lng=' + str(lon) + '&username=bdamay'
    places = json.loads(urllib.urlopen(url).readlines()[0])['postalCodes']
    if len(places) > 0:
        return places[0]['placeName']
    #si rien de trouvé nearby tout court (tout lieu)
    url = 'http://api.geonames.org/findNearbyJSON?lat=' + str(lat) + '&lng=' + str(lon) + '&username=bdamay'
    places = json.loads(urllib.urlopen(url).readlines()[0])['geonames']
    if len(places) > 0:
        return places[0]['name']
    return 'Inconnu'
