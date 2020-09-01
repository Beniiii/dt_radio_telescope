import pandas as pd
import numpy as np
import UserInterface.util.helpers as helpers
from Pipeline.util import get_decimal_from_string
from Pipeline.util import transform_frequency
from Pipeline.util import calculate_beam_size


class InputModel:
    """
    This class initializes all needed data in variables, lists and dataframes for passing it to the AppPipeline
    for radio observation.
    """

    def __init__(self, simobserve, simanalyze, imhead, exportfits):
        """
        This method will be called when an object of this class is instantiated. It initializes variables and calls
        methods.
        :param simobserve: The CASA task simobserve.
        :param simanalyze: The CASA task simanalyze.
        :param imhead: The CASA task imhead.
        :param exportfits: The CASA task exportfits
        """
        self.simobserve = simobserve
        self.simanalyze = simanalyze
        self.imhead = imhead
        self.exportfits = exportfits
        self.mode = ""
        self.sm = ""
        self.telescope = ""
        self.antennalist = "vla.c.cfg"
        self.sm_selected_shapes = []
        self.sp_selected_shapes = []
        self.selected_weightings = []
        self.var_params_values_num = pd.DataFrame(columns=["Name", "Min", "Max", "Steps", "Units"])
        self.var_param_values_lists = {}
        self.checkboxes_params_variables = []
        self.sm_shape_variables = []
        self.sp_shape_variables = []
        self.weighting_variables = []
        self.var_param_set = ""
        self.number_of_sources = 0
        self.estimation = ""
        self.prefix = "Parameterfiles/"
        self.fixed_params_sim = helpers.read_fixed_params_from_file(self.prefix + "fixed_sim_parameters.csv",
                                                                    ["Name", "Value", "Units"])
        self.fixed_params_sm = helpers.read_fixed_params_from_file(self.prefix + "fixed_sm_parameters.csv",
                                                                   ["Name", "Value", "Units"])
        self.default_params_sp = helpers.read_fixed_params_from_file(self.prefix + "fixed_sp_parameters.csv",
                                                                     ["sp_flux", "sp_fluxunit", "sp_direction_ra",
                                                                    "sp_direction_dec", "sp_shape", "sp_majoraxis",
                                                                    "sp_minoraxis", "sp_positionangle", "sp_frequency",
                                                                    "sp_frequency_unit"])
        self.fixed_params_sp = []
        self.output_path = ""

        self.mode_options = ["Single Run", "Multiple Runs"]
        self.sm_options = ['Custom', 'Haslam-Map']
        self.telescope_options = ['VLA', 'ALMA', 'MWA', 'Meerkat']
        self.telescope_diameters = {'VLA': 25.0,
                                    'ALMA': 12.0,
                                    'MWA': 4.0,
                                    'Meerkat': 12.0
                                    }
        self.csv_selector = {
            'Instrumental': [self.prefix + 'var_sim_parameters.csv'],
            'Sky-model': [self.prefix + 'var_sm_parameters.csv'],
            'Sources': [self.prefix + 'var_sp_parameters.csv'],
            'Instrumental & Sky-model': [self.prefix + 'var_sim_parameters.csv', self.prefix + 'var_sm_parameters.csv'],
            'Instrumental & Sources': [self.prefix + 'var_sim_parameters.csv', self.prefix + 'var_sp_parameters.csv'],
            'Sky-model & Sources': [self.prefix + 'var_sm_parameters.csv', self.prefix + 'var_sp_parameters.csv']
        }
        self.var_param_set_options = ['Instrumental',
                                      'Sky-model',
                                      'Sources',
                                      'Instrumental & Sky-model',
                                      'Instrumental & Sources',
                                      'Sky-model & Sources']
        self.var_params_num = ["inwidth", "integration", "totaltime", "t_ground", "t_seed", "t_user_pwv", "t_sky",
                               "tau0", "leakage", "analyze_niter", "sm_flux", "sm_direction_ra", "sm_direction_dec",
                               "sm_majoraxis", "sm_minoraxis", "sm_positionangle", "sm_frequency", "sp_flux",
                               "sp_direction_ra", "sp_direction_dec", "sp_majoraxis", "sp_minoraxis",
                               "sp_positionangle", "sp_frequency", "nsp"]
        self.var_params_str = ["analyze_weighting", "sm_shape", "sp_shape"]
        self.shapes = ["Gaussian", "point", "disk", "limbdarkeneddisk"]
        self.weightings = ["natural", "uniform", "briggs"]

    def get_number_of_iterations(self):
        """
        Returns the number of iterations of multiple runs out of number of steps and selected checkboxes

        :return: iterations: The number of total iterations as integer
        """
        if self.mode == "Multiple Runs":
            if not self.var_params_values_num.empty:
                self.var_params_values_num["Steps"] = self.var_params_values_num["Steps"].astype(int)
                iterations = self.var_params_values_num["Steps"].sum()
                iterations += len(self.selected_weightings) + len(self.sm_selected_shapes) + \
                              len(self.sp_selected_shapes)
                return int(iterations)
            else:
                iterations = 0
                iterations += len(self.selected_weightings) + len(self.sm_selected_shapes) + \
                              len(self.sp_selected_shapes)
                return int(iterations)
        else:
            iterations = 1
            return iterations

    def calculate_estimated_time_total(self):
        """
        Returns the calculated total estimation computation time in seconds. Parameters that influence the estimated
        time are "totaltime", "integration", "imsize" and "sm_size" as well as the selection of the sky brightness
        distribution. Additionally if the beam size is greater than 1 radian, computation time for interpolating with
        the haslam map is taken into account.

        :return: total_estimation: The total estimated time in seconds as float
        """
        totaltime = float(self.fixed_params_sim[self.fixed_params_sim["Name"] == 'totaltime']["Value"].squeeze())
        integration = float(self.fixed_params_sim[self.fixed_params_sim["Name"] == 'integration']["Value"].squeeze())

        imsize = int(self.fixed_params_sim[self.fixed_params_sim["Name"] == 'analyze_imsize']["Value"].squeeze())
        sm_size = int(self.fixed_params_sm[self.fixed_params_sm["Name"] == 'sm_size']["Value"].squeeze())

        sm_freq = float(self.fixed_params_sm[self.fixed_params_sm["Name"] == 'sm_frequency']["Value"].squeeze())
        freq_unit = self.fixed_params_sm[self.fixed_params_sm["Name"] == 'sm_frequency']["Units"].squeeze()
        sm_freq = transform_frequency(sm_freq, freq_unit)
        dish_diam = self.telescope_diameters[self.telescope]
        beam_size = calculate_beam_size(sm_freq, dish_diam)

        if self.sm == "Haslam-Map":
            haslam = True
        else:
            haslam = False

        estimations = []
        if self.mode == "Multiple Runs":
            index_totaltime = 0
            index_integration = 0
            index_sm_freq = 0
            for i in range(self.get_number_of_iterations()):
                totaltime_var = totaltime
                integration_var = integration
                sm_freq_var = sm_freq
                if "totaltime" in self.var_param_values_lists.keys():
                    if i < len(self.var_param_values_lists["totaltime"]):
                        totaltime_var, _ = get_decimal_from_string(self.var_param_values_lists["totaltime"]
                                                                   [index_totaltime])
                        index_totaltime = index_totaltime + 1
                if "integration" in self.var_param_values_lists.keys():
                    if i < len(self.var_param_values_lists["integration"]):
                        integration_var, _ = get_decimal_from_string(self.var_param_values_lists["integration"]
                                                                     [index_integration])
                        index_integration = index_integration + 1
                if "sm_frequency" in self.var_param_values_lists.keys():
                    if i < len(self.var_param_values_lists["sm_frequency"]):
                        sm_freq_var, sm_freq_var_units = get_decimal_from_string(self.var_param_values_lists
                                                                                 ["sm_frequency"][index_sm_freq])
                        sm_freq_var = transform_frequency(sm_freq_var, sm_freq_var_units)
                        index_sm_freq = index_sm_freq + 1
                integrations_var = totaltime_var / integration_var
                beam_size = calculate_beam_size(sm_freq_var, dish_diam)
                estimation = helpers.calulate_estimated_time(integrations_var, imsize, sm_size, haslam, beam_size)
                estimations.append(estimation)
        elif self.mode == "Single Run":
            integrations = totaltime / integration
            estimation = helpers.calulate_estimated_time(integrations, imsize, sm_size, haslam, beam_size)
            estimations.append(estimation)

        total_estimation = np.array(estimations).sum()
        return total_estimation

    def get_var_param_values(self):
        """
        Returns a dictionary with the varying parameter names as keys and a list of their values.
        Updates alphabetic varying parameter dataframe.

        :return: var_param_values_lists: The varying parameters and their lists of values as dictionary.
        """
        df = self.var_params_values_num
        var_param_values_lists = {}
        for param in df["Name"]:
            min_value = helpers.transform_to_number(df[df["Name"] == param]["Min"].squeeze())
            max_value = helpers.transform_to_number(df[df["Name"] == param]["Max"].squeeze())
            steps = int(df[df["Name"] == param]["Steps"].squeeze())
            units = df[df["Name"] == param]["Units"].squeeze()
            values = helpers.create_param_values_list(min_value, max_value, steps, units)
            var_param_values_lists.update({param: values})

        if len(self.sm_selected_shapes) > 0:
            var_param_values_lists.update({"sm_shape": self.sm_selected_shapes})
        if len(self.sp_selected_shapes) > 0:
            var_param_values_lists.update({"sp_shape": self.sp_selected_shapes})
        if len(self.selected_weightings) > 0:
            var_param_values_lists.update({"analyze_weighting": self.selected_weightings})

        return var_param_values_lists
