import datetime
import logging
import os
import pickle
import numpy as np
from astropy import constants as const


def configure_logger(name):
    """
    Configures and returns a logger.

    :param: folder: The folder name of the iteration.
    :returns:
        - logger: The configured logger.
        - logfile: Name of the logfile.
    """
    logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s", level=logging.INFO)
    logger = logging.getLogger(name)

    # Create handlers
    date = str(datetime.date.today())
    now = datetime.datetime.now()
    current_time = now.strftime("%H%M%S")
    filename = 'pipeline-' + date.replace('-', '') + '-' + current_time + '.log'

    f_handler = logging.FileHandler(filename, 'w')
    f_handler.setLevel(logging.INFO)

    f_format = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    f_handler.setFormatter(f_format)

    # Add handlers to the logger
    logger.addHandler(f_handler)
    return logger, filename


def create_output_name(antennalist, mode, var_param_set, incenter, inwidth, integration, skymodel, var_param="",
                       index=""):
    """
    Creates and returns the output folder name out of given parameters.

    :param antennalist: The selected antenna configuration.
    :param mode: The selected simulation mode.
    :param var_param_set: The selected set of varying parameters.
    :param incenter: The incenter from simobserve parameters.
    :param inwidth: The inwidth from simobserve parameters.
    :param integration: The integration from simobserve parameters.
    :param skymodel: The selected sky-model.
    :param var_param: The current varying parameter. Only used in multiple runs mode.
    :param index: The current value index of the varying parameter. Only used in multiple runs mode.
    :return: folder: The output folder name.
    """
    antennalist = antennalist[:-4].replace(".", "_")
    var_param_sets = {
        'Instrumental': "sim",
        'Sky-model': "sm",
        'Sources': "sp",
        'Instrumental & Sky-model': "sim-sm",
        'Instrumental & Sources': "sim-sp",
        'Sky-model & Sources': "sm-sp"}
    if mode == "Multiple Runs":
        mode = "mult"
        ending = "-" + var_param + str(index)
    else:
        mode = "single"
        ending = ""
    if skymodel == "Custom":
        skymodel = "custom"
    else:
        skymodel = "haslam"

    if mode == "single":
        folder = antennalist + "-" + mode + "-" + "f_" + str(incenter) + "-" + \
                 "df_" + str(inwidth) + "-" + "dt_" + str(integration) + "-" + "sm_" + skymodel + ending
    else:
        folder = antennalist + "-" + mode + "-" + var_param_sets[var_param_set] + "-" + "f_" + str(incenter) + "-" + \
                 "df_" + str(inwidth) + "-" + "dt_" + str(integration) + "-" + "sm_" + skymodel + ending
    return folder


def rename_casa_images(folder, file_ext):
    """
    Renames CASA images in the given output folder.

    :param folder: The output folder name.
    :param file_ext: The file extension name.
    """
    if os.path.exists(folder) and os.path.isdir(folder):
        for image in os.listdir(folder):
            file_ext = file_ext.replace(folder, "")
            new_name = image.replace(file_ext, "")
            if os.path.exists(folder + "/" + image):
                os.rename(folder + "/" + image, folder + "/" + new_name)


def find_index_of_nearest_xy(y_array, x_array, y_point, x_point):
    """
    Finds and returns the xy index of the haslam map that corresponds to a (Alt,Azimuth) pair.

    :param y_array: y-axis of the map
    :param x_array: x-axis of the map
    :param y_point: y coordinates of the point in radians.
    :param x_point: x coordinates of the point in radians.
    :returns:
        - idy[0]: y index
        - idx[0]: x index
        - distance: distance to the nearest pixel in the haslam map
    """
    distance = (y_array - y_point) ** 2 + (x_array - x_point) ** 2
    idy, idx = np.where(distance == distance.min())
    return idy[0], idx[0], distance


def get_decimal_from_string(string):
    """
    Extracts and returns the decimal value of a string and the units.

    :param string: The input string.
    :returns:
        - number: The decimal number as float.
        - units: The corresponding units as string.
    """
    string = str(string)
    numeric = '0123456789-.'
    index = 0
    for i, c in enumerate(string + " "):
        index = i
        if c not in numeric:
            break
    number = string[:index]
    units = string[index:len(string)]
    return float(number), units


def transform_frequency(frequency, units):
    """
    Transforms the frequency amount to GHz from either Hz, kHz or MHz.

    :param frequency: The frequency to transform.
    :param units: The units of the frequency.
    :return: frequency: The transformed frequency.
    """
    if units == "Hz":
        frequency = frequency / 10 ** 9
    elif units == "kHz":
        frequency = frequency / 10 ** 6
    elif units == "MHz":
        frequency = frequency / 10 ** 3
    elif units == "GHz":
        pass
    else:
        raise ValueError(units + " is invalid as units for frequency. Use Hz, kHz, MHz or GHz.")
    return frequency


def convert_deg_to_dms(deg):
    """
    Converts input degrees to declination and returns the value in the format 30d0m0.0s.

    :param deg: The input degree value.
    :return: dms: The converted degree value as dms string.
    """
    d = int(deg)
    rest = abs((deg - d) * 60)
    m = int(rest)
    rest = rest - m
    s = rest * 60
    dms = str(d) + "d" + str(m) + "m" + format(s, ".2f") + "s"
    return dms


def convert_deg_to_hour(deg):
    """
    Converts input degrees to right ascension and returns the value in the format 12h0m0.0s.

    :param deg: The input degree value.
    :return: ha: The converted degree value as hour angle string.
    """
    dec = deg / 15
    h = int(dec)
    rest = abs((dec - h) * 60)
    m = int(rest)
    rest = rest - m
    s = rest * 60
    ha = str(h) + "h" + str(m) + "m" + format(s, ".2f") + "s"
    return ha


def concat_ra_dec(ra, dec):
    """
    Concatenates right ascension and declination including the epoch and returns a direction string in the format
    J2000 12h0m0.0s 30d0m0.0s.

    :param ra: The right ascension string.
    :param dec: The declination string.
    :return: direction: The sky direction as concatenated string.
    """
    direction = "J2000 " + ra + " " + dec
    return direction


def get_substring_til_char(string, char):
    """
    Extracts and returns a substring from a given string until given character (including the character).

    :param string: The input string.
    :param char: The character where to stop.
    :return: substring: The extracted substring.
    """
    substring = ""
    for c in string:
        substring = substring + c
        if c == char:
            break
    return substring


def calculate_beam_size(freq, dish_diam):
    """
    Calculates the beam size from given frequency and dish diameter.

    :param freq: The frequency in GHz.
    :param dish_diam: The dish diameter.
    :return: beam_size: The beam size.
    """
    # const.c is the speed of light
    beam_size = const.c.value / (freq * 10 ** 9 * dish_diam)
    return beam_size


def get_vis_string(folder, antennalist):
    """
    Returns the name of the measurement set created from the output folder name and the antenna list.

    :param folder: The output folder name.
    :param antennalist: The name of the antenna list.
    :return: vis: The name of the measurement set.
    """
    vis = folder + "." + antennalist.replace("cfg", "noisy.ms")
    return vis


def export_sources(sources, folder):
    """
    Exports the source parameters as pickle file to the specified folder.

    :param sources: The source parameters.
    :param folder: The target folder.
    """
    with open("sources.pkl", 'wb') as output:
        pickle.dump(sources, output, pickle.HIGHEST_PROTOCOL)
    os.system("mv sources.pkl " + folder + '/' + 'Skymodel')
