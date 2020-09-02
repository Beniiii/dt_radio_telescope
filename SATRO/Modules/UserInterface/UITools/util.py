import os.path
import numpy as np
import math
from astropy.io import fits
from astropy.wcs import WCS
from astropy.stats import scott_bin_width
from matplotlib import pyplot as plt, gridspec as gridspec
from Pipeline.util import get_decimal_from_string


def load_fits_files(folder):
    """
    Returns *.image.fits, *.residual.fits and *.fidelity.fits where * gets replaced by the given folder name.
    :param folder: The folder name.
    :return: fits_files: A list containing the fits files.
    """
    fits_files = [fits.open(folder + ".image.fits"),
                  fits.open(folder + ".residual.fits"),
                  fits.open(folder + ".fidelity.fits")]
    return fits_files


def create_analysis_plot(fits, name, sources):
    """
    Creates a matplotlib plot from given FITS file. The plot includes the image, image distribution, on- and off-source
    distribution and statistical information.

    :param fits: The FITS file to be plotted.
    :param name: The name of the FITS file, used in plots
    :param sources: The directions of the sources in the image.
    :return: fig: The created matplotlib figure.
    """
    fig = plt.figure(figsize=(13, 9))
    fig.canvas.set_window_title("Analysis of " + name)
    #fig.set_facecolor('black')

    grid = gridspec.GridSpec(9, 2, wspace=0.4, hspace=0.05, width_ratios=[4, 3])

    wcs = WCS(fits[0].header, fix=False)
    data_image = np.array(fits[0].data).squeeze()

    sources_directions = []
    source_sizes = []
    for source in sources:
        direction = (source['sp_direction_ra'], source['sp_direction_dec'])
        sources_directions.append(direction)


    data_onsource = remove_nan_values(create_masked_data(wcs, data_image, sources, invert=True))
    data_offsource = remove_nan_values(create_masked_data(wcs, data_image, sources, invert=False))
    rms = calculate_rms(data_image)
    rms_onsource = calculate_rms(data_onsource)
    rms_offsource = calculate_rms(data_offsource)
    dr = calculate_dr(data_image, rms)
    dr_onsource = calculate_dr(data_image, rms_onsource)
    dr_offsource = calculate_dr(data_image, rms_offsource)
    stats = stats_dict(data_image)

    try:
        image_plot = fig.add_subplot(grid[:-2, 0], projection=wcs)
    except:
        image_plot = fig.add_subplot(grid[:-2, 0])
    im = image_plot.imshow(data_image, cmap='jet', origin='lower')
    image_plot.set_title(name)
    image_plot.set_xlabel('RA (J2000)')
    image_plot.set_ylabel('DEC (J2000)')
    cmap = fig.colorbar(im, ax=image_plot, fraction=0.046, pad=0.04)
    cmap.set_label(fits[0].header["BUNIT"])
    image_plot.text(0.05, -0.45,
                    "maximum pixel value: " + str(stats["max"]) + "\n" +
                    "minimum pixel value: " + str(stats["min"]) + "\n" +
                    "mean pixel value: " + str(stats["mean"]) + "\n" +
                    "median pixel value: " + str(stats["median"]) + "\n" +
                    "standard deviation about mean: " + str(stats["sigma"]) + "\n" +
                    "sum of pixel values: " + str(stats["sum"]) + "\n" +
                    "size of all pixel values: " + str(stats["size"]) + "\n",
                    transform=image_plot.transAxes)

    hist_plot = fig.add_subplot(grid[0:2, 1])
    hist_plot.hist(remove_nan_values(data_image.flatten()), bins="scott")
    hist_plot.set_title("Image Distribution")
    hist_plot.text(0.8, 0.8, "RMS: " + str(rms) + "\n" + "DR: " + str(dr), horizontalalignment='center',
                   verticalalignment='center', transform=hist_plot.transAxes)

    hist_on_plot = fig.add_subplot(grid[3:5, 1])
    hist_on_plot.hist(data_onsource.flatten(), bins="sturges")
    hist_on_plot.set_title("On-Source Distribution")
    hist_on_plot.text(0.8, 0.8, "RMS: " + str(rms_onsource) + "\n" + "DR: " + str(dr_onsource),
                      horizontalalignment='center', verticalalignment='center',
                      transform=hist_on_plot.transAxes)

    hist_off_plot = fig.add_subplot(grid[6:8, 1])
    hist_off_plot.hist(data_offsource.flatten(), bins="scott")
    hist_off_plot.set_title("Off-Source Distribution")
    hist_off_plot.text(0.8, 0.8, "RMS: " + str(rms_offsource) + "\n" + "DR: " + str(dr_offsource),
                       horizontalalignment='center', verticalalignment='center',
                       transform=hist_off_plot.transAxes)

    return fig


