"""Represent models for near-Earth objects and their close approaches.

The `NearEarthObject` class represents a near-Earth object. Each has a unique
primary designation, an optional unique name, an optional diameter, and a flag
for whether the object is potentially hazardous.

The `CloseApproach` class represents a close approach to Earth by an NEO. Each
has an approach datetime, a nominal approach distance, and a relative approach
velocity.

A `NearEarthObject` maintains a collection of its close approaches, and a
`CloseApproach` maintains a reference to its NEO.

The functions that construct these objects use information extracted from the
data files from NASA, so these objects should be able to handle all of the
quirks of the data set, such as missing names and unknown diameters.

You'll edit this file in Task 1.
"""
import hashlib
from helpers import datetime_to_str


class NearEarthObject:
    """A near-Earth object (NEO).

    An NEO encapsulates semantic and physical parameters about the object, such
    as its primary designation (required, unique), IAU name (optional), diameter
    in kilometers (optional - sometimes unknown), and whether it's marked as
    potentially hazardous to Earth.

    A `NearEarthObject` also maintains a collection of its close approaches -
    initialized to an empty collection, but eventually populated in the
    `NEODatabase` constructor.
    """


    def __init__(self, **info):
        """Create a new `NearEarthObject`.

        :param info: This variadic for future proofing. i.e. new iterations of this project may 
            take in additional keywords.
            However, the specif keys expected parameters are:
            
            pdes - NASA's designation as a string
            name - the name of the NEO, if it is named, as a string
            diameter - diameter of the NEO in km.
            pha - a boolean value if this is dangerous or not earth.

            The data is expected to be sanitzied and edge cases handled 
            prior to the invocation of the function.
            Specifically, data sanitation is done on extract.py

            Reason being, is I could concieve of getting this information via .csv, .json, 
            an async request, sql response object of some sort etc. 
            Each would require a custom helper function(s) to sanitize them anyway, 
            so it's better to lightly couple the sanitization from object creation.
        """
        self.designation = info['pdes']
        self.name = info['name'] # will sanitize at ingest, empty strings will be set to None
        self.diameter = info['diameter'] # or float('nan') to be set at input
        self.hazardous = info['pha'] # Boolean also to be set at ingest.

        # Create an empty initial collection of linked approaches.
        self.approaches = []

    @property
    def des(self):
        """ gets the unique identifier of this NEO as a property """
        return self.designation

    @property
    def fullname(self):
        """Return a representation of the full name of this NEO. 
        In this case, it is simply the two combed together"""
        if self.name is None:
            local_name = 'unnamed NEO'
        else:
            local_name = self.name
        return f'{self.designation} - {local_name}'

    def append_approach(self,approach):
        """ Appends an approach to this element. 
        :param a CloseApproach instance
        """
        self.approaches.append(approach)

    def __str__(self):
        """Returns an easy to read summary of the object as a sentance. 
        Tells the user its PDES, name, and if its dangerous"""
        if self.name:  
            begin = f"A NearEarthObject with a PDES as {self.designation}, \
                commonly known as {self.name!r}. "
        else:
            begin = f"An unnamed NearEarthObject with a PDES as {self.designation}. "
        if self.hazardous:
            end = "It is considered potentially hazardous."
        else:
            end = "It is not considered a danger to earth"
        return begin + end

    def __repr__(self):
        """Return `repr(self)`, a computer-readable string representation of this object."""
        return f"NearEarthObject(designation={self.designation!r}, name={self.name!r}, " \
               f"diameter={self.diameter:.3f}, hazardous={self.hazardous!r})"

    def serialize(self):
        """ Returns properties of this NEO as a Python dictionary """
        asDict = {
            'designation': self.designation,
            'name': self.name,
            'diameter_km': self.diameter,
            'potentially_hazardous': self.hazardous
        }
        return asDict


class CloseApproach:
    """A close approach to Earth by an NEO.

    A `CloseApproach` encapsulates information about the NEO's close approach to
    Earth, such as the date and time (in UTC) of closest approach, the nominal
    approach distance in astronomical units, and the relative approach velocity
    in kilometers per second.

    A `CloseApproach` also maintains a reference to its `NearEarthObject` -
    initially, this information (the NEO's primary designation) is saved in a
    private attribute, but the referenced NEO is eventually replaced in the
    `NEODatabase` constructor.
    """


    def __init__(self, **info):
        """Create a new `CloseApproach`.

        :param info: A dictionary of excess keyword arguments supplied to the constructor.
            The expected arguments are
            
            designation - string value for the NASA pdes
            time - a datetime object
            distance - a float representing the distance
            velocity - a flot represeting the relative velocity of the object.

        Similiar as the NearEarthObject class, 
        all data transformation/ sanitization is done prior to the invocation of this function.
        Code for that sanitization is also found in extract.py
        """

        self._designation = info['designation']
        self.time = info['time']
        self.distance = info['distance']
        self.velocity = info['velocity']

        # Create an attribute for the referenced NEO, originally None.
        self.neo = None

    @property 
    def datetime(self):
        """ gets the time as a raw datetime object. May be useful for sorting """
        return self.time

    @property
    def des(self):
        """ returns NASA's unique identifer of the object """
        return self._designation

    @property
    def hash_key(self):
        """ Returns a unique hash key for this event and object. 
        Would be good as primary key in a Database """
        hash_me = str(self.time) + self.des
        hash_me = hash_me.encode('utf-8')
        return hashlib.sha256(hash_me)

    @property
    def time_str(self):
        """Return a formatted representation of this `CloseApproach`'s approach time.

        The value in `self.time` should be a Python `datetime` object. While a
        `datetime` object has a string representation, the default representation
        includes seconds - significant figures that don't exist in our input
        data set.

        The `datetime_to_str` method converts a `datetime` object to a
        formatted string that can be used in human-readable representations and
        in serialization to CSV and JSON files.
        """

        return datetime_to_str(self.time)

    def __str__(self):
        """Return `str(self)`. Can use the common name for the object"""
        if self.neo.name is not None:
            nameString = f'(commonly known as {self.neo.name})'
        else:
            nameString = "(an unnamed object)"
        return f'{self.time_str} - {self.des} {nameString} approached earth \
                    with a relative velocity of {self.velocity}.'

    def __repr__(self):
        """Return `repr(self)`, a computer-readable string representation of this object."""
        return f"CloseApproach(time={self.time_str!r}, distance={self.distance:.2f}, " \
               f"velocity={self.velocity:.2f}, neo={self.neo!r}, hash_key={self.hash_key})"

    def serialize(self):
        """ Returns the properties of the close encounter as a dictionary"""
        as_dict = {
            'datetime_utc': self.time_str,
            'distance_au': self.distance,
            'velocity_km_s': self.velocity
        }
        return as_dict
