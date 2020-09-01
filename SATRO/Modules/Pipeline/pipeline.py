from init_tools import cltool, iatool, qatool
import os
import math
import numpy as np
import copy
import timeit
import pickle
import Pipeline.util as util
import shutil
import sys
from astropy.io import fits


def run(model):
    """
    Starts the AppPipeline with the given model as input to either simulate a single observation or multiple iterations
    with varying parameters. If there are multiple iterations, for each value of the varying parameters an iteration
    will be executed.

    :param model: The input model from GUI.
    """
    parameters_settings = get_params_settings(model)
    parameters_skymodel = get_params_skymodel(model)
    parameters_simobserve = get_params_simobserve(model)
    parameters_simanalyze = get_params_simanalyze(model)
    parameters_sources = get_params_sources(model)

    if model.mode == "Multiple Runs":
        multi_run(model, parameters_settings, parameters_skymodel, parameters_sources, parameters_simobserve,
                  parameters_simanalyze)

    elif model.mode == "Single Run":
        run_iteration(model, parameters_settings, parameters_skymodel, parameters_sources,
                      parameters_simobserve, parameters_simanalyze)


def multi_run(model, parameters_settings, parameters_skymodel, parameters_sources, parameters_simobserve,
              parameters_simanalyze):
    """
    Executes multiple iterations with given parameter sets. First, a sky-model will be created and sources added, then
    the observation will be simulated and analyzed. Output data will be moved to the provided output path from the
    model. This process will be done for each value for each varying parameter. If source parameters occur in the
    varying parameters, sources will be adjusted separately.

    :param model: The input model from the GUI.
    :param parameters_settings: Parameter set extracted from the model containing settings parameters.
                                See get_params_settings for detailed content.
    :param parameters_skymodel: Parameter set extracted from the model containing sky-model parameters.
                                See get_params_skymodel for detailed content.
    :param parameters_sources: Parameter set extracted from the model containing source parameters.
                               See get_params_sources for detailed content.
    :param parameters_simobserve: Parameter set extracted from the model containing simobserve parameters.
                                  See get_params_simobserve for detailed content.
    :param parameters_simanalyze: Parameter set extracted from the model containing simanalyze parameters.
                                  See get_params_simanalyze for detailed content.
    """
    parameter_sets_original = [parameters_skymodel, parameters_simobserve, parameters_simanalyze]
    parameter_sets = copy.deepcopy(parameter_sets_original)
    parameters_sources_original = copy.deepcopy(parameters_sources)

    var_param_values = model.var_param_values_lists
    for parameter in var_param_values.keys():
        if "Sources" in model.var_param_set:
            index = 0
            for value in var_param_values[parameter]:
                new_value = {parameter: value}
                for source in parameters_sources:
                    source.update(new_value)
                run_iteration(model, parameters_settings, parameter_sets[0], parameters_sources,
                              parameter_sets[1], parameter_sets[2], parameter, index)
                index = index + 1
            parameters_sources = copy.deepcopy(parameters_sources_original)

        for parameter_set in parameter_sets:
            if parameter in parameter_set.keys():
                index = 0
                for value in var_param_values[parameter]:
                    new_value = {parameter: value}
                    parameter_set.update(new_value)
                    run_iteration(model, parameters_settings, parameter_sets[0], parameters_sources,
                                  parameter_sets[1], parameter_sets[2], parameter, index)
                    index = index + 1
        parameter_sets = copy.deepcopy(parameter_sets_original)


