"""Provide filters for querying close approaches
and limit the generated results.

The `create_filters` function produces a collection of
objects that is used by the `query` method to generate a
stream of `CloseApproach` objects that match all of the desired
criteria. The arguments to `create_filters` are provided by
the main module and originate from the user's command-line options.

This function can be thought to return a collection of
instances of subclasses of `AttributeFilter` - a 1-argument
callable (on a `CloseApproach`) constructedfrom a comparator
(from the `operator` module), a reference value, and a class
method `get` that subclasses can override to
fetch an attribute of interest from the supplied
`CloseApproach`.

The `limit` function simply limits the maximum number
of values produced by an iterator.
"""
import operator
import itertools
from helpers import numerical_to_datetime


class UnsupportedCriterionError(NotImplementedError):
    """A filter criterion is unsupported."""


class AttributeFilter:
    """A general superclass for filters on comparable attributes.

    An `AttributeFilter` represents the search criteria pattern
    comparing some attribute of a close approach (or its attached NEO)
    to a reference value. It essentially functions as a callable predicate
    for whether a `CloseApproach` object satisfies the encoded criterion.

    It is constructed with a comparator operator and a reference value, and
    calling the filter (with __call__) executes `get(approach) OP value` (in
    infix notation).

    Concrete subclasses can override the `get` classmethod to provide custom
    behavior to fetch a desired attribute from the given `CloseApproach`.
    """
    def __init__(self, op, value):
        """Construct a new `AttributeFilter` from an
        binary predicate and a reference value.

        The reference value will be supplied as the second (right-hand side)
        argument to the operator function. For example, an `AttributeFilter`
        with `op=operator.le` and `value=10` will, when called on an approach,
        evaluate `some_attribute <= 10`.

        :param op: A 2-argument predicate comparator (such as `operator.le`).
        :param value: The reference value to compare against.
        """
        self.op = op
        self.value = value

    def __call__(self, approach):
        """Invoke `self(approach)`."""
        return self.op(self.get(approach), self.value)

    @classmethod
    def get(cls, approach):
        """Get an attribute of interest from a close approach.

        Concrete subclasses must override this method to get an
        attribute of interest from the supplied `CloseApproach`.

        :param approach: A `CloseApproach` on which to evaluate this filter.
        :return: The value of an attribute of interest,
        comparable to `self.value` via `self.op`.
        """
        raise UnsupportedCriterionError

    def __repr__(self):
        return f"{self.__class__.__name__}\
            (op=operator.{self.op.__name__}, value={self.value})"


class CheckDate(AttributeFilter):
    """ Is a filter class that compares to a CloseApproach date."""
    @classmethod
    def get(cls, approach):
        # Returns the raw datetime object.
        return approach.datetime

    def __str__(self):
        return f"Filters on a value {self.op.__name__} on \
            a date object."


class CheckDistance(AttributeFilter):
    """ Is a filter class that compares to a
    CloseApproach distance from earth."""
    @classmethod
    def get(cls, approach):
        # Returns the distance
        return approach.distance

    def __str__(self):
        return f"Filters on a value {self.op.__name__} on \
            a float object (distance)."


class CheckVelocity(AttributeFilter):
    """ Is a filter class that compares to a
    CloseApproach relative velocity."""
    @classmethod
    def get(cls, approach):
        # Returns the Velocity
        return approach.velocity

    def __str__(self):
        return f"Filters on a value {self.op.__name__} on a \
            float object (velocity)."


class CheckDiameter(AttributeFilter):
    """ Is a filter class that compares to a NEO's diamater"""
    @classmethod
    def get(cls, approach):
        # Returns the distance
        return approach.neo.diameter

    def __str__(self):
        return f"Filters on a value {self.op.__name__} on \
            a float object (diameter)."


class CheckHazardous(AttributeFilter):
    """ is a filter class that compares to whether
    or not an NEO is dangerous. """
    @classmethod
    def get(cls, approach):
        # Returns the if this is a hazardous object
        return approach.neo.hazardous

    def __str__(self):
        return f"Filters on a value {self.op.__name__} \
            on a boolean object (is dangerous?)."


