#!/usr/bin/env python

'''
Queries the Smithsonian Archive for volcanos, parses the return xml,
and generates volcano products
'''

from __future__ import print_function
import os
import re
import json
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
    location = volc_obj["geometry"]
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

if __name__ == '__main__':
    main()