def run_iteration(model, parameters_settings, parameters_skymodel, parameters_sources, parameters_simobserve,
                  parameters_simanalyze, parameter="", index=""):
    """
    Executes a single simulation with given parameter sets. First, a sky-model will be created and sources added, then
    the observation will be simulated and analyzed. Output data will be moved to the provided output path from the
    model.

    :param model: The input model from the GUI.
    :param parameters_settings: Parameter set extracted from the model containing settings parameters.
                                See get_params_settings for detailed content.
    :param parameters_skymodel: Parameter set extracted from the model containing sky-model parameters.
                                See get_params_skymodel for detailed content.
    :param parameters_sources: Parameter set extracted from the model containing source parameters.
                               See get_params_sources for detailed content.
    :param parameters_simobserve: Parameter set extracted from the model containing simobserve parameters.
                                  See get_params_simobserve for detailed content.
    :param parameters_simanalyze: Parameter set extracted from the model containing simanalyze parameters.
                                  See get_params_simanalyze for detailed content.
    :param parameter: The parameter name of the varying parameter. Only used in multiple runs mode.
    :param index: Index of the iteration of the parameter values. Only used in multiple runs mode.
    """
    start_time = timeit.default_timer()
    if not os.path.exists('Skymodel'):
        os.mkdir('Skymodel')
    if not os.path.exists('Taskfiles'):
        os.mkdir('Taskfiles')
    folder = util.create_output_name(parameters_settings["antennalist"], parameters_settings["mode"],
                                     parameters_settings["var_param_set"], parameters_simobserve["incenter"],
                                     parameters_simobserve["inwidth"], parameters_simobserve["integration"],
                                     parameters_settings["sm"], parameter, index)
    logger, logfile = util.configure_logger(folder + "-logger")
    if os.path.exists(folder) and os.path.isdir(folder):
        try:
            shutil.rmtree(folder)
        except:
            os.system("mv " + folder + " junk_" + logfile[-4])
    for directory in os.listdir(os.getcwd()):
        if "junk" in directory:
            logger.warn("There is still junk left, probably from a previously crashed simulation. Please remove it "
                        "manually from the following directory: \n" + os.getcwd())
            break

    logger.info("Starting iteration for " + folder)
    logger.info("Logfile: " + logfile)
    logger.info("Creating sky-model image")
    create_skymodel(model.exportfits, parameters_skymodel)
    if parameters_settings["sm"] == "Haslam-Map":
        logger.info("Interpolating with haslam all-sky map")
        create_haslam_map(parameters_settings, parameters_skymodel)
    logger.info("Adding sources")
    create_sources(parameters_sources)
    logger.info("Starting observation")
    run_simobserve(model.simobserve, parameters_settings, parameters_simobserve, folder)
    logger.info("Starting analysis")
    measurement_set = util.get_vis_string(folder, parameters_settings["antennalist"])
    file_ext = folder + '.' + parameters_settings["antennalist"].replace("cfg", "noisy")
    if not os.path.exists(folder + "/" + measurement_set):
        measurement_set = measurement_set.replace(".noisy", "")
        file_ext = file_ext.replace(".noisy", "")
    run_simanalyze(model.simanalyze, parameters_simanalyze, parameters_skymodel, measurement_set, folder)

    util.rename_casa_images(folder, file_ext)
    create_fits_files(model.exportfits, model.imhead, folder)

    logger.info("Moving output folder to " + parameters_settings["output_path"])
    os.system('mv Skymodel/ ' + folder)
    os.system('mv *.last Taskfiles')
    os.system('mv Taskfiles ' + folder)
    util.export_sources(parameters_sources, folder)
    if os.path.exists(parameters_settings["output_path"] + "/" + folder):
        logger.info("Output folder already exists. Overwriting output folder")
        shutil.rmtree(parameters_settings["output_path"] + "/" + folder)
    os.system('cp -RLf ' + folder + ' ' + parameters_settings["output_path"])
    shutil.rmtree(folder)
    elapsed = timeit.default_timer() - start_time
    logger.info("Iteration finished: See the task files and the CASA logfile for detailed information. \n" +
                "******************************* \n" +
                "Time elapsed: " + str(elapsed) + "s\n" +
                "*******************************")
    os.system('cp -RLf ' + logfile + ' ' + parameters_settings["output_path"] + '/' + folder)
    os.remove(logfile)


def get_params_settings(model):
    """
    Returns extracted general setting parameters as a dictionary from the model.
    Parameter keys: "mode", "sm", "output-path", "antennalist", "var_param_set".

    :param model: The input model from the GUI.
    :return: parameter_settings: A set of parameters for general settings extracted from the model as dictionary.
    """
    parameters_settings = {"mode": model.mode,
                           "sm": model.sm,
                           "telescope": float(model.telescope_diameters[model.telescope]),
                           "output_path": model.output_path,
                           "antennalist": model.antennalist,
                           "var_param_set": model.var_param_set
                           }
    return parameters_settings


