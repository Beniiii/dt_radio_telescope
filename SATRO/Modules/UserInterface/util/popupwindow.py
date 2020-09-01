# coding=utf-8
import Tkinter as tk


class PopupWindows(tk.Frame):
    """
    This class creates popup windows for the view.
    """

    def __init__(self, *args, **kwargs):
        """
        This methods will be called when an object of this class is instantiated. It initializes variables.

        :param args: arguments
        :param kwargs: keyword arguments
        """

        #########################
        # Labels for Settings
        #########################
        tk.Frame.__init__(self, *args, **kwargs)
        self.label_mode = "Mode"
        self.label_mode_text = 'Single Run: Single iteration with fixed parameter values.' + "\n" + \
                               'Multiple Runs: Multiple iterations, that use fixed parameter values and ' + "\n" + \
                               'different varying parameter values that change with each iteration.'

        self.label_sky_brightness = "Sky Brightness Distribution (Sky-model)"
        self.label_sky_brightness_text = 'Custom: Customized Sky Brightness Distribution with options to change ' \
                                         'values.' + "\n" + \
                                         'Haslam: Predefined all-sky map.'

        self.label_telescope = "Telescope (when Haslam selected)"
        self.label_telescope_text = 'VLA: Telescope configuration of VLA (Very Large Array).' + "\n" + \
                                    'ALMA: Telescope configuration of ALMA (Atacama Large Millimeter Array).' + "\n" + \
                                    'MWA: Telescope configuration of MWA (Murchison Widefield Array).' + "\n" + \
                                    'Meerkat: Telescope configuration of Meerkat.'
        self.label_antennalist = "Antenna configuration"
        self.label_antennalist_text = "Choose antenna configuration in your file system for the observation. " + "\n" + \
                                      "Default value is vla.c.cfg."

        #########################
        # Labels for var params
        #########################
        self.label_var_param = "Varying Parameter"
        self.label_var_param_text = "Parameter values are going to be varied in each iteration. " + "\n" + \
                                    "Varying parameter are divided in different sets: Instrumental, Sky-model and " \
                                    "Sources."
        self.label_var_manual = "Manual"
        self.label_manual_text = "Select and set values/units of varying parameters manually."
        self.label_from_file = "From file"
        self.label_from_file_text = "Select csv with predefined varying parameter values."
        self.label_var_param_set = "Varying Parameter Set"
        self.label_var_param_set_text = "Instrumental: Telescope-based parameters (radio telescope configuration). " \
                                        + "\n" + \
                                        "Sky-model: Sky-based parameters, corresponding to Sky-model values." + "\n" + \
                                        "Sources: Sky-based parameters, additionally adding sources to Sky-model." \
                                        + "\n" + \
                                        "Instrumental & Sky-model: Combination of Instrumental and Sky-model" \
                                        "parameter sets." + "\n" + \
                                        "Instrumental & Sources: Combination of Instrumental and Sources parameter" \
                                        " sets." + "\n" + \
                                        "Sky-model & Sources: Combination of Sky-model and Sources parameter sets."
        self.label_var_param_header = "Varying Parameter Headers"
        self.label_var_param_header_text = "Name: Name of varying parameter." + "\n" + \
                                           "Min: Minimum value of varying parameter." + "\n" + \
                                           "Max: Maximum value of varying parameter." + "\n" + \
                                           "Steps: Steps between minimum and maximum value of one varying parameter." \
                                           + "\n" + \
                                           "Number of steps corresponds to number of iterations." + "\n" + \
                                           "Values: Values of varying parameter that can rather be " \
                                           "checked or unchecked." + "\n" + "\n" + \
                                           "Example: " + "\n" + \
                                           "inwidth: minimum value is 1.0, maximum value is 2.0, steps is 3 " \
                                           "and Units “GHz”. " + "\n" + \
                                           "Varying parameter values for the iterations are: 1.0GHz, 1.5GHz, 2.0GHz."

        #########################
        # Labels for fixed params
        #########################
        self.label_fixed_param = "Fixed Parameter"
        self.label_fixed_param_text = "Parameter default value, that does not change with each iteration " \
                                      "while doing" + "\n" + \
                                      "multiple runs. Except this parameter is also selected as varying" + "\n" + \
                                      "parameter then the values of the fixed parameters will not be used. " + "\n" + \
                                      "Fixed parameters are divided in three different sections: Instrumental, " \
                                      "Sky-model and Sources."
        self.label_fixed_param_file = "Choose from file"
        self.label_fixed_param_file_text = "Csv-file path: Select csv-file on your file system."
        self.label_fixed_param_source = "Number of Sources"
        self.label_fixed_param_source_text = "Select how many sources should be added to the Sky Brightness " \
                                             "Distribution."

        #########################
        # Labels for analysis
        #########################
        self.label_analysis_folder = "Select directory"
        self.label_analysis_folder_text = "Select directory created by the pipeline for analysis. The directory " + "\n" + \
                                          "must contain following data:" + "\n" + \
                                          "FITS-Files: Folder with fits-files " + "\n" + \
                                          "*.image.fits: Fits-file with ending *.image.fits " + "\n" + \
                                          "*.residual.fits: Fits-file with ending *.residual.fits " + "\n" + \
                                          "*.fidelity.fits: Fits-file with ending *.fidelity.fits " + "\n" + \
                                          "sources.pkl: Pkl-file with the sources "
        self.label_image = "Show Image Plots"
        self.label_image_text = "Shows the synthesized image with various histograms and statistical " + "\n" + \
                                "information."
        self.label_residual = "Show Residual Plots"
        self.label_residual_text = "Shows the residual image with various histograms and statistical " + "\n" + \
                                   "information."
        self.label_fidelity = "Show Fidelity Plots"
        self.label_fidelity_text = "Shows the fidelity image with various histograms and statistical " + "\n" + \
                                   "information."

        #########################
        # Labels for comparison
        #########################
        self.label_image1 = "Select fits-image"
        self.label_image1_text = "Select fits-Image of a pipeline output directory for comparison." + "\n" + \
                                 "The fits-file can be found in the folder 'FITS-Files'."
        self.label_button1 = "Show Image"
        self.label_button1_text = "Shows selected fits-image with histogram and " + "\n" + \
                                  "statistical information about the image. "
        self.label_compare = "Comparing two images"
        self.label_compare_text = "Shows the difference between the selected images. The images are required" + "\n" + \
                                  "to have the same brightness unit (unit of the pixel values)" + "\n" + \
                                  "and shape excluding empty dimensions. The tool shows residual after the " + "\n" + \
                                  "subtraction, a histogram and statistical information."

        #########################
        # Labels matplotlib
        #########################
        self.label_matplot = "Matplotlib Controls for Plots"
        self.label_matplot_text = "The plots of matplotlib have some navigation controls that the library " \
                                  "provides." + "\n" + \
                                  "Pan/Zoom: p" + "\n" + \
                                  "Save: ctrl + s" + "\n" + \
                                  "Toggle x axis scale (log/linear): L or K when mouse is over an axes." + "\n" + \
                                  "Toggle y axis scale (log/linear): I when mouse is over an axes."

    def popup_window_comparison(self):
        """
        Initializes, layouts and displays all needed widgets for the popup window "analysis".
        """
        window_comparison = tk.Toplevel()
        window_comparison.attributes('-topmost', True)
        window_comparison.title("Image Comparison")
        window_comparison.minsize(580, 415)

        #########################
        # Initialize widgets
        #########################
        grid = tk.Frame(window_comparison)
        label_image1 = tk.Label(window_comparison, text=self.label_image1,
                                font=("Helvetica", 13, "bold"), justify=tk.LEFT, anchor="w")
        label_image1_text = tk.Label(window_comparison, text=self.label_image1_text, justify=tk.LEFT,
                                     anchor="w")
        label_button1 = tk.Label(window_comparison, text=self.label_button1, font=("Helvetica", 13, "bold"),
                                 justify=tk.LEFT, anchor="w")
        label_button1_text = tk.Label(window_comparison, text=self.label_button1_text, justify=tk.LEFT,
                                      anchor="w")
        label_compare = tk.Label(window_comparison, text=self.label_compare, font=("Helvetica", 13, "bold"),
                                 justify=tk.LEFT, anchor="w")
        label_compare_text = tk.Label(window_comparison, text=self.label_compare_text, justify=tk.LEFT,
                                      anchor="w")
        label_matplotlib = tk.Label(window_comparison, text=self.label_matplot, font=("Helvetica", 13, "bold"),
                                    justify=tk.LEFT, anchor="w")
        label_matplotlib_text = tk.Label(window_comparison, text=self.label_matplot_text, justify=tk.LEFT,
                                         anchor="w")

        #########################
        # Layout widgets
        #########################
        label_image1.pack(fill='x', padx=10, pady=0, expand=True)
        label_image1_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)
        label_button1.pack(fill='x', padx=10, pady=0, expand=True)
        label_button1_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)
        label_compare.pack(fill='x', padx=10, pady=0, expand=True)
        label_compare_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)
        label_matplotlib.pack(fill='x', padx=10, pady=0, expand=True)
        label_matplotlib_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)

        #########################
        # Button for closing
        #########################
        button_close = tk.Button(grid, text="Close", command=window_comparison.destroy, height=2, width=6)
        grid.pack(side="bottom", fill="x", expand=False, anchor="s")
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(99, weight=1)
        button_close.grid(row=1, column=99, sticky="E", padx=15, pady=15)

    def popup_window_analysis(self):
        """
        Initializes, layouts and displays all needed widgets for the popup window "analysis".
        """
        window_analysis = tk.Toplevel()
        window_analysis.attributes('-topmost', True)
        window_analysis.title("Output Analysis")
        window_analysis.minsize(570, 530)

        #########################
        # Initialize widgets
        #########################
        grid = tk.Frame(window_analysis)
        label_analysis_folder = tk.Label(window_analysis, text=self.label_analysis_folder,
                                         font=("Helvetica", 13, "bold"), justify=tk.LEFT, anchor="w")
        label_analysis_folder_text = tk.Label(window_analysis, text=self.label_analysis_folder_text, justify=tk.LEFT,
                                              anchor="w")
        label_image = tk.Label(window_analysis, text=self.label_image, font=("Helvetica", 13, "bold"),
                               justify=tk.LEFT, anchor="w")
        label_image_text = tk.Label(window_analysis, text=self.label_image_text, justify=tk.LEFT,
                                    anchor="w")
        label_residual = tk.Label(window_analysis, text=self.label_residual, font=("Helvetica", 13, "bold"),
                                  justify=tk.LEFT, anchor="w")
        label_residual_text = tk.Label(window_analysis, text=self.label_residual_text, justify=tk.LEFT,
                                       anchor="w")
        label_fidelity = tk.Label(window_analysis, text=self.label_fidelity, font=("Helvetica", 13, "bold"),
                                  justify=tk.LEFT, anchor="w")
        label_fidelity_text = tk.Label(window_analysis, text=self.label_fidelity_text, justify=tk.LEFT,
                                       anchor="w")
        label_matplotlib = tk.Label(window_analysis, text=self.label_matplot, font=("Helvetica", 13, "bold"),
                                    justify=tk.LEFT, anchor="w")
        label_matplotlib_text = tk.Label(window_analysis, text=self.label_matplot_text, justify=tk.LEFT,
                                         anchor="w")

        #########################
        # Layout widgets
        #########################
        label_analysis_folder.pack(fill='x', padx=10, pady=0, expand=True)
        label_analysis_folder_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)
        label_image.pack(fill='x', padx=10, pady=0, expand=True)
        label_image_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)
        label_residual.pack(fill='x', padx=10, pady=0, expand=True)
        label_residual_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)
        label_fidelity.pack(fill='x', padx=10, pady=0, expand=True)
        label_fidelity_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)
        label_matplotlib.pack(fill='x', padx=10, pady=0, expand=True)
        label_matplotlib_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)

        #########################
        # Button for closing
        #########################
        button_close = tk.Button(grid, text="Close", command=window_analysis.destroy, height=2, width=6)
        grid.pack(side="bottom", fill="x", expand=False, anchor="s")
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(99, weight=1)
        button_close.grid(row=1, column=99, sticky="E", padx=15, pady=15)

    def popup_window_settings(self):
        """
        Initializes, layouts and displays all needed widgets for the popup window "settings".
        """
        window_settings = tk.Toplevel()
        window_settings.title("Settings")
        window_settings.minsize(600, 400)

        #########################
        # Initialize widgets
        #########################
        grid = tk.Frame(window_settings)
        label_mode = tk.Label(window_settings, text=self.label_mode, font=("Helvetica", 13, "bold"), justify=tk.LEFT,
                              anchor="w")
        label_mode_text = tk.Label(window_settings, text=self.label_mode_text, justify=tk.LEFT, anchor="w")
        label_sky_brightness = tk.Label(window_settings, text=self.label_sky_brightness, font=("Helvetica", 13, "bold"),
                                        justify=tk.LEFT, anchor="w")
        label_sky_brightness_text = tk.Label(window_settings, text=self.label_sky_brightness_text, justify=tk.LEFT,
                                             anchor="w")
        label_telescope = tk.Label(window_settings, text=self.label_telescope, font=("Helvetica", 13, "bold"),
                                   justify=tk.LEFT, anchor="w")
        label_telescope_text = tk.Label(window_settings, text=self.label_telescope_text, justify=tk.LEFT, anchor="w")
        label_antennalist = tk.Label(window_settings, text=self.label_antennalist, font=("Helvetica", 13, "bold"),
                                     justify=tk.LEFT, anchor="w")
        label_antennalist_text = tk.Label(window_settings, text=self.label_antennalist_text, justify=tk.LEFT,
                                          anchor="w")

        #########################
        # Layout widgets
        #########################
        label_mode.pack(side="top", fill='x', padx=10, pady=0, expand=True)
        label_mode_text.pack(side="top", fill='x', padx=50, pady=(0, 10), expand=True)
        label_sky_brightness.pack(side="top", fill='x', padx=10, pady=0, expand=True)
        label_sky_brightness_text.pack(side="top", fill='x', padx=50, pady=(0, 10), expand=True)
        label_telescope.pack(side="top", fill='x', padx=10, pady=5, expand=True)
        label_telescope_text.pack(side="top", fill='x', padx=50, pady=(0, 10), expand=True)
        label_antennalist.pack(side="top", fill='x', padx=10, pady=0, expand=True)
        label_antennalist_text.pack(side="top", fill='x', padx=50, pady=(0, 10), expand=True)

        #########################
        # Button for closing
        #########################
        button_close = tk.Button(grid, text="Close", command=window_settings.destroy, height=2, width=6)
        grid.pack(side="bottom", fill="x", expand=False, anchor="s")
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(99, weight=1)
        button_close.grid(row=1, column=99, sticky="E", padx=15, pady=15)

    def popup_window_var_param(self):
        """
        Initializes, layouts and displays all needed widgets for the popup window "varying parameter configuration".
        """
        window_var_param = tk.Toplevel()
        window_var_param.title("Varying Parameter Configurations")
        window_var_param.minsize(630, 560)

        #########################
        # Initialize widgets
        #########################
        grid = tk.Frame(window_var_param)
        label_var_param = tk.Label(window_var_param, text=self.label_var_param, font=("Helvetica", 13, "bold"),
                                   justify=tk.LEFT, anchor="w")
        label_var_param_text = tk.Label(window_var_param, text=self.label_var_param_text, justify=tk.LEFT, anchor="w")
        label_var_manual = tk.Label(window_var_param, text=self.label_var_manual, font=("Helvetica", 13, "bold"),
                                    justify=tk.LEFT, anchor="w")
        label_manual_text = tk.Label(window_var_param, text=self.label_manual_text, justify=tk.LEFT, anchor="w")
        label_from_file = tk.Label(window_var_param, text=self.label_from_file, font=("Helvetica", 13, "bold"),
                                   justify=tk.LEFT, anchor="w")
        label_from_file_text = tk.Label(window_var_param, text=self.label_from_file_text, justify=tk.LEFT, anchor="w")
        label_var_param_set = tk.Label(window_var_param, text=self.label_var_param_set, font=("Helvetica", 13, "bold"),
                                       justify=tk.LEFT, anchor="w")
        label_var_param_set_text = tk.Label(window_var_param, text=self.label_var_param_set_text, justify=tk.LEFT,
                                            anchor="w")
        label_var_param_header = tk.Label(window_var_param, text=self.label_var_param_header,
                                          font=("Helvetica", 13, "bold"), justify=tk.LEFT, anchor="w")
        label_var_param_header_text = tk.Label(window_var_param, text=self.label_var_param_header_text, justify=tk.LEFT,
                                               anchor="w")

        #########################
        # Layout widgets
        #########################
        label_var_param.pack(fill='x', padx=10, pady=0, expand=True)
        label_var_param_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)
        label_var_manual.pack(fill='x', padx=10, pady=0, expand=True)
        label_manual_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)
        label_from_file.pack(fill='x', padx=10, pady=0, expand=True)
        label_from_file_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)
        label_var_param_set.pack(fill='x', padx=10, pady=0, expand=True)
        label_var_param_set_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)
        label_var_param_header.pack(fill='x', padx=10, pady=0, expand=True)
        label_var_param_header_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)

        #########################
        # Button for closing
        #########################
        button_close = tk.Button(grid, text="Close", command=window_var_param.destroy, height=2, width=6)
        grid.pack(side="bottom", fill="x", expand=False, anchor="s")
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(99, weight=1)
        button_close.grid(row=1, column=99, sticky="E", padx=15, pady=15)

    def popup_window_fixed_param(self):
        """
        Initializes, layouts and displays all needed widgets for the popup window "fixed parameter configuration
        (Instrumental and sky-model)".
        """
        window_fixed_param = tk.Toplevel()
        window_fixed_param.title("Fixed Parameter Configurations")
        window_fixed_param.minsize(660, 210)

        #########################
        # Initialize widgets
        #########################
        grid = tk.Frame(window_fixed_param)
        label_fixed_param = tk.Label(window_fixed_param, text=self.label_fixed_param, font=("Helvetica", 13, "bold"),
                                     justify=tk.LEFT, anchor="w")
        label_fixed_param_text = tk.Label(window_fixed_param, text=self.label_fixed_param_text, justify=tk.LEFT,
                                          anchor="w")
        label_fixed_param_file = tk.Label(window_fixed_param, text=self.label_fixed_param_file,
                                          font=("Helvetica", 13, "bold"), justify=tk.LEFT, anchor="w")
        label_fixed_param_file_text = tk.Label(window_fixed_param, text=self.label_fixed_param_file_text,
                                               justify=tk.LEFT,
                                               anchor="w")

        #########################
        # Layout widgets
        #########################
        label_fixed_param.pack(fill='x', padx=10, pady=0, expand=True)
        label_fixed_param_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)
        label_fixed_param_file.pack(fill='x', padx=10, pady=0, expand=True)
        label_fixed_param_file_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)

        #########################
        # Button for closing
        #########################
        button_close = tk.Button(grid, text="Close", command=window_fixed_param.destroy, height=2, width=6)
        grid.pack(side="bottom", fill="x", expand=False, anchor="s")
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(99, weight=1)
        button_close.grid(row=1, column=99, sticky="E", padx=15, pady=15)

    def popup_window_fixed_param_sources(self):
        """
        Initializes, layouts and displays all needed widgets for the popup window "fixed parameter configuration
        (Sources)".
        """
        window_fixed_param_sources = tk.Toplevel()
        window_fixed_param_sources.title("Fixed Parameter Configurations")
        window_fixed_param_sources.minsize(660, 210)

        #########################
        # Initialize widgets
        #########################
        grid = tk.Frame(window_fixed_param_sources)
        label_fixed_param = tk.Label(window_fixed_param_sources, text=self.label_fixed_param,
                                     font=("Helvetica", 13, "bold"),
                                     justify=tk.LEFT, anchor="w")
        label_fixed_param_text = tk.Label(window_fixed_param_sources, text=self.label_fixed_param_text, justify=tk.LEFT,
                                          anchor="w")
        label_fixed_param_source = tk.Label(window_fixed_param_sources, text=self.label_fixed_param_source,
                                            font=("Helvetica", 13, "bold"), justify=tk.LEFT, anchor="w")
        label_fixed_param_source_text = tk.Label(window_fixed_param_sources, text=self.label_fixed_param_source_text,
                                                 justify=tk.LEFT, anchor="w")

        #########################
        # Layout widgets
        #########################
        label_fixed_param.pack(fill='x', padx=10, pady=0, expand=True)
        label_fixed_param_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)
        label_fixed_param_source.pack(fill='x', padx=10, pady=0, expand=True)
        label_fixed_param_source_text.pack(fill='x', padx=50, pady=(0, 10), expand=True)

        #########################
        # Button for closing
        #########################
        button_close = tk.Button(grid, text="Close", command=window_fixed_param_sources.destroy, height=2, width=6)
        grid.pack(side="bottom", fill="x", expand=False, anchor="s")
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(99, weight=1)
        button_close.grid(row=1, column=99, sticky="E", padx=15, pady=15)
