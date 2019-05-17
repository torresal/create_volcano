#!/usr/bin/env python

'''generates a volcano product from an input GVP id, lat/lon, & volcano name'''

from __future__ import print_function
import os
import re
import math
import json

VERSION = "v1.0"
PROD_ID = "VOLC-GVN_{}-{}-{}"

def main():
    '''generates holocene volcano products'''
    #load from context
    ctx = load_context()
    vname = ctx.get('volcano_name', False)
    if not vname:
        raise Exception('Volcano Name not provided')
    lat = ctx.get('latitude', False)
    lon = ctx.get('longitude', False)
    gvp_id = ctx.get('GVP_number', False)
    #save to object
    gen_product(vname, lat, lon, gvp_id)

def gen_product(vname, lat, lon, gvp_id):
    '''generates the appropriate metadata for the volcano'''
    clean_name = re.sub('[^a-z^A-Z^0-9\^_]+', '', vname.replace(' ', '_')).strip('_')
    if len(clean_name) < 2:
        raise Exception('please use a longer volcano_name: {} is too short'.format(clean_name))
    vname = clean_name.replace('_', ' ')
    lat = float(lat)
    if lat < -90 or lat > 90:
        raise Exception('Input latitude: {} is out of bounds'.format(lat))
    if lon < -180 or lon > 180:
        raise Exception('Input longitude: {} is out of bounds'.format(lon))
    clean_gvp = re.sub('[^0-9\^]+', '', gvp_id)
    if len(clean_gvp) > 50 or len(clean_gvp) < 1:
        raise Exception('Provided GVP number is invalid: {}'.format(clean_gvp))
    prod_id = PROD_ID.format(clean_gvp, clean_name, VERSION)
    location = build_polygon_geometry(lat, lon)
    ds_obj = {'label': prod_id, 'version': VERSION, "location": location}
    met_obj = {"geometry": location, "volcano_number": clean_gvp, "longitude": lon, "latitude": lat,
               "clean_name": clean_name, "volcano_name": vname}
    save_product_met(prod_id, ds_obj, met_obj)

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

def build_polygon_geojson(lat, lon):
    radius = 1.0
    l = range(0, 361, 20)
    coordinates = []
    for b in l:
        coords = shift(lat, lon, b, radius)
        coordinates.append(coords)
    return {"coordinates": [coordinates], "type": "Polygon"}

def load_context():
    '''loads the context file into a dict'''
    try:
        context_file = '_context.json'
        with open(context_file, 'r') as fin:
            context = json.load(fin)
        return context
    except:
        raise Exception('unable to parse _context.json from work directory')

if __name__ == '__main__':
    main()