def get_params_skymodel(model):
    """
    Returns extracted sky-model parameters as a dictionary from the model.
    Parameter keys: "sm_flux", "sm_fluxunit", "sm_polarization", "sm_direction_ra", "sm_direction_dec", "sm_shape",
    "sm_majoraxis", "sm_minoraxis", "sm_positionangle", "sm_frequency", "sm_index", "sm_spectrumtype", "sm_label",
    "component_frequency", "frequency_increment", "sm_cellsize", "sm_size".

    :param model: The input model from the GUI.
    :return: parameter_skymodel: A set of sky-model parameters from the model as dictionary.
    """
    df = model.fixed_params_sm
    parameters_skymodel = {"sm_flux": float(df[df["Name"] == 'sm_flux']["Value"].squeeze()),
                           "sm_fluxunit": df[df["Name"] == 'sm_fluxunit']["Value"].squeeze(),
                           "sm_polarization": df[df["Name"] == 'sm_polarization']["Value"].squeeze(),
                           "sm_direction_ra": float(df[df["Name"] == 'sm_direction_ra']["Value"].squeeze()),
                           "sm_direction_dec": float(df[df["Name"] == 'sm_direction_dec']["Value"].squeeze()),
                           "sm_shape": df[df["Name"] == 'sm_shape']["Value"].squeeze(),
                           "sm_majoraxis": df[df["Name"] == 'sm_majoraxis']["Value"].squeeze() +
                                           df[df["Name"] == 'sm_majoraxis'][
                                               "Units"].squeeze(),
                           "sm_minoraxis": df[df["Name"] == 'sm_minoraxis']["Value"].squeeze() +
                                           df[df["Name"] == 'sm_minoraxis'][
                                               "Units"].squeeze(),
                           "sm_positionangle": df[df["Name"] == 'sm_positionangle']["Value"].squeeze() +
                                               df[df["Name"] == 'sm_positionangle'][
                                                   "Units"].squeeze(),
                           "sm_frequency": df[df["Name"] == 'sm_frequency']["Value"].squeeze() +
                                           df[df["Name"] == 'sm_frequency'][
                                               "Units"].squeeze(),
                           "sm_index": float(df[df["Name"] == 'sm_index']["Value"].squeeze()),
                           "sm_spectrumtype": df[df["Name"] == 'sm_spectrumtype']["Value"].squeeze(),
                           "sm_label": df[df["Name"] == 'sm_label']["Value"].squeeze(),
                           "component_frequency": df[df["Name"] == 'component_frequency']["Value"].squeeze() +
                                                  df[df["Name"] == 'component_frequency'][
                                                      "Units"].squeeze(),
                           "frequency_increment": df[df["Name"] == 'frequency_increment']["Value"].squeeze() +
                                                  df[df["Name"] == 'frequency_increment'][
                                                      "Units"].squeeze(),
                           "sm_cellsize": df[df["Name"] == 'sm_cellsize']["Value"].squeeze() +
                                          df[df["Name"] == 'sm_cellsize'][
                                              "Units"].squeeze(),
                           "sm_size": int(df[df["Name"] == "sm_size"]["Value"].squeeze())
                           }

    return parameters_skymodel


def get_params_sources(model):
    """
    Returns extracted source parameters for each source as a list of dictionaries from the model.
    Parameter keys: "sp_flux", "sp_fluxunit", "sp_direction_ra", "sp_direction_dec", "sp_shape", "sp_frequency".

    :param model: The input model from the GUI.
    :return: parameter_sources: A set of source parameters from the model as dictionary.
    """
    df = model.fixed_params_sp
    parameters_sources = []
    for i in range(1, len(df.columns)):
        source = {"Name": df.columns[i],
                  "sp_flux": float(df[df["Parameter"] == "sp_flux"][df.columns[i]].squeeze()),
                  "sp_fluxunit": df[df["Parameter"] == "sp_fluxunit"][df.columns[i]].squeeze(),
                  "sp_direction_ra": float(df[df["Parameter"] == "sp_direction_ra"][df.columns[i]].squeeze()),
                  "sp_direction_dec": float(df[df["Parameter"] == "sp_direction_dec"][df.columns[i]].squeeze()),
                  "sp_shape": df[df["Parameter"] == "sp_shape"][df.columns[i]].squeeze(),
                  "sp_majoraxis": df[df["Parameter"] == "sp_majoraxis"][df.columns[i]].squeeze(),
                  "sp_minoraxis": df[df["Parameter"] == "sp_minoraxis"][df.columns[i]].squeeze(),
                  "sp_positionangle": df[df["Parameter"] == "sp_positionangle"][df.columns[i]].squeeze(),
                  "sp_frequency": df[df["Parameter"] == "sp_frequency"][df.columns[i]].squeeze() +
                                  df[df["Parameter"] == 'sm_frequency_unit'][df.columns[i]].squeeze(),
                  }
        parameters_sources.append(source)
    return parameters_sources


