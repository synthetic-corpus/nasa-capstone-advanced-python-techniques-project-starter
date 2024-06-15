"""Extract data on near-Earth objects and close approaches from CSV and JSON files.

The `load_neos` function extracts NEO data from a CSV file, formatted as
described in the project instructions, into a collection of `NearEarthObject`s.

The `load_approaches` function extracts close approach data from a JSON file,
formatted as described in the project instructions, into a collection of
`CloseApproach` objects.

The main module calls these functions with the arguments provided at the command
line, and uses the resulting collections to build an `NEODatabase`.

You'll edit this file in Task 2.
"""
import csv
import json
from collections import deque
from helpers import cd_to_datetime

from models import NearEarthObject, CloseApproach


def load_neos(neo_csv_path):
    """Read near-Earth object information from a CSV file.

    :param neo_csv_path: A path to a CSV file containing data about near-Earth objects.
    :return: A collection (deque) of `NearEarthObject`s.

    Loading_neo sanitizes/transform several csv values so that 
    they are the right type for Class objects.
    """
    with open(neo_csv_path,'r') as neoCSV:
        reader = csv.DictReader(neoCSV)
        neo_deque = deque()
        for line in reader:
            # get only the columns needed. Discard the rest
            necessary_keys = {'pdes','name','pha','diameter'}
            new_line = {key: line[key] for key in necessary_keys if key in line.keys()}

            # sanitization for the keys:
            if new_line['name'] == '':
                new_line['name'] = None
            if new_line['pha'] == 'Y':
                new_line['pha'] = True
            else:
                new_line['pha'] = False
            if new_line['diameter'] == '':
                new_line['diameter'] = float('nan')
            else:
                new_line['diameter'] = float(new_line['diameter'])


            neo_deque.append(NearEarthObject(
                pdes = new_line['pdes'],
                name = new_line['name'],
                diameter = new_line['diameter'],
                pha = new_line['pha']
            ))


    return neo_deque


def load_approaches(cad_json_path):
    """Read close approach data from a JSON file.

    :param cad_json_path: A path to a JSON file containing data about close approaches.
    :return: A collection (deque) of `CloseApproach`es.

    The loading sanitizes and transforms several json values to ensure that 
    they are the right data type for the corresponding class.
    """
    approach_deque = deque()

    with open(cad_json_path,'r') as bigJson:
        data = json.load(bigJson)
        approaches = data['data']

        for approach in approaches:
            # Perform input conversions
            pdes = approach[0]
            time = cd_to_datetime(approach[3])
            distance = float(approach[4])
            velocity = float(approach[7])

            approach_deque.append(CloseApproach(
                designation = pdes,
                time = time,
                distance = distance,
                velocity = velocity
            ))
    return approach_deque
