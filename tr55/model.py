"""
TR-55 Model Implementation

A mapping between variable/parameter names found in the TR-55 document
and variables used in this program are as follows:
 * `precip` is referred to as P in the report
 * `runoff` is Q
 * `evaptrans` maps to ET, the evapotranspiration
 * `inf` is the amount of water that infiltrates into the soil (in inches)
 * `init_abs` is Ia, the initial abstraction, another form of infiltration
"""

from datetime import date
from tr55.tablelookup import lookup_et, lookup_p, lookup_bmp_infiltration, lookup_cn, is_bmp, is_built_type


def runoff_pitt(precip, land_use):
    """
    The Pitt Small Storm Hydrology method.  This comes from Table D in
    the 2010/12/27 document.  The output is a runoff value in inches.
    """
    const1 = +3.638858398e-2
    const2 = -1.243464039e-1
    const3 = +1.295682223e-1
    const4 = +9.375868043e-1
    const5 = -2.235170859e-2
    const6 = +0.170228067e0
    const7 = -3.971810782e-1
    const8 = +3.887275538e-1
    const9 = -2.289321859e-2
    impervious = (const1 * pow(precip, 3)) + (const2 * pow(precip, 2)) + (const3 * precip) + const4
    urban_grass = (const5 * pow(precip, 4)) + (const6 * pow(precip, 3)) + (const7 * pow(precip, 2)) + (const8 * precip) + const9
    runoff_vals = {
        'Water':          impervious,
        'LI_Residential': 0.20 * impervious + 0.80 * urban_grass,
        'HI_Residential': 0.65 * impervious + 0.35 * urban_grass,
        'Commercial':     impervious,
        'Industrial':     impervious,
        'Transportation': impervious,
        'UrbanGrass':     urban_grass
    }
    if land_use not in runoff_vals:
        raise Exception('Land use %s not a built-type' % land_use)
    else:
        return min(runoff, precip)


def runoff_nrcs(precip, soil_type, land_use):
    """
    The runoff equation from the TR-55 document.  The output is a
    runoff value in inches.
    """
    curve_number = lookup_cn(soil_type, land_use)
    potential_retention = (1000.0 / curve_number) - 10
    initial_abs = 0.2 * potential_retention
    precip_minus_initial_abs = precip - initial_abs
    runoff = pow(precip_minus_initial_abs, 2) / (precip_minus_initial_abs + potential_retention)
    return min(runoff, precip)


def simulate_tile(parameters, tile_string, pre_columbian=False):
    """
    Simulate a tile on a given day using the method given in the
    flowchart 2011_06_16_Stroud_model_diagram_revised.PNG.

    The first argument can be one of two types.  It can either be a
    date object, in which case the precipitation and
    evapotranspiration are looked up from the sample year table.
    Alternatively, those two values can be supplied directly via this
    argument as a tuple.

    The second argument is a string which contains a soil type and
    land use separted by a colon.

    The third argument is a boolean which is true if pre-Columbian
    circumstances are to be simulated and false otherwise.

    The return value is a triple of runoff, evapotranspiration, and
    infiltration.
    """
    soil_type, land_use = tile_string.split(':')

    pre_columbian_land_uses = set(['Water', 'WoodyWetland', 'HerbaceousWetland'])
    if pre_columbian:
        if land_use not in pre_columbian_land_uses:
            land_use = 'MixedForest'

    if type(parameters) is date:
        precip = lookup_p(parameters)  # precipitation
        evaptrans = lookup_et(parameters, land_use)  # evapotranspiration
    elif type(parameters) is tuple:
        precip, evaptrans = parameters
    else:
        raise Exception('First argument must be a date or a (P,ET) pair')

    if precip == 0.0:
        return (0.0, 0.0, 0.0)

    if is_bmp(tile_string):
        inf = lookup_bmp_infiltration(soil_type, land_use)  # infiltration
        runoff = precip - (evaptrans + inf)  # runoff
        return (max(runoff, 0.0), evaptrans, inf)  # Q, ET, Inf.

    if is_built_type(land_use) and precip <= 2.0:
        runoff = runoff_pitt(precip, land_use)
    else:
        runoff = runoff_nrcs(precip, soil_type, land_use)
    inf = precip - (evaptrans + runoff)
    return (runoff, evaptrans, max(inf, 0.0))


def tile_by_tile_tr55(parameters, tile_census, pre_columbian=False):
    """
    Simulate each tile and return the overall results.

    The first argument is either a day or a P,ET double (as in simulate_tile).

    The second argument is a dictionary (presumably converted from
    JSON) that gives the number of each type of tile in the query
    polygon.

    The output is a runoff, evapotranspiration, infiltration triple
    which is an average of those produced by all of the tiles.
    """
    if 'error' in tile_census:
        raise Exception('Tile census contains "error" key')
    if 'result' not in tile_census:
        raise Exception('Tile census does not contain "result" key')
    elif 'cell_count' not in tile_census['result']:
        raise Exception('Tile census does not contain "result.cell_count" key')
    elif 'distribution' not in tile_census['result']:
        raise Exception('Tile census does not contain "result.distribution" key')

    global_count = tile_census['result']['cell_count']

    def simulate(tile_string, local_count):
        """
        A local helper function which captures various values.
        """
        return [(x * local_count) / global_count for x in simulate_tile(parameters, tile_string, pre_columbian)]

    results = [simulate(tile, n) for tile, n in tile_census['result']['distribution'].items()]
    return reduce(lambda (a, b, c), (x, y, z): (a+x, b+y, c+z), results, (0.0, 0.0, 0.0))