def get_params_simobserve(model):
    """
    Returns extracted simobserve parameters from the model.
    Parameter keys: "incenter", "compwidth", "incell", "inwidth", "integration", "totaltime", "mapsize", "thermalnoise",
    "t_ground", "t_sky", "leakage", "t_seed", "t_user_pwv", "tau0", "frequency_increment", "sm_cellsize", "sm_size".

    :param model: The input model from the GUI.
    :return: parameter_simobserve: A set of simobserve parameters from the model as dictionary.
    """
    df = model.fixed_params_sim
    parameters_simobserve = {"incenter": df[df["Name"] == 'incenter']["Value"].squeeze() + df[df["Name"] == 'incenter'][
        "Units"].squeeze(),
                             "compwidth": df[df["Name"] == 'compwidth']["Value"].squeeze() +
                                          df[df["Name"] == 'compwidth'][
                                              "Units"].squeeze(),
                             "incell": df[df["Name"] == 'incell']["Value"].squeeze() + df[df["Name"] == 'incell'][
                                 "Units"].squeeze(),
                             "inwidth": df[df["Name"] == 'inwidth']["Value"].squeeze() + df[df["Name"] == 'inwidth'][
                                 "Units"].squeeze(),
                             "integration": df[df["Name"] == 'integration']["Value"].squeeze() +
                                            df[df["Name"] == 'integration'][
                                                "Units"].squeeze(),
                             "totaltime": df[df["Name"] == 'totaltime']["Value"].squeeze() +
                                          df[df["Name"] == 'totaltime'][
                                              "Units"].squeeze(),
                             "mapsize": df[df["Name"] == 'mapsize']["Value"].squeeze() +
                                        df[df["Name"] == 'mapsize'][
                                            "Units"].squeeze(),
                             "thermalnoise": df[df["Name"] == 'thermalnoise']["Value"].squeeze(),
                             "t_ground": float(df[df["Name"] == 't_ground']["Value"].squeeze()),
                             "t_sky": float(df[df["Name"] == 't_sky']["Value"].squeeze()),
                             "leakage": float(df[df["Name"] == 'leakage']["Value"].squeeze()),
                             "t_seed": int(df[df["Name"] == 't_seed']["Value"].squeeze()),
                             "t_user_pwv": float(df[df["Name"] == 't_user_pwv']["Value"].squeeze()),
                             "tau0": float(df[df["Name"] == 'tau0']["Value"].squeeze())
                             }
    return parameters_simobserve


def get_params_simanalyze(model):
    """
    Returns extracted simanalyze parameters from the model.
    Parameter keys: "niter", "imsize", "weighting", "cell", "stokes", "threshold".

    :param model: The input model from the GUI.
    :return: parameter_simanalyze: A set of simanalyze parameters from the model as dictionary.
    """
    df = model.fixed_params_sim
    imsize = int(df[df["Name"] == 'analyze_imsize']["Value"].squeeze())
    parameters_simanalyze = {"analyze_niter": int(df[df["Name"] == 'analyze_niter']["Value"].squeeze()),
                             "analyze_imsize": [imsize, imsize],
                             "analyze_weighting": df[df["Name"] == 'analyze_weighting']["Value"].squeeze(),
                             "analyze_cell": df[df["Name"] == 'analyze_cell']["Value"].squeeze() +
                                             df[df["Name"] == 'analyze_cell']["Units"].squeeze(),
                             "analyze_stokes": df[df["Name"] == 'analyze_stokes']["Value"].squeeze(),
                             "analyze_threshold": df[df["Name"] == 'analyze_threshold']["Value"].squeeze() +
                                                  df[df["Name"] == 'analyze_threshold']["Units"].squeeze()}
    return parameters_simanalyze