def create_comparison_plot(fits, name):
    """
    Creates a matplotlib plot from given FITS file. The plot includes the image, image distribution and
    statistical information.

    :param fits: The FITS file to be plotted.
    :param name: The name of the FITS file, used in plots
    :return: fig: The created matplotlib figure.
    """
    title = name.replace(".fits", "")
    fig = plt.figure(figsize=(13, 9))
    fig.set_facecolor('black')
    fig.canvas.set_window_title(title)

    grid = gridspec.GridSpec(3, 3, wspace=0.4, hspace=0.4)

    wcs = WCS(fits[0].header, fix=False)
    data_image = np.array(fits[0].data).squeeze()

    rms = calculate_rms(data_image)
    dr = calculate_dr(data_image, rms)
    stats = stats_dict(data_image)

    try:
        image_plot = fig.add_subplot(grid[0:2, 0:2], projection=wcs)
    except:
        image_plot = fig.add_subplot(grid[0:2, 0:2])
    im = image_plot.imshow(data_image, cmap='jet', origin='lower')
    image_plot.set_title(title)
    image_plot.set_xlabel('RA (J2000)')
    image_plot.set_ylabel('DEC (J2000)')
    cmap = fig.colorbar(im, ax=image_plot, fraction=0.046, pad=0.04)
    cmap.set_label('Jy/beam')
    image_plot.text(1.5, 0.4,
                    "maximum pixel value: " + str(stats["max"]) + "\n" +
                    "minimum pixel value: " + str(stats["min"]) + "\n" +
                    "mean pixel value: " + str(stats["mean"]) + "\n" +
                    "median pixel value: " + str(stats["median"]) + "\n" +
                    "standard deviation about mean: " + str(stats["sigma"]) + "\n" +
                    "sum of pixel values: " + str(stats["sum"]) + "\n" +
                    "size of all pixel values: " + str(stats["size"]) + "\n",
                    transform=image_plot.transAxes)

    hist_plot = fig.add_subplot(grid[2, :])
    hist_plot.hist(remove_nan_values(data_image.flatten()), bins="scott")
    hist_plot.set_title("Image Distribution")
    hist_plot.text(0.95, 0.85, "RMS: " + str(rms) + "\n" + "DR: " + str(dr), horizontalalignment='center',
                   verticalalignment='center', transform=hist_plot.transAxes)

    return fig


def check_folder(directory, name_folder):
    """
    Validates given directory if it meets the requirements to be read from the analysis tool. The folder must
    contain a "sources.pkl"-file and directory named "FITS_Files" where the fits files are located. Output folders
    from the pipeline meet these requirements. Returns true if the directory is valid.

    :param directory: The directory that will be validated.
    :param name_folder: The generated name of the output folder.
    :return: valid: If the directory is valid or not.
    """
    valid = True
    error_messages = []
    if not os.path.isdir(directory + "/FITS_Files"):
        error_messages.append("- No FITS_Files folder.")
        valid = False
    else:
        if not os.path.isfile(directory + "/FITS_Files/" + name_folder + ".image.fits"):
            error_messages.append("- No *.image.fits.")
            valid = False
        if not os.path.isfile(directory + "/FITS_Files/" + name_folder + ".residual.fits"):
            error_messages.append("- No *.residual.fits.")
            valid = False
        if not os.path.isfile(directory + "/FITS_Files/" + name_folder + ".fidelity.fits"):
            error_messages.append("- No *.fidelity.fits.")
            valid = False
    if not os.path.isfile(directory + "/Skymodel/sources.pkl"):
        error_messages.append("- No sources.pkl.")
        valid = False
    return valid, error_messages


