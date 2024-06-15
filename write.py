"""Write a stream of close approaches to CSV or to JSON.

This module exports two functions: `write_to_csv` and `write_to_json`, each of
which accept an `results` stream of close approaches and a path to which to
write the data.

These functions are invoked by the main module with the output of the `limit`
function and the filename supplied by the user at the command line. The file's
extension determines which of these functions is used.

You'll edit this file in Part 4.
"""
import csv
import json
import math

def prep_csv(close_approach):
    """ This is a Helper Function. 
    It takes in one close approach object and formats its for CSV dict injest"""
    return_this = {}
    tempt_dict = close_approach.serialize()
    tempt_dict.update(close_approach.neo.serialize())

    for key,value in tempt_dict.items():
        if value is None:
            value = '' # CSV files love emptry strings!
        if value is False:
            value = 'False'
        if value is True:
            value = 'True'
        if key == 'diameter_km' and math.isnan(value):
            value = 'nan'
        return_this[key] = value
    return return_this


def write_to_csv(results, filename):
    """Write an iterable of `close_approach` objects to a CSV file.

    The precise output specification is in `README.md`. Roughly, each output row
    corresponds to the information in a single close approach from the `results`
    stream and its associated near-Earth object.

    :param results: An iterable of `close_approach` objects.
    :param filename: A Path-like object pointing to where the data should be saved.
    """
    
    with open(filename,'w',newline = '') as out_csv:
        fieldnames = (
        'datetime_utc', 'distance_au', 'velocity_km_s',
        'designation', 'name', 'diameter_km', 'potentially_hazardous'
        )
        writer = csv.DictWriter(out_csv, fieldnames)
        writer.writeheader()
        for row in results:
            writer.writerow(prep_csv(row))


def write_to_json(results, filename):
    """Write an iterable of `close_approach` objects to a JSON file.

    The precise output specification is in `README.md`. Roughly, the output is a
    list containing dictionaries, each mapping `close_approach` attributes to
    their values and the 'neo' key mapping to a dictionary of the associated
    NEO's attributes.

    :param results: An iterable of `close_approach` objects.
    :param filename: A Path-like object pointing to where the data should be saved.
    """
    result_list = []
    for close_approach in results:
        # makes a nice Dictionary object from two Dictionaries.
        append_this = close_approach.serialize()
        append_this['neo'] = close_approach.neo.serialize()
        result_list.append(append_this)

    with open(filename,'w') as outfile:
        json.dump(result_list,outfile)