def create_skymodel(exportfits, parameters_skymodel):
    """
    Creates a sky-model CASA image out from given parameters and exports it as FITS file using the CASA task exportfits.
    To create the CASA image, the CASA tools componentlist, coordinate system, image analysis and quanta. See
    CASA documentation for further information: https://casa.nrao.edu/casadocs

    :param exportfits: The CASA task exportfits
    :param parameters_skymodel: Parameter set extracted from the model containing sky-model parameters.
                                See get_params_skymodel for detailed content.
    """
    cl = cltool()
    ia = iatool()
    qa = qatool()

    ra = util.convert_deg_to_hour(parameters_skymodel["sm_direction_ra"])
    dec = util.convert_deg_to_dms(parameters_skymodel["sm_direction_dec"])
    direction = util.concat_ra_dec(ra, dec)
    sm_image = 'Skymodel/skymodel.im'
    sm_size = [parameters_skymodel["sm_size"], parameters_skymodel["sm_size"], 1, 1]
    sm_cellsize = parameters_skymodel["sm_cellsize"]
    sm_frq = parameters_skymodel["sm_frequency"]
    sm_frq_inc = parameters_skymodel["frequency_increment"]
    sm_fits = 'Skymodel/skymodel.fits'

    # closes any open component lists, if any.
    cl.done()
    cl.addcomponent(flux=parameters_skymodel["sm_flux"],
                    fluxunit=parameters_skymodel["sm_fluxunit"],
                    polarization=parameters_skymodel["sm_polarization"],
                    dir=direction,
                    shape=parameters_skymodel["sm_shape"],
                    majoraxis=parameters_skymodel["sm_majoraxis"],
                    minoraxis=parameters_skymodel["sm_minoraxis"],
                    positionangle=parameters_skymodel["sm_positionangle"],
                    freq=parameters_skymodel["component_frequency"],
                    spectrumtype=parameters_skymodel["sm_spectrumtype"],
                    index=parameters_skymodel["sm_index"],
                    label=parameters_skymodel["sm_label"])

    # creates a new, empty CASA image with the name and dimensions given.
    ia.fromshape(sm_image, sm_size, overwrite=True)
    # gets the coordinate system of the image.
    cs = ia.coordsys()
    # defines the units of the four axes of the new CASA image.
    cs.setunits(["rad", "rad", "", "Hz"])
    # will be the cell size and units in this CASA image.
    cell_rad = qa.convert(qa.quantity(sm_cellsize), "rad")["value"]
    # tells CASA that RA increases to the right, Dec increases going up, and, a few lines later,
    cs.setincrement([-cell_rad, cell_rad], "direction")
    # sets the center of the image in RA, Dec, and frequency.
    cs.setreferencevalue([qa.convert(ra, "rad")["value"], qa.convert(dec, "rad")["value"]], type="direction")
    cs.setreferencevalue(sm_frq, "spectral")
    # tells CASA with of the one channel.
    cs.setincrement(sm_frq_inc, "spectral")
    # puts the coordinates and frequencies into the image header.
    ia.setcoordsys(cs.torecord())
    # defines the brightness unit (Jy per pixel) of the CASA image.
    ia.setbrightnessunit("Jy/pixel")
    # puts the component into the image.
    ia.modify(cl.torecord(), subtract=False)
    exportfits(imagename=sm_image,
               fitsimage=sm_fits,
               overwrite=True)


