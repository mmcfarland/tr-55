# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division

"""
Various routines to do table lookups.
"""

from tr55.tables import BMPS, BUILT_TYPES, LAND_USE_VALUES, \
    NON_NATURAL, POLLUTANTS, POLLUTION_LOADS, AREA_CALC_BMPS


def lookup_infiltration_factor(land_use):
    """
    Lookup the infiltration factor for bmps.
    """
    if land_use not in LAND_USE_VALUES:
        raise KeyError('Unknown land use: %s' % land_use)
    elif 'ki' not in LAND_USE_VALUES[land_use]:
        raise KeyError('No infiltration factor for land use %s' % land_use)
    else:
        return LAND_USE_VALUES[land_use]['infiltration_factor']


def lookup_ki(land_use):
    """
    Lookup the landuse coefficient.
    """
    if land_use not in LAND_USE_VALUES:
        raise KeyError('Unknown land use: %s' % land_use)
    elif 'ki' not in LAND_USE_VALUES[land_use]:
        raise KeyError('No ki for land use %s' % land_use)
    else:
        return LAND_USE_VALUES[land_use]['ki']


def lookup_cn(soil_type, land_use):
    """
    Lookup the runoff curve number for a particular soil type and land use.
    """
    if land_use not in LAND_USE_VALUES:
        raise KeyError('Unknown land use: %s' % land_use)
    elif 'cn' not in LAND_USE_VALUES[land_use]:
        raise KeyError('No curve numbers for land use %s' % land_use)
    elif soil_type not in LAND_USE_VALUES[land_use]['cn']:
        raise KeyError('Unknown soil type: %s' % soil_type)
    else:
        return LAND_USE_VALUES[land_use]['cn'][soil_type]


def is_bmp(land_use):
    """
    Test to see if the land use is a BMP.
    """
    return land_use in BMPS


def is_area_bmp(bmp):
    """
    Test to see if the BMP is of a type that requires a total area
    loading calculation and not a cell by cell runoff calculation
    """
    return bmp in AREA_CALC_BMPS


def is_built_type(land_use):
    """
    Test to see if the land use is a "built type".
    """
    return land_use in BUILT_TYPES


def make_precolumbian(land_use):
    """
    Project the given land use to a Pre-Columbian one.
    """
    if land_use in NON_NATURAL:
        return 'mixed_forest'
    else:
        return land_use


def lookup_load(nlcd_class, pollutant):
    """
    Get the Event Mean Concentration of `pollutant` for land use
    class `nlcd_class`
    """
    if pollutant not in ['tn', 'tp', 'bod', 'tss']:
        raise KeyError('Unknown pollutant type: %s' % pollutant)
    elif nlcd_class not in POLLUTION_LOADS:
        raise KeyError('Unknown NLCD class: %s' % nlcd_class)
    else:
        return POLLUTION_LOADS[nlcd_class][pollutant]


def lookup_nlcd(land_use):
    """
    Get the NLCD number for a particular human-readable land use.
    """
    if land_use not in LAND_USE_VALUES:
        raise KeyError('Unknown land use type: %s' % land_use)
    elif 'nlcd' not in LAND_USE_VALUES[land_use]:
        raise KeyError('Land use type %s does not have an NLCD class defined',
                       land_use)
    else:
        return LAND_USE_VALUES[land_use]['nlcd']


def get_pollutants():
    """
    Return the list of pollutants.
    """
    return POLLUTANTS