def create_filters(
        date=None, start_date=None, end_date=None,
        distance_min=None, distance_max=None,
        velocity_min=None, velocity_max=None,
        diameter_min=None, diameter_max=None,
        hazardous=None
):
    """Create a collection of filters from user-specified criteria.

    Each argument is provided by the main module with a value from the
    user's options at the command line. Each corresponds to a different type
    of filter. For example, the `--date` option corresponds to the `date`
    argument, and represents a filter that selects close approaches that
    occurred within that given date. Similarly, the `--min-distance` option
    corresponds to the `distance_min` argument, and represents a filter that
    selects close approaches whose nominal approach distance is at least that
    far away from Earth. Each option is `None` if not specified at the command
    line (in particular, this means that the `--not-hazardous` flag results in
    `hazardous=False`, not to be confused with `hazardous=None`).

    The return value must be compatible with the `query` method of
    `NEODatabase` because the main module directly
    passes this result to that method. For now,
    this can be thought of as a collection of `AttributeFilter`s.

    :param date: A `date` on which a matching `CloseApproach` occurs.
    :param start_date: A `date` on or after which
    a matching `CloseApproach` occurs.
    :param end_date: A `date` on or before which
    a matching `CloseApproach` occurs.
    :param distance_min: A minimum nominal approach distance for
    a matching `CloseApproach`.
    :param distance_max: A maximum nominal approach distance for
    a matching `CloseApproach`.
    :param velocity_min: A minimum relative approach velocity for
    a matching `CloseApproach`.
    :param velocity_max: A maximum relative approach velocity for
    a matching `CloseApproach`.
    :param diameter_min: A minimum diameter of the NEO of
    a matching `CloseApproach`.
    :param diameter_max: A maximum diameter of the NEO of
    a matching `CloseApproach`.
    :param hazardous: Whether the NEO of a matching `CloseApproach`
    is potentially hazardous.
    :return: A collection of filters for use with `query`.
    """

    # this is the list to be returned.
    my_filters = []

    # op_dict maps the parameter to the expect operator.
    op_dict = {
        'date': operator.eq,
        'start_date': operator.ge,
        'end_date': operator.le,
        'distance_min': operator.ge,
        'distance_max': operator.le,
        'velocity_min': operator.ge,
        'velocity_max': operator.le,
        'diameter_min': operator.ge,
        'diameter_max': operator.le,
        'hazardous': operator.eq
    }

    # filter dict maps the parameter to the corresponding function.
    filter_dict = {
        'date': None,
        'start_date': CheckDate,
        'end_date': CheckDate,
        'distance_min': CheckDistance,
        'distance_max': CheckDistance,
        'velocity_min': CheckVelocity,
        'velocity_max': CheckVelocity,
        'diameter_min': CheckDiameter,
        'diameter_max': CheckDiameter,
        'hazardous': CheckHazardous
    }

    # this object exists entirely to avoid getting lint'ed
    # by PIP 8 standards.
    # Original idea was to simply grab by *locals().
    arguments_dict = {
        'date': date,
        'start_date': start_date,
        'end_date': end_date,
        'distance_min': distance_min,
        'distance_max': distance_max,
        'velocity_min': velocity_min,
        'velocity_max': velocity_max,
        'diameter_min': diameter_min,
        'diameter_max': diameter_max,
        'hazardous': hazardous
    }

    for key, value in arguments_dict.items():
        # If the value is not None,
        # then make the corresponding filters
        if value is not None:
            # dates have an edge case.
            # hours and minutes must be applied
            if key == 'start_date':
                value = numerical_to_datetime(str(value) + ' 00:00')
            if key == 'end_date':
                value = numerical_to_datetime(str(value) + ' 23:59')

            # If an exact date is selected, we use the
            # same filters start_date and end_date
            if key == 'date':
                start = numerical_to_datetime(str(value) + ' 00:00')
                end = numerical_to_datetime(str(value) + ' 23:59')
                my_filters.append(filter_dict['start_date']
                                  (op_dict['start_date'], start))
                my_filters.append(filter_dict['end_date']
                                  (op_dict['end_date'], end))
            else:
                # all other functions will not need transformation.
                my_filters.append(filter_dict[key](op_dict[key], value))

    return my_filters


def limit(iterator, n=None):
    """Produce a limited stream of values from an iterator.

    If `n` is 0 or None, don't limit the iterator at all,
    i.e the iterator argument is simply returned.

    :param iterator: An iterator of values.
    :param n: The maximum number of values to produce.
    :yield: The first (at most) `n` values from the iterator.
    """
    if n == 0 or n is None:
        return iterator

    return itertools.islice(iterator, 0, n)