def create_haslam_map(parameters_settings, parameters_skymodel):
    """
    Extracts data from given slice from the haslam all-sky map and replaces the data column of the sky-model FITS with
    it. If the beam size is bigger than 1 degree, interpolation with the haslam map of all pixels of the sky-model will
    be done, else only for the element in the phase center.

    :param parameters_settings: Parameter set extracted from the model containing settings parameters.
                                See get_params_settings for detailed content.
    :param parameters_skymodel: Parameter set extracted from the model containing sky-model parameters.
                                See get_params_skymodel for detailed content.
    """
    ra_rad = parameters_skymodel["sm_direction_ra"] * math.pi / 180
    dec_rad = parameters_skymodel["sm_direction_dec"] * math.pi / 180
    size = [parameters_skymodel["sm_size"], parameters_skymodel["sm_size"]]
    cellsize = parameters_skymodel["sm_cellsize"]
    sm_freq = parameters_skymodel["sm_frequency"]
    del_, cellsize_unit = util.get_decimal_from_string(cellsize)
    if cellsize_unit == "arcmin":
        del_ = del_ * 60
    elif cellsize_unit == "arcsec":
        pass
    else:
        raise ValueError(cellsize_unit + " is invalid as units for cellsize. Use arcmin or arcsec.")

    freq, freq_unit = util.get_decimal_from_string(sm_freq)
    freq = util.transform_frequency(freq, freq_unit)

    dish_diam = parameters_settings["telescope"]
    beam_size = util.calculate_beam_size(freq, dish_diam)
    ra_array = np.linspace(-1, 1, size[0]) * del_ * (1 / 3600 * np.pi / 180) + ra_rad
    dec_array = np.linspace(-1, 1, size[1]) * del_ * (1 / 3600 * np.pi / 180) + dec_rad
    # n must not be smaller than beam_size
    n = 100
    # haslam_gal is temperature, ra_dec is ra dec grid
    haslam_gal, spec_index, gal_lat, gal_lon, haslam_ra, haslam_dec = pickle.load(
        open('Skymaps/haslam_spec_gal_guzman.p', 'r'))
    # index of the array that is provided for the given direction
    idx_c = util.find_index_of_nearest_xy(haslam_ra, haslam_dec, ra_rad, dec_rad)
    tb_sky = np.zeros((size[0], size[1]))
    spec = np.zeros((size[0], size[1]))
    if beam_size > 1:
        start_time = timeit.default_timer()
        for i in range(size[0]):
            perc = float(i) / size[0] * 100
            for j in range(size[1]):
                idx = util.find_index_of_nearest_xy(haslam_ra[idx_c[0] - n:idx_c[0] + n, idx_c[1] - n:idx_c[1] + n],
                                                    haslam_dec[idx_c[0] - n:idx_c[0] + n, idx_c[1] - n:idx_c[1] + n],
                                                    ra_array[i], dec_array[j])
                tb_sky[i, j] = haslam_gal[idx_c[0] - n + idx[0], idx_c[1] - n + idx[1]]
                spec[i, j] = spec_index[idx_c[0] - n + idx[0], idx_c[1] - n + idx[1]]

            sys.stdout.write('Interpolation progress: [%d%%]\r' % perc)
            sys.stdout.flush()
        elapsed = timeit.default_timer() - start_time
        sys.stdout.write("elapsed: " + str(elapsed))
        tb_sky = np.array(tb_sky)
    else:
        # interpolation of only one element (phase center direction)
        # instead of a snippet of the haslam map?
        tb_sky = tb_sky + haslam_gal[idx_c[0], idx_c[1]]
        spec = spec + spec_index[idx_c[0], idx_c[1]]
    tb_sky = tb_sky * (freq / 0.408) ** (-spec)
    tb_sky = tb_sky.reshape(1, 1, size[0], size[1])
    # Convert Temperature in Kelvin to Flux (Jy/pixel)
    flux_sky = (tb_sky / (1.222 * 10 ** 3) * freq ** 2 * (del_ * del_)) / 1000

    # Replace data column of the sky-model fits with the haslam interpolation.
    with fits.open('Skymodel/skymodel.fits', mode='update') as skymodel_fits:
        skymodel_fits[0].data = flux_sky
        skymodel_fits.flush()


def create_sources(parameters_sources):
    """
    Creates a new component list and adds sources from given parameters using the componentlist CASA tool.

    :param parameters_sources: Parameter set extracted from the model containing source parameters.
                               See get_params_sources for detailed content.
    """
    cl = cltool()

    os.system('rm -rf Skymodel/point.cl')
    cl.done()
    for source in parameters_sources:
        ra = util.convert_deg_to_hour(source["sp_direction_ra"])
        dec = util.convert_deg_to_dms(source["sp_direction_dec"])
        direction = util.concat_ra_dec(ra, dec)
        cl.addcomponent(flux=source["sp_flux"],
                        fluxunit=source["sp_fluxunit"],
                        dir=direction,
                        shape=source["sp_shape"],
                        majoraxis=source["sp_majoraxis"],
                        minoraxis=source["sp_minoraxis"],
                        positionangle=source["sp_positionangle"],
                        freq=source["sp_frequency"],
                        label=source["Name"])
    cl.rename("Skymodel/point.cl")
    cl.done()


