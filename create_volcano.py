#!/usr/bin/env python

'''
Queries the Smithsonian Archive for volcanos, parses the return xml,
and generates volcano products
'''

from __future__ import print_function
import os
import re
import json
import math
import urllib3
import requests

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VOLC_PROD = "VOLC-GVN_{}-{}-{}"
SMITHSONIAN_URL = "https://webservices.volcano.si.edu/geoserver/GVP-VOTW/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=GVP-VOTW:Smithsonian_VOTW_Holocene_Volcanoes&outputFormat=application/json"
VERSION = "v1.0"

def main():
    '''queries the smithsonian and generates holocene volcano products'''
    response = requests.get(SMITHSONIAN_URL, verify=False, timeout=45)
    response.raise_for_status()
    results = json.loads(response.text.encode('ascii', 'ignore').decode('utf-8')).get('features')
    for result in results:
        #convert to lower & print
        for key in result.keys():
            if isinstance(result.get(key), dict):
                result[key] = {k.lower(): v for k, v in result[key].items()}
        #save to object
        gen_product(result)

def gen_product(volc_obj):
    '''generates the appropriate metadata for the volcano'''
    prop = volc_obj.get("properties", {})
    vname = prop.get("volcano_name")
    vnumber = prop.get("volcano_number")
    clean_name = re.sub('[^a-z^A-Z^0-9\^_]+', '', vname.replace(' ', '_').replace('-','_')).strip('_')
    prod_id = VOLC_PROD.format(vnumber, clean_name, VERSION)
    location = build_polygon_geojson(volc_obj.get('geometry')) #volc_obj["geometry"] # cannot use POint obj in grq
    volc_obj['clean_name'] = clean_name
    ds_obj = {'label': prod_id, 'version': VERSION, "location": location}
    met_obj = volc_obj
    print("generating: {}".format(prod_id))
    save_product_met(prod_id, ds_obj, met_obj)
    if not prop.get('primary_photo_link', False) == None:
        attempt_browse(prod_id, met_obj)
    else:
        print("link not found.")

def attempt_browse(prod_id, met_obj):
    '''attempts to download the browse product'''
    url = met_obj.get("properties", {}).get("primary_photo_link", False)
    browse_path = os.path.join(prod_id, "{}.browse.png".format(prod_id))
    jpg_path = os.path.join(prod_id, "{}.browse.jpeg".format(prod_id))
    print('localizing url {} to {}'.format(url, browse_path))
    try:
        if url.endswith('jpg') or url.endswith('jpeg'):
            os.system("wget -O {} {}".format(jpg_path, url))
            os.system("convert {} {}".format(jpg_path, browse_path))
            os.remove(jpg_path)
        else:
            os.system("wget -O {} {}".format(browse_path, url))
    except:
        pass

def save_product_met(prod_id, ds_obj, met_obj):
    '''generates the appropriate product json files in the product directory'''
    if not os.path.exists(prod_id):
        os.mkdir(prod_id)
    outpath = os.path.join(prod_id, '{}.dataset.json'.format(prod_id))
    with open(outpath, 'w') as outf:
        json.dump(ds_obj, outf)
    outpath = os.path.join(prod_id, '{}.met.json'.format(prod_id))
    with open(outpath, 'w') as outf:
        json.dump(met_obj, outf)

def shift(lat, lon, bearing, distance):
    R = 6378.1  # Radius of the Earth
    bearing = math.pi * bearing / 180  # convert degrees to radians
    lat1 = math.radians(lat)  # Current lat point converted to radians
    lon1 = math.radians(lon)  # Current long point converted to radians
    lat2 = math.asin(math.sin(lat1) * math.cos(distance / R) +
                     math.cos(lat1) * math.sin(distance / R) * math.cos(bearing))
    lon2 = lon1 + math.atan2(math.sin(bearing) * math.sin(distance / R) * math.cos(lat1),
                             math.cos(distance / R) - math.sin(lat1) * math.sin(lat2))
    lat2 = math.degrees(lat2)
    lon2 = math.degrees(lon2)
    return [lon2, lat2]

def build_polygon_geojson(geometry):
    lat = float(geometry.get('coordinates')[1])
    lon = float(geometry.get('coordinates')[0])
    radius = 1.0
    l = range(0, 361, 20)
    coordinates = []
    for b in l:
        coords = shift(lat, lon, b, radius)
        coordinates.append(coords)
    return {"coordinates": [coordinates], "type": "Polygon"}

if __name__ == '__main__':
    main()