def create_masked_data(wcs, data, sources, invert=False):
    """
    Calculates a masked array with the size of the source around given coordinated either masked (invert=False), or
    everything else is masked but the slice (Invert=True).

    :param wcs: The world coordinate system of the data
    :param data: The data Array.
    :param sources: The sources of the image
    :param invert: Invert the masked array or not.
    :return: masked_array: The masked array.
    """
    if invert:
        mask = np.ones(data.shape, dtype=bool)
    else:
        mask = np.zeros(data.shape, dtype=bool)

    coordinates = []
    sizes = []
    for source in sources:
        direction = (source['sp_direction_ra'], source['sp_direction_dec'])
        coord = calculate_pixcoord(wcs, direction)
        coordinates.append(coord)
        if source['sp_shape'] == "point":
            size_pixels = (int(data.shape[0] / 40), int(data.shape[1] / 40))
        else:
            size_value, units = get_decimal_from_string(source['sp_majoraxis'])
            if units.strip() == "arcsec":
                size = size_value / 3600
            elif units.strip() == "arcmin":
                size = size_value / 60
            else:
                raise ValueError(units + " is invalid as units for sp_majoraxis. Use arcmin or arcsec.")
            pix_coords_src = calculate_pixcoord(wcs, (direction[0] + size, direction[1] - size))
            size_pixels = pix_coords_src - coord

        size_pixels = (int(abs(math.ceil(size_pixels[0]))), int(abs(math.ceil(size_pixels[1]))))
        sizes.append(size_pixels)

    for i in range(len(coordinates)):
        x_lower = int(coordinates[i][0]) - sizes[i][0]
        x_upper = int(coordinates[i][0]) + sizes[i][0]
        y_lower = int(coordinates[i][1]) - sizes[i][1]
        y_upper = int(coordinates[i][1]) + sizes[i][1]

        # check if source is outside the image
        if (x_lower < 0 and x_upper < 0) or (x_lower >= data.shape[0] and x_upper >= data.shape[0]) or \
           (y_lower < 0 and y_upper < 0) or (y_lower >= data.shape[1] and y_upper >= data.shape[1]):
            pass

        else:
            # cut off the source of necessary
            x_lower = raise_to_zero(x_lower)
            x_upper = lower_to_size(x_upper, data.shape[0])
            y_lower = raise_to_zero(y_lower)
            y_upper = lower_to_size(y_upper, data.shape[0])

            mask[x_lower: x_upper, y_lower: y_upper] = not invert

    masked_array = np.ma.masked_array(data, mask, fill_value=float('NaN'))
    return masked_array


def raise_to_zero(number):
    """
    Raise a number to zero if it is smaller.

    :param number: The number to be raised.
    :return: number: The raised number.
    """
    if number < 0:
        number = 0
    return number


def lower_to_size(number, size):
    """
    Lowers a number to the given size - 1.

    :param number: The number to be lowered.
    :param size: The given size as threshold.
    :return: number: The lowered number.
    """
    if number >= size:
        number = size-1
    return number


def calculate_rms(data):
    """
    Calculates and returns root mean square of given data array rounded to 4 places after decimal point.
    :param data: The dara array.
    :return: rms: The root mean square score.
    """
    rms = np.sqrt(np.nanmean(np.square(data)))
    return rms.round(4)


def calculate_dr(data, rms):
    """
    Calculates and returns the dynamic range of given data array.

    :param data: The data array.
    :param rms: The root mean square score.
    :return: dr: The dynamic range.
    """
    dr = np.nanmax(data) / rms
    return dr.round(4)


def stats_dict(data):
    """
    Calculates several statistical information and returns them in a dictionary. Measures to be calculated are:
    number of data points, maximum and minimum value, mean, median, standard deviation about mean and the sum.

    :param data: The data array.
    :return: stats: The statistical information as dictionary.
    """
    stats = {'size': np.size(data),
             'max': np.nanmax(data).round(3),
             'min': np.nanmin(data).round(3),
             'mean': np.mean(data).round(3),
             'median': np.median(data).round(3),
             'sigma': np.std(data).round(3),
             'sum': np.sum(data).round(3)}
    return stats


def calculate_pixcoord(wcs, direction):
    """
    Calculates and returns pixel coordinates from given world coordinates and direction (ra, dec in degrees).

    :param wcs: The world coordinates object.
    :param direction: The direction (ra, dec in degrees).
    :return: An tuple with the pixel coordinates in the format (x,y).
    """
    ra_deg = direction[0]
    dec_deg = direction[1]

    coordinates = np.array(wcs.wcs_world2pix(ra_deg, dec_deg, 0, ra_dec_order=True))
    return np.array([coordinates[1], coordinates[0]])


def remove_nan_values(array):
    """
    Returns an array free of nan values from given array.

    :param array: The data array.
    :return: filteres_array: The data array without nan values.
    """
    nan_array = np.isnan(array)
    not_nan_array = ~ nan_array
    filtered_array = array[not_nan_array]
    return filtered_array