def run_simobserve(simobserve, parameters_settings, parameters_simobserve, folder):
    """
    Runs the CASA task simobserve with given parameters. See CASA documentation for further information:
    https://casa.nrao.edu/casadocs

    :param simobserve: The CASA task simobserve.
    :param parameters_settings: Parameter set extracted from the model containing settings parameters.
                                See get_params_settings for detailed content.
    :param parameters_simobserve: Parameter set extracted from the model containing simobserve parameters.
                                  See get_params_simobserve for detailed content.
    :param folder: The output folder name.
    """
    simobserve(project=folder,
               skymodel='Skymodel/skymodel.fits',
               inbright="",
               incell=parameters_simobserve["incell"],
               incenter=parameters_simobserve["incenter"],
               inwidth=parameters_simobserve["inwidth"],
               complist="Skymodel/point.cl",
               compwidth=parameters_simobserve["compwidth"],
               setpointings=True,
               integration=parameters_simobserve["integration"],
               mapsize=parameters_simobserve["mapsize"],
               totaltime=parameters_simobserve["totaltime"],
               antennalist=parameters_settings["antennalist"],
               thermalnoise=parameters_simobserve["thermalnoise"],
               user_pwv=parameters_simobserve["t_user_pwv"],
               t_ground=parameters_simobserve["t_ground"],
               t_sky=parameters_simobserve["t_sky"],
               tau0=parameters_simobserve["tau0"],
               seed=parameters_simobserve["t_seed"],
               leakage=parameters_simobserve["leakage"],
               graphics="file",
               overwrite=True)


def run_simanalyze(simanalyze, parameters_simanalyze, parameters_skymodel, measurement_set, folder):
    """
    Runs the CASA task simanalyze with given parameters. See CASA documentation for further information:
    https://casa.nrao.edu/casadocs

    :param simanalyze: The CASA task simanalyze.
    :param parameters_simanalyze: Parameter set extracted from the model containing simanalyze parameters.
                                  See get_params_simanalyze for detailed content.
    :param parameters_skymodel: Parameter set extracted from the model containing sky-model parameters.
                                See get_params_skymodel for detailed content.
    :param measurement_set: The measurement set to be imaged and analyzed.
    :param folder: The output folder name.
    """
    ra = util.convert_deg_to_hour(parameters_skymodel["sm_direction_ra"])
    dec = util.convert_deg_to_dms(parameters_skymodel["sm_direction_dec"])
    direction = util.concat_ra_dec(ra, dec)
    simanalyze(project=folder,
               vis=measurement_set,
               imsize=parameters_simanalyze["analyze_imsize"],
               imdirection=direction,
               cell=parameters_simanalyze["analyze_cell"],
               niter=parameters_simanalyze["analyze_niter"],
               weighting=parameters_simanalyze["analyze_weighting"],
               stokes=parameters_simanalyze["analyze_stokes"],
               threshold=parameters_simanalyze["analyze_threshold"],
               showuv=False,
               showpsf=False,
               showmodel=True,
               showconvolved=True,
               showclean=True,
               showresidual=True,
               showdifference=True,
               showfidelity=True,
               image=True,
               analyze=True,
               graphics="file",
               overwrite=True)


def create_fits_files(exportfits, imhead, folder):
    """
    Runs the CASA task exportfits to save CASA images as fits-files. Uses CASA task imhead to modify the object.
    See CASA documentation for further information:
    https://casa.nrao.edu/casadocs

    :param exportfits: The CASA task exportfits.
    :param imhead: The CASA taks imhead
    :param folder: the output folder name
    """
    os.system('mkdir ' + folder + '/FITS_Files')

    name_image = folder + '/' + folder + '.image'
    name_residual = folder + '/' + folder + '.residual'
    name_fidelity = folder + '/' + folder + '.fidelity'

    imhead(name_image, mode="put", hdkey="object", hdvalue="radio_image")
    imhead(name_residual, mode="put", hdkey="object", hdvalue="residual_image")
    imhead(name_fidelity, mode="put", hdkey="object", hdvalue="fidelity_image")

    exportfits(imagename=name_image,
               fitsimage=folder + '/FITS_Files/' + folder + '.image.fits', overwrite=True, dropdeg=True)

    exportfits(imagename=name_residual,
               fitsimage=folder + '/FITS_Files/' + folder + '.residual.fits', overwrite=True, dropdeg=True)

    exportfits(imagename=name_fidelity,
               fitsimage=folder + '/FITS_Files/' + folder + '.fidelity.fits', overwrite=True, dropdeg=True)
