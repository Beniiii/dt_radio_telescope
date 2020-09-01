import Tkinter as tk
import os
import tkFileDialog
import tkMessageBox
import ttk
import csv

from util.popupwindow import PopupWindows
import util.helpers as helpers


class ConfigurationPage(tk.Frame):
    """
    Subclass of tk.Frame. This class creates and layouts widgets for the first page of the GUI. This class allows to
    configure basic settings and parameter values for radio observations.
    """

    def __init__(self, model, *args, **kwargs):
        """
        This method will be called when an object of this class is instantiated. It initializes variables and calls
        methods.

        :param model: the input model
        :param args: arguments
        :param kwargs: keyword arguments
        """
        tk.Frame.__init__(self, *args, **kwargs)
        #########################
        # initialize variables
        #########################
        self.model = model
        self.checkboxes_params = []
        self.checkboxes_params_variables = []
        self.selected_params_num = []
        self.selected_params_str = []
        self.var_param_entries_num = {}
        self.sm_shape_checkboxes = []
        self.sm_shape_variables = []
        self.sm_selected_shapes = []
        self.sp_shape_checkboxes = []
        self.sp_shape_variables = []
        self.sp_selected_shapes = []
        self.weighting_checkboxes = []
        self.weighting_variables = []
        self.selected_weightings = []
        self.sp_entries = []
        self.valid_selected = False
        self.valid_num = False
        self.valid_str = False

        self.mode = tk.StringVar(self)
        self.mode.set(self.model.mode_options[0])
        self.sm = tk.StringVar(self)
        self.sm.set(self.model.sm_options[0])
        self.telescope = tk.StringVar(self)
        self.telescope.set(self.model.telescope_options[0])
        self.var_param_set = tk.StringVar(self)
        self.var_param_set.set(self.model.var_param_set_options[0])
        self.number_of_sources = tk.IntVar(self)
        self.number_of_sources.set(1)

        self.var_radio = tk.IntVar()
        self.var_radio.set(1)

        self.popup = PopupWindows()

        #########################
        # call functions
        #########################
        self.initialize_widgets()
        self.layout_widgets()
        self.create_var_param_str_checkboxes()
        self.get_var_param_options(self.var_param_set.get())
        helpers.create_entry_table(self.model.fixed_params_sim, self.table_fixed_params_sim)
        helpers.create_entry_table(self.model.fixed_params_sm, self.table_fixed_params_sm)
        self.create_entry_table_sources(self.number_of_sources.get())

    def initialize_widgets(self):
        """Initializes all needed widgets for the page."""
        self.label_title = tk.Label(self, text="Parameter Configuration", font=("Arial", 20, 'bold'), fg="white",
                                    bg="#7695e3", )

        self.grid_top = tk.LabelFrame(self, text="Settings", font=("Arial", 16, 'bold'))
        self.grid_middle = tk.LabelFrame(self, text="Varying Parameter Configuration", font=("Arial", 16, 'bold'))
        self.grid_bottom = tk.LabelFrame(self, text="Fixed Parameter Configuration", font=("Arial", 16, 'bold'))

        #########################
        # Widgets for top grid
        #########################
        self.label_mode = tk.Label(self.grid_top, text='Mode')
        self.dropdown_mode = tk.OptionMenu(self.grid_top, self.mode, *self.model.mode_options, command=self.set_mode)
        self.label_sm = tk.Label(self.grid_top, text='Sky Brightness Distribution')
        self.dropdown_sm = tk.OptionMenu(self.grid_top, self.sm, *self.model.sm_options, command=self.set_skymodel)

        self.button_popup_help_settings = tk.Button(self.grid_top, text="?", command=self.popup.popup_window_settings,
                                                    width=4)

        self.label_telescope = tk.Label(self.grid_top, text='Telescope: ')
        self.dropdown_telescope = tk.OptionMenu(self.grid_top, self.telescope, *self.model.telescope_options,
                                                command=self.set_telescope)

        self.label_browse_antenna = tk.Label(self.grid_top, text="Choose antenna list")
        self.entry_browse_antenna = tk.Entry(self.grid_top, state="normal")
        self.entry_browse_antenna.insert(0, self.model.antennalist)
        self.button_browse_antenna = tk.Button(self.grid_top, text="Browse...", command=self.browse_antenna_file,
                                               state="normal")

        #########################
        # Widgets for middle grid
        #########################
        self.grid_var_params_radio = tk.Frame(self.grid_middle)
        self.radio_manual = tk.Radiobutton(self.grid_var_params_radio, text="Manual", variable=self.var_radio, value=1,
                                           command=self.toggle_browsing)
        self.radio_file = tk.Radiobutton(self.grid_var_params_radio, text="From file", variable=self.var_radio, value=2,
                                         command=self.toggle_browsing)

        self.button_popup_help_var_params = tk.Button(self.grid_var_params_radio, text="?",
                                                      command=self.popup.popup_window_var_param, width=4)

        self.label_browse = tk.Label(self.grid_var_params_radio, text="Csv-file path")
        self.entry_browse = tk.Entry(self.grid_var_params_radio, state="disabled")
        self.button_browse = tk.Button(self.grid_var_params_radio, text="Browse...", command=self.browse_file,
                                       state="disabled")

        self.grid_var_param_settings = tk.Frame(self.grid_middle)
        self.label_var_param_set = tk.Label(self.grid_var_param_settings, text="Varying Parameter Set")
        self.dropdown_var_param_set = tk.OptionMenu(self.grid_var_param_settings, self.var_param_set,
                                                    *self.model.var_param_set_options,
                                                    command=self.get_var_param_options)

        self.grid_var_param_checkboxes = tk.Frame(self.grid_middle)

        self.table_var_params_num = tk.Frame(self.grid_middle)
        self.label_name_num = tk.Label(self.table_var_params_num, text="Name", borderwidth=1, relief="solid")
        self.label_min_num = tk.Label(self.table_var_params_num, text="Min", borderwidth=1, relief="solid")
        self.label_max_num = tk.Label(self.table_var_params_num, text="Max", borderwidth=1, relief="solid")
        self.label_steps_num = tk.Label(self.table_var_params_num, text="Steps", borderwidth=1, relief="solid")
        self.label_units_num = tk.Label(self.table_var_params_num, text="Units", borderwidth=1, relief="solid")

        self.grid_var_params_str = tk.Frame(self.grid_middle)
        self.label_name_str = tk.Label(self.grid_var_params_str, text="Name", borderwidth=1, relief="solid")
        self.label_values_str = tk.Label(self.grid_var_params_str, text="Values", borderwidth=1, relief="solid")

        #########################
        # Widgets for bottom grid
        #########################
        self.note = ttk.Notebook(self.grid_bottom)
        self.tab1 = tk.Frame(self.note)
        self.tab2 = tk.Frame(self.note)
        self.tab3 = tk.Frame(self.note)
        self.note.add(self.tab1, text="Instrumental")
        self.note.add(self.tab2, text="Sky-model")
        self.note.add(self.tab3, text="Sources")

        # Widgets for grid_fixed_sim
        self.grid_browse_fixed_sim = tk.Frame(self.tab1)
        self.button_popup_help_fixed_params_tab1 = tk.Button(self.grid_browse_fixed_sim, text="?",
                                                             command=self.popup.popup_window_fixed_param, width=4)
        self.label_browse_fixed_sim = tk.Label(self.grid_browse_fixed_sim,
                                               text="Choose from file")
        self.entry_browse_fixed_sim = tk.Entry(self.grid_browse_fixed_sim, state="normal")
        self.button_browse_fixed_sim = tk.Button(self.grid_browse_fixed_sim, text="Browse...",
                                                 command=self.load_fixed_params_sim, state="normal")
        self.table_fixed_params_sim = tk.Frame(self.tab1)

        # Widgets for grid_fixed_sm
        self.grid_browse_fixed_sm = tk.Frame(self.tab2)
        self.button_popup_help_fixed_params_tab2 = tk.Button(self.grid_browse_fixed_sm, text="?",
                                                             command=self.popup.popup_window_fixed_param, width=4)
        self.label_browse_fixed_sm = tk.Label(self.grid_browse_fixed_sm,
                                              text="Choose from file")
        self.entry_browse_fixed_sm = tk.Entry(self.grid_browse_fixed_sm, state="normal")
        self.button_browse_fixed_sm = tk.Button(self.grid_browse_fixed_sm, text="Browse...",
                                                command=self.load_fixed_params_sm, state="normal")
        self.table_fixed_params_sm = tk.Frame(self.tab2)

        # Widgets for grid_fixed_sp
        self.grid_nsp = tk.Frame(self.tab3)
        self.button_popup_help_fixed_params_tab3 = tk.Button(self.grid_nsp, text="?",
                                                             command=self.popup.popup_window_fixed_param_sources,
                                                             width=4)
        self.label_nsp = tk.Label(self.grid_nsp, text="Number Of Sources")
        self.dropdown_nsp = tk.OptionMenu(self.grid_nsp, self.number_of_sources,
                                          *[1, 2, 3, 4, 5],
                                          command=self.create_entry_table_sources)

        self.table_sources = tk.Frame(self.tab3)
        self.label_sp_name = tk.Label(self.table_sources, text="Parameter", borderwidth=1, relief="solid")
        self.label_sp_flux = tk.Label(self.table_sources, text="sp_flux")
        self.label_sp_fluxunit = tk.Label(self.table_sources, text="sp_fluxunit")
        self.label_sp_direction_ra = tk.Label(self.table_sources, text="sp_direction_ra")
        self.label_sp_direction_dec = tk.Label(self.table_sources, text="sp_direction_dec")
        self.label_sp_shape = tk.Label(self.table_sources, text="sp_shape")
        self.label_sp_majoraxis = tk.Label(self.table_sources, text="sp_majoraxis")
        self.label_sp_minoraxis = tk.Label(self.table_sources, text="sp_minoraxis")
        self.label_sp_positionangle = tk.Label(self.table_sources, text="sp_positionangle")
        self.label_sp_frequency = tk.Label(self.table_sources, text="sp_frequency")
        self.label_sp_frequency_unit = tk.Label(self.table_sources, text="sp_frequency_unit")

    def layout_widgets(self):
        """Displays and layouts the widgets in the correct places"""
        self.label_title.pack(side="top", fill="x", expand=True, anchor="n")

        #########################
        # Top grid layout
        #########################
        self.grid_top.grid_columnconfigure(0, weight=1)
        self.grid_top.grid_columnconfigure(3, weight=1)
        self.grid_top.grid_columnconfigure(99, weight=1)

        self.label_mode.grid(row=1, column=1, sticky='w', pady=(10, 0))
        self.dropdown_mode.grid(row=1, column=2, sticky='e', pady=(10, 0))
        self.label_sm.grid(row=1, column=4, sticky='w', columnspan=1, pady=(10, 0))
        self.dropdown_sm.grid(row=1, column=5, columnspan=3, sticky='e', pady=(10, 0))

        self.button_popup_help_settings.grid(row=1, column=99, columnspan=2, sticky='e', padx=(10, 10), pady=(10, 0))

        self.label_browse_antenna.grid(row=3, column=1, sticky='w', pady=(0, 10))
        self.entry_browse_antenna.grid(row=3, column=2, sticky='w', pady=(0, 10))
        self.button_browse_antenna.grid(row=3, column=3, sticky='w', pady=(0, 10))

        #########################
        # Middle grid layout
        #########################
        self.grid_middle.grid_columnconfigure(0, weight=1)
        self.grid_middle.grid_columnconfigure(99, weight=1)

        self.grid_var_params_radio.grid_columnconfigure(0, weight=1)
        self.grid_var_params_radio.grid_columnconfigure(99, weight=1)
        self.radio_manual.grid(row=1, column=1, pady=(10, 0))
        self.radio_file.grid(row=1, column=2, pady=(10, 0))
        self.button_popup_help_var_params.grid(row=1, column=99, columnspan=2, sticky='e', padx=(10, 10), pady=(10, 0))
        self.label_browse.grid(row=2, column=1)
        self.entry_browse.grid(row=2, column=2)
        self.button_browse.grid(row=2, column=3)
        self.grid_var_params_radio.pack(side="top", fill="x", expand=True, anchor="n", pady=(0, 10))

        self.grid_var_param_settings.grid_columnconfigure(0, weight=1)
        self.grid_var_param_settings.grid_columnconfigure(99, weight=1)
        self.label_var_param_set.grid(row=1, column=1)
        self.dropdown_var_param_set.grid(row=1, column=2)
        self.grid_var_param_settings.pack(side="top", fill="x", expand=True, anchor="n", pady=(0, 10))

        self.grid_var_param_checkboxes.grid_columnconfigure(0, weight=1)
        self.grid_var_param_checkboxes.grid_columnconfigure(99, weight=1)
        self.grid_var_param_checkboxes.pack(side="top", fill="x", expand=True, anchor="n", pady=(0, 10))

        self.table_var_params_num.grid_columnconfigure(0, weight=1)
        self.table_var_params_num.grid_columnconfigure(1, weight=1)
        self.table_var_params_num.grid_columnconfigure(2, weight=1)
        self.table_var_params_num.grid_columnconfigure(3, weight=1)
        self.table_var_params_num.grid_columnconfigure(4, weight=1)
        self.table_var_params_num.grid_columnconfigure(5, weight=1)
        self.table_var_params_num.grid_columnconfigure(6, weight=1)
        self.table_var_params_num.pack(side="top", fill="x", expand=True, anchor="n", pady=(0, 10))

        self.grid_var_params_str.grid_columnconfigure(0, weight=1)
        self.grid_var_params_str.grid_columnconfigure(99, weight=1)
        self.grid_var_params_str.pack(side="top", fill="x", expand=True, anchor="n", pady=(0, 10))

        #########################
        # Bottom grid layout
        #########################
        self.grid_bottom.grid_columnconfigure(0, weight=1)
        self.grid_bottom.grid_columnconfigure(99, weight=1)

        self.button_popup_help_fixed_params_tab1.grid(row=1, column=99, columnspan=2, sticky='e', padx=(10, 10),
                                                      pady=(0, 10))
        self.button_popup_help_fixed_params_tab2.grid(row=1, column=99, columnspan=2, sticky='e', padx=(10, 10),
                                                      pady=(0, 10))
        self.button_popup_help_fixed_params_tab3.grid(row=1, column=99, columnspan=2, sticky='e', padx=(10, 10),
                                                      pady=(0, 10))

        self.label_browse_fixed_sim.grid(row=1, column=1, pady=(0, 10))
        self.entry_browse_fixed_sim.grid(row=1, column=2, pady=(0, 10))
        self.button_browse_fixed_sim.grid(row=1, column=3, pady=(0, 10))
        self.grid_browse_fixed_sim.grid_columnconfigure(0, weight=1)
        self.grid_browse_fixed_sim.grid_columnconfigure(99, weight=1)
        self.grid_browse_fixed_sim.pack(side="top", fill="x", expand=True, anchor="n", pady=(10, 0))
        self.table_fixed_params_sim.grid_columnconfigure(0, weight=1)
        self.table_fixed_params_sim.grid_columnconfigure(4, weight=1)
        self.table_fixed_params_sim.pack(side="top", fill="x", expand=True, anchor="n")

        self.label_browse_fixed_sm.grid(row=1, column=1, pady=(0, 10))
        self.entry_browse_fixed_sm.grid(row=1, column=2, pady=(0, 10))
        self.button_browse_fixed_sm.grid(row=1, column=3, pady=(0, 10))
        self.grid_browse_fixed_sm.grid_columnconfigure(0, weight=1)
        self.grid_browse_fixed_sm.grid_columnconfigure(99, weight=1)
        self.grid_browse_fixed_sm.pack(side="top", fill="x", expand=True, anchor="n", pady=(10, 0))
        self.table_fixed_params_sm.grid_columnconfigure(0, weight=1)
        self.table_fixed_params_sm.grid_columnconfigure(4, weight=1)
        self.table_fixed_params_sm.pack(side="top", fill="x", expand=True, anchor="n")

        self.grid_nsp.grid_columnconfigure(0, weight=1)
        self.grid_nsp.grid_columnconfigure(99, weight=1)
        self.label_nsp.grid(row=1, column=1, pady=(0, 10))
        self.dropdown_nsp.grid(row=1, column=2, pady=(0, 10))
        self.grid_nsp.pack(side="top", fill="x", expand=True, anchor="n", pady=(10, 0))

        self.table_sources.grid_columnconfigure(0, weight=1)
        self.table_sources.grid_columnconfigure(3, weight=1)
        self.label_sp_name.grid(row=0, column=1, sticky='nesw')
        self.label_sp_flux.grid(row=1, column=1, sticky='nesw')
        self.label_sp_fluxunit.grid(row=2, column=1, sticky='nesw')
        self.label_sp_direction_ra.grid(row=3, column=1, sticky='nesw')
        self.label_sp_direction_dec.grid(row=4, column=1, sticky='nesw')
        self.label_sp_shape.grid(row=5, column=1, sticky='nesw')
        self.label_sp_majoraxis.grid(row=6, column=1, sticky='nesw')
        self.label_sp_minoraxis.grid(row=7, column=1, sticky='nesw')
        self.label_sp_positionangle.grid(row=8, column=1, sticky='nesw')
        self.label_sp_frequency.grid(row=9, column=1, sticky='nesw')
        self.label_sp_frequency_unit.grid(row=10, column=1, sticky='nesw')
        self.table_sources.pack(side="top", fill="x", expand=True, anchor="n")

        self.note.pack(side="top", fill="x", expand=True, anchor="n", pady=(10, 0))

        # pack all main grids
        self.grid_top.pack(side="top", fill="x", expand=True, anchor="n", pady=(15, 15))
        self.grid_bottom.pack(side="top", fill="x", expand=True, anchor="n", pady=(15, 15))

    ############################
    # Functions for top grid
    ############################
    def set_skymodel(self, sm):
        """
        Sets the sky-model (Custom or Haslam) and displays additional widgets if Haslam.

        :param sm: the sky-model
        """
        self.sm.set(sm)
        if self.sm.get() == "Custom":
            self.label_telescope.grid_forget()
            self.dropdown_telescope.grid_forget()
        else:
            self.label_telescope.grid(row=3, column=4, sticky="w", pady=(0, 10))
            self.dropdown_telescope.grid(row=3, column=5, columnspan=3, sticky='e', pady=(0, 10))

    def set_mode(self, mode):
        """
        Sets the mode (Multiple Runs or Single Run) and displays correct information.

        :param mode: the mode
        """
        self.mode.set(mode)
        if self.mode.get() == "Single Run":
            self.create_var_param_entries_num()
            self.create_var_param_str_checkboxes()
            self.grid_middle.pack_forget()
        else:
            self.grid_bottom.pack_forget()
            self.grid_middle.pack(side="top", fill="x", expand=True, anchor="n")
            self.grid_bottom.pack(side="top", fill="x", expand=True, anchor="n")

    def set_telescope(self, telescope):
        """Sets the telescope configuration for Haslam-Map.

        :param telescope: the telescope configuration
        """
        self.telescope.set(telescope)

    def browse_antenna_file(self):
        """Browses through file system and selects desired cfg file"""
        antenna_list_path = "Antennalists/"
        filename_antenna = tkFileDialog.askopenfilename(initialdir=antenna_list_path, title="Select file",
                                                        filetypes=(("cfg files", "*.cfg"), ("all files", "*.*")))
        if filename_antenna:
            self.entry_browse_antenna.delete(0, tk.END)
            self.entry_browse_antenna.insert(0, filename_antenna)
        else:
            self.entry_browse_antenna.delete(0, tk.END)
            self.entry_browse_antenna.insert(0, self.model.antennalist)

    ############################
    # Functions for middle grid
    ############################
    def get_var_param_options(self, var_param_set):
        """
        Gets different varying parameter options as sets and calls methods for creating checkboxes and displaying
        varying parameter correctly.

        :param var_param_set: the varying parameter sets
        """
        self.model.var_param_set = var_param_set
        csv_files = self.model.csv_selector.get(var_param_set)
        parameters = helpers.get_param_tags(csv_files)
        self.create_var_param_checkboxes(parameters)

        for key in self.var_param_entries_num.keys():
            self.destroy_var_param_entries(key)
        self.var_param_entries_num.clear()
        self.label_name_num.grid_forget()
        self.label_min_num.grid_forget()
        self.label_max_num.grid_forget()
        self.label_steps_num.grid_forget()
        self.label_units_num.grid_forget()

        self.selected_params_str = []
        self.toggle_var_param_str_display()

    def create_var_param_checkboxes(self, parameters):
        """
        Creates checkboxes for numeric varying parameters and displays them in the correct place

        :param parameters: the parameter tags
        """
        for i in range(len(self.checkboxes_params)):
            self.checkboxes_params[i].destroy()
        self.checkboxes_params = []
        self.checkboxes_params_variables = []
        col = 1
        row = 1
        init_row = row
        for parameter in parameters:
            variable = tk.IntVar()
            self.checkboxes_params_variables.append(variable)
            checkbox = tk.Checkbutton(self.grid_var_param_checkboxes, text=parameter, variable=variable,
                                      command=self.get_selected_params)
            self.checkboxes_params.append(checkbox)
            if row == init_row + 3:
                row = init_row
                col = col + 1
            checkbox.grid(row=row, column=col, sticky='W')
            row = row + 1

    def get_selected_params(self):
        """
        Gets the selected varying parameters divided into numeric and alphabetic parameters and calls methods for
        creating numeric varying parameter entries and displaying alphabetic parameter names
        """
        self.selected_params_num = []
        self.selected_params_str = []
        for i in range(len(self.checkboxes_params_variables)):
            parameter = self.checkboxes_params[i].cget("text")
            if self.checkboxes_params_variables[i].get() == 1:
                if parameter in self.model.var_params_num:
                    self.selected_params_num.append(parameter)
                else:
                    self.selected_params_str.append(parameter)
        self.create_var_param_entries_num()
        self.toggle_var_param_str_display()

    def toggle_browsing(self):
        """
        Updates layout with placing and hiding widgets depending on the selected radiobutton.
        Removes all saved items from varying parameter.
        """
        if self.var_radio.get() == 2:
            self.button_browse.config(state="active")
            self.entry_browse.config(state="normal")
            self.grid_var_param_checkboxes.pack_forget()
            self.grid_var_param_settings.pack_forget()
            self.grid_var_params_str.pack_forget()
            for var in self.checkboxes_params_variables:
                var.set(0)
        else:
            self.button_browse.config(state="disabled")
            self.entry_browse.config(state="disabled")
            self.table_var_params_num.pack_forget()
            self.grid_var_params_str.pack_forget()
            self.grid_var_param_settings.pack(side="top", fill="x", expand=True, anchor="n")
            self.grid_var_param_checkboxes.pack(side="top", fill="x", expand=True, anchor="n")
            self.table_var_params_num.pack(side="top", fill="x", expand=True, anchor="n")
            self.grid_var_params_str.pack(side="top", fill="x", expand=True, anchor="n")
        self.clear_var_params()
        self.selected_params_str = []
        self.toggle_var_param_str_display()

    def destroy_var_param_entries(self, parameter):
        """
        Destroys each varying parameter entry (widget) in list.

        :param parameter: varying parameter name
        """
        for entry in self.var_param_entries_num[parameter]:
            entry.destroy()

    def clear_var_params(self):
        """Removes all varying parameter items from list and hides label widgets."""
        for key in self.var_param_entries_num.keys():
            self.destroy_var_param_entries(key)
        self.var_param_entries_num.clear()
        self.selected_params_num = []
        self.label_name_num.grid_forget()
        self.label_min_num.grid_forget()
        self.label_max_num.grid_forget()
        self.label_steps_num.grid_forget()
        self.label_units_num.grid_forget()

    def browse_file(self):
        """
        Selects and reads predefined csv-file for varying parameter and creates entries from each column of this file.
        """
        filename = tkFileDialog.askopenfilename(initialdir="./", title="Select file",
                                                filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        self.entry_browse.delete(0, tk.END)
        self.entry_browse.insert(0, filename)

        if filename:
            with open(filename, "r") as csv_num:
                reader = csv.DictReader(csv_num)
                parameter_names = []
                parameter_min = []
                parameter_max = []
                parameter_steps = []
                parameter_units = []
                i = 0
                for row in reader:
                    parameter_names.append(row['Name'])
                    parameter_min.append(row['Min'])
                    parameter_max.append(row['Max'])
                    parameter_steps.append(row['Steps'])
                    parameter_units.append(row['Units'])
                    i = i + 1

                for i in range(len(parameter_names)):
                    parameter = parameter_names[i]
                    self.selected_params_num.append(parameter)
                    entry_name = tk.Label(self.table_var_params_num, text=parameter)
                    entry_min = tk.Entry(self.table_var_params_num, highlightthickness=0)
                    entry_max = tk.Entry(self.table_var_params_num, highlightthickness=0)
                    entry_steps = tk.Entry(self.table_var_params_num, highlightthickness=0)
                    entry_units = tk.Entry(self.table_var_params_num, highlightthickness=0)
                    entry_min.insert(0, parameter_min[i])
                    entry_max.insert(0, parameter_max[i])
                    entry_steps.insert(0, parameter_steps[i])
                    entry_units.insert(0, parameter_units[i])
                    entries = [entry_name, entry_min, entry_max, entry_steps, entry_units]
                    self.var_param_entries_num.update({parameter_names[i]: entries})
                self.create_var_param_entries_num()
                self.selected_params_str = []
                self.toggle_var_param_str_display()

    def toggle_var_param_str_display(self):
        """
        Displays and layouts selected alphabetic varying parameter correctly on page.
        Parameter keys: "sm_shape", "sp_shape", "analyze_weighting"
        """
        if self.selected_params_str:
            self.label_name_str.grid(row=0, column=1, sticky="nesw")
            self.label_values_str.grid(row=0, column=2, columnspan=6, sticky="nesw")
        else:
            self.label_name_str.grid_forget()
            self.label_values_str.grid_forget()

        if "sm_shape" in self.selected_params_str:
            row = 1
            self.label_sm_shp.grid(row=row, column=1, sticky="w")
            for col in range(len(self.sm_shape_checkboxes)):
                self.sm_shape_checkboxes[col].grid(row=row, column=col + 2, sticky="w")
        else:
            self.label_sm_shp.grid_forget()
            for i in range(len(self.sm_shape_checkboxes)):
                self.sm_shape_checkboxes[i].grid_forget()
                self.sm_shape_variables[i].set(0)
            self.sm_selected_shapes = []

        if "sp_shape" in self.selected_params_str:
            row = 2
            self.label_sp_shp.grid(row=row, column=1, sticky="w")
            for col in range(len(self.sp_shape_checkboxes)):
                self.sp_shape_checkboxes[col].grid(row=row, column=col + 2, sticky="w")
        else:
            self.label_sp_shp.grid_forget()
            for i in range(len(self.sp_shape_checkboxes)):
                self.sp_shape_checkboxes[i].grid_forget()
                self.sp_shape_variables[i].set(0)
            self.sp_selected_shapes = []

        if "analyze_weighting" in self.selected_params_str:
            row = 3
            self.label_weighting.grid(row=row, column=1, sticky="w")
            for col in range(len(self.weighting_checkboxes)):
                self.weighting_checkboxes[col].grid(row=row, column=col + 2, sticky="w")
        else:
            self.label_weighting.grid_forget()
            for i in range(len(self.weighting_checkboxes)):
                self.weighting_checkboxes[i].grid_forget()
                self.weighting_variables[i].set(0)
            self.selected_weightings = []

    ####################################
    # Creating varying parameter entries
    ####################################
    def create_var_param_entries_num(self):
        """
        Creates numeric varying parameter entries for each parameter selected and displays them correctly on the page.
        """
        row = 1
        for parameter in self.selected_params_num:
            entries = []
            if parameter not in self.var_param_entries_num.keys():
                entry_name = tk.Label(self.table_var_params_num, text=parameter)
                entries.append(entry_name)
                for i in range(4):
                    entry = tk.Entry(self.table_var_params_num, highlightthickness=0)
                    entries.append(entry)
                self.var_param_entries_num.update({parameter: entries})

        self.selected_param_num()

        for parameter in self.var_param_entries_num.keys():
            if parameter not in self.selected_params_num:
                self.destroy_var_param_entries(parameter)
                del self.var_param_entries_num[parameter]
            else:
                self.var_param_entries_num[parameter][0].grid(row=row, column=1, sticky="nesw")
                for col in range(2, 6):
                    self.var_param_entries_num[parameter][col - 1].grid(row=row, column=col, sticky="nesw")
            row = row + 1

    def selected_param_num(self):
        """Hides or displays and layouts selected varying parameter correctly"""
        if self.selected_params_num:
            self.label_name_num.grid(row=0, column=1, sticky="nesw")
            self.label_min_num.grid(row=0, column=2, sticky="nesw")
            self.label_max_num.grid(row=0, column=3, sticky="nesw")
            self.label_steps_num.grid(row=0, column=4, sticky="nesw")
            self.label_units_num.grid(row=0, column=5, sticky="nesw")
        else:
            self.label_name_num.grid_forget()
            self.label_min_num.grid_forget()
            self.label_max_num.grid_forget()
            self.label_steps_num.grid_forget()
            self.label_units_num.grid_forget()

    #######################################
    # Creating varying parameter checkboxes
    #######################################
    def create_var_param_str_checkboxes(self):
        """
        Creates checkboxes for specific alphabetic varying parameter values for the parameter keys: "sm_shape",
        "sp_shape", "analyze_weighting"
        """
        self.create_sm_shape_checkboxes()
        self.create_sp_shape_checkboxes()
        self.create_weighting_checkboxes()

    def create_sm_shape_checkboxes(self):
        """Creates checkboxes for sm_shape."""
        self.sm_shape_checkboxes = []
        self.sm_shape_variables = []
        self.label_sm_shp = tk.Label(self.grid_var_params_str, text="sm_shape")
        for shape in self.model.shapes:
            checkbox_var = tk.IntVar()
            checkbox = tk.Checkbutton(self.grid_var_params_str, variable=checkbox_var, text=shape,
                                      command=self.get_selected_sm_shapes)
            self.sm_shape_checkboxes.append(checkbox)
            self.sm_shape_variables.append(checkbox_var)

    def create_sp_shape_checkboxes(self):
        """Creates checkboxes for sp_shape."""
        self.sp_shape_checkboxes = []
        self.sp_shape_variables = []
        self.label_sp_shp = tk.Label(self.grid_var_params_str, text="sp_shape")
        for shape in self.model.shapes:
            checkbox_var = tk.IntVar()
            checkbox = tk.Checkbutton(self.grid_var_params_str, variable=checkbox_var, text=shape,
                                      command=self.get_selected_sp_shapes)
            self.sp_shape_checkboxes.append(checkbox)
            self.sp_shape_variables.append(checkbox_var)

    def create_weighting_checkboxes(self):
        """Creates checkboxes for analyze_weighting."""
        self.weighting_checkboxes = []
        self.weighting_variables = []
        self.label_weighting = tk.Label(self.grid_var_params_str, text="analyze_weighting")
        for weighting in self.model.weightings:
            checkbox_var = tk.IntVar()
            checkbox = tk.Checkbutton(self.grid_var_params_str, variable=checkbox_var, text=weighting,
                                      command=self.get_selected_weightings)
            self.weighting_checkboxes.append(checkbox)
            self.weighting_variables.append(checkbox_var)

    def get_selected_sm_shapes(self):
        """Gets the selected values of sky-model shape and saves it to list."""
        self.sm_selected_shapes = []
        for i in range(len(self.sm_shape_variables)):
            if self.sm_shape_variables[i].get() == 1:
                sm_shape = self.sm_shape_checkboxes[i].cget("text")
                self.sm_selected_shapes.append(sm_shape)

    def get_selected_sp_shapes(self):
        """Gets the selected values of source shape and saves it to list."""
        self.sp_selected_shapes = []
        for i in range(len(self.sp_shape_variables)):
            if self.sp_shape_variables[i].get() == 1:
                sp_shape = self.sp_shape_checkboxes[i].cget("text")
                self.sp_selected_shapes.append(sp_shape)

    def get_selected_weightings(self):
        """Gets the selected values of weightings and saves it to list."""
        self.selected_weightings = []
        for i in range(len(self.weighting_variables)):
            if self.weighting_variables[i].get() == 1:
                weighting = self.weighting_checkboxes[i].cget("text")
                self.selected_weightings.append(weighting)

    #########################################
    # Input validation for varying parameters
    #########################################
    def check_var_values_selected(self):
        """Creates input validation that at least one varying parameter has been selected."""
        valid = True
        error_message = ""

        if self.mode.get() == "Multiple Runs":
            if not self.selected_params_num and not self.selected_params_str:
                if "- Select at least one varying parameter" not in error_message:
                    error_message += "- Select at least one varying parameter" + "\n"
                    valid = False

        if not valid:
            self.valid_selected = False
            tkMessageBox.showerror("Missing Varying Parameter", error_message)
        else:
            self.valid_selected = True

    def check_var_values_num(self):
        """
        Creates input validation on varying parameter values for entries min-value, max-value, steps and units.
        Shows message box if incorrect values are entered.
        """
        color_error = "red"
        color_valid = "black"
        valid = True
        error_message = ""
        message_sp_flux = "The unit is already provided in the Sources (Fixed Parameter Configuration)."

        for key in self.var_param_entries_num.keys():
            entries = self.var_param_entries_num[key]
            entry_min = entries[1]
            entry_max = entries[2]
            entry_steps = entries[3]
            entry_units = entries[4]

            entry_min.config(highlightbackground=color_valid, highlightcolor=color_valid, highlightthickness=0)
            entry_max.config(highlightbackground=color_valid, highlightcolor=color_valid, highlightthickness=0)
            entry_steps.config(highlightbackground=color_valid, highlightcolor=color_valid, highlightthickness=0)
            entry_units.config(highlightbackground=color_valid, highlightcolor=color_valid, highlightthickness=0)

            min_value = entry_min.get()
            max_value = entry_max.get()
            steps_value = entry_steps.get()
            units_value = entry_units.get()

            if not min_value.replace('.', '', 1).isdigit():
                if "- Min must be numeric" not in error_message:
                    error_message += "- Min must be numeric" + "\n"
                valid = False
                entry_min.config(highlightbackground=color_error, highlightcolor=color_error, highlightthickness=2)
            if not max_value.replace('.', '', 1).isdigit():
                if "- Max must be numeric" not in error_message:
                    error_message += "- Max must be numeric" + "\n"
                valid = False
                entry_max.config(highlightbackground=color_error, highlightcolor=color_error, highlightthickness=2)
            if not steps_value.isdigit():
                if "- Steps must be a positive integer" not in error_message:
                    error_message += "- Steps must be a positive integer" + "\n"
                valid = False
                entry_steps.config(highlightbackground=color_error, highlightcolor=color_error, highlightthickness=2)
            elif int(steps_value) < 2:
                if "- Steps must be positive and greater than 1" not in error_message:
                    error_message += "- Steps must be positive and greater than 1" + "\n"
                valid = False
                entry_steps.config(highlightbackground=color_error, highlightcolor=color_error, highlightthickness=2)
            if "sp_flux" in self.var_param_entries_num.keys():
                if units_value:
                    if "- Units for sp_flux must be empty. " + message_sp_flux not in error_message:
                        error_message += "- Units for sp_flux must be empty. " + message_sp_flux
                    valid = False
                    entry_units.config(highlightbackground=color_error, highlightcolor=color_error,
                                       highlightthickness=2)

        if not valid:
            self.valid_num = False
            tkMessageBox.showerror("Invalid Input", error_message)
        else:
            self.valid_num = True

    def check_var_values_str(self):
        """
        Creates input validation on alphabetic varying parameter values. Shows message box if incorrect values
        are entered.
        Key Parameter: sm_shape, sp_shape and weighting
        """
        valid = True
        error_message = ""

        if "analyze_weighting" in self.selected_params_str:
            if not self.selected_weightings:
                if "- Select at least one analyze_weighting" not in error_message:
                    error_message += "- Select at least one analyze_weighting" + "\n"
                    valid = False
        if "sm_shape" in self.selected_params_str:
            if not self.sm_selected_shapes:
                if "- Select at least one shape" not in error_message:
                    error_message += "- Select at least one shape" + "\n"
                    valid = False
        if "sp_shape" in self.selected_params_str:
            if not self.sp_selected_shapes:
                if "- Select at least one shape" not in error_message:
                    error_message += "- Select at least one shape" + "\n"
                    valid = False

        if not valid:
            self.valid_str = False
            tkMessageBox.showerror("Invalid Input", error_message)
        else:
            self.valid_str = True

    ############################
    # Functions bottom grid
    ############################
    def create_entry_table_sources(self, nsp):
        """
        Creates entries for fixed parameter of the sources corresponding to the number of selected sources
        in the dropdown.

        :param nsp: number of sources
        """
        self.table_sources.grid_columnconfigure(len(self.sp_entries) + 2, weight=0)
        if nsp > len(self.sp_entries):
            for col in range(len(self.sp_entries), nsp):
                label_name = tk.Label(self.table_sources, text="Source" + str(col + 1), borderwidth=1, relief="solid")
                entry_flux = tk.Entry(self.table_sources, width=10)
                entry_fluxunit = tk.Entry(self.table_sources, width=10)
                entry_direction_ra = tk.Entry(self.table_sources, width=10)
                entry_direction_dec = tk.Entry(self.table_sources, width=10)
                entry_shape = tk.Entry(self.table_sources, width=10)
                entry_majoraxis = tk.Entry(self.table_sources, width=10)
                entry_minoraxis = tk.Entry(self.table_sources, width=10)
                entry_positionangle = tk.Entry(self.table_sources, width=10)
                entry_frequency = tk.Entry(self.table_sources, width=10)
                entry_frequency_unit = tk.Entry(self.table_sources, width=10)

                self.sp_entries.append([label_name, entry_flux, entry_fluxunit, entry_direction_ra, entry_direction_dec,
                                        entry_majoraxis, entry_minoraxis, entry_positionangle, entry_shape,
                                        entry_frequency, entry_frequency_unit])

                for index, line in self.model.default_params_sp.iterrows():
                    entry_flux.insert(0, line["sp_flux"])
                    entry_fluxunit.insert(0, line["sp_fluxunit"])
                    entry_direction_ra.insert(0, line["sp_direction_ra"])
                    entry_direction_dec.insert(0, line["sp_direction_dec"])
                    entry_shape.insert(0, line["sp_shape"])
                    entry_majoraxis.insert(0, line["sp_majoraxis"])
                    entry_minoraxis.insert(0, line["sp_minoraxis"])
                    entry_positionangle.insert(0, line["sp_positionangle"])
                    entry_frequency.insert(0, line["sp_frequency"])
                    entry_frequency_unit.insert(0, line["sp_frequency_unit"])

                    label_name.grid(row=0, column=col + 2, sticky="nesw")
                    entry_flux.grid(row=1, column=col + 2)
                    entry_fluxunit.grid(row=2, column=col + 2)
                    entry_direction_ra.grid(row=3, column=col + 2)
                    entry_direction_dec.grid(row=4, column=col + 2)
                    entry_shape.grid(row=5, column=col + 2)
                    entry_majoraxis.grid(row=6, column=col + 2)
                    entry_minoraxis.grid(row=7, column=col + 2)
                    entry_positionangle.grid(row=8, column=col + 2)
                    entry_frequency.grid(row=9, column=col + 2)
                    entry_frequency_unit.grid(row=10, column=col + 2)
        else:
            for i in range(nsp, len(self.sp_entries)):
                for entry in self.sp_entries[i]:
                    entry.destroy()
            self.sp_entries = self.sp_entries[0:nsp]
        self.table_sources.grid_columnconfigure(nsp + 2, weight=1)

    def load_fixed_params(self, entry_browse, grid):
        """
        Reads fixed parameter values from file and calls method to create fixed parameter entries which
        displays them correctly on the page.

        :param entry_browse: The entry with the file path.
        :param grid: The grid where the table should be created.
        """
        filename = tkFileDialog.askopenfilename(initialdir="./", title="Select file",
                                                filetypes=(("csv files", "*.csv"), ("all files", "*.*")))
        if filename:
            entry_browse.insert(0, filename)
            helpers.destroy_slaves(grid)
            self.model.fixed_params = helpers.read_fixed_params_from_file(filename, ["Name, Values, Units"])
            helpers.create_entry_table(self.model.fixed_params, grid)

    def load_fixed_params_sim(self):
        """Loads fixed parameter simulation (instrumental parameters) values."""
        self.load_fixed_params(self.entry_browse_fixed_sim, self.table_fixed_params_sim)

    def load_fixed_params_sm(self):
        """Loads fixed parameter sky-model (sky-based parameters) values."""
        self.load_fixed_params(self.entry_browse_fixed_sm, self.table_fixed_params_sm)

    ##############################
    # Functions to save input data
    ##############################
    def save_antenna_list(self):
        """Saves antenna list to the model"""
        if os.path.exists(self.entry_browse_antenna.get()):
            path_tail = os.path.split(self.entry_browse_antenna.get())
            self.model.antennalist = path_tail[1]
        else:
            self.model.antennalist = self.entry_browse_antenna.get()

    def save_values_to_model(self):
        """Saves all input data from this page to the model."""
        self.model.mode = self.mode.get()
        self.model.sm = self.sm.get()
        self.model.telescope = self.telescope.get()
        self.save_antenna_list()
        self.model.number_of_sources = self.number_of_sources.get()
        self.model.fixed_params_sim = helpers.read_values_from_entry_table(self.table_fixed_params_sim,
                                                                           ["Name", "Value", "Units"])
        self.model.fixed_params_sm = helpers.read_values_from_entry_table(self.table_fixed_params_sm,
                                                                          ["Name", "Value", "Units"])
        sources_columns = ["Parameter"]
        for i in range(self.number_of_sources.get()):
            sources_columns.append("Source" + str(i + 1))
        self.model.fixed_params_sp = helpers.read_values_from_entry_table(self.table_sources, sources_columns)

        if self.mode.get() == "Single Run":
            self.model.sm_selected_shapes = []
            self.model.sp_selected_shapes = []
            self.model.selected_weightings = []
            self.model.var_param_values_lists = {}
            self.model.checkboxes_params_variables = []
        elif self.mode.get() == "Multiple Runs":
            self.model.var_param_set = self.var_param_set.get()
            self.model.var_params_values_num = helpers.read_values_from_entry_table(self.table_var_params_num,
                                                                                    ["Name", "Value", "Units"])
            self.model.sm_selected_shapes = self.sm_selected_shapes
            self.model.sp_selected_shapes = self.sp_selected_shapes
            self.model.selected_weightings = self.selected_weightings
            self.model.var_param_values_lists = self.model.get_var_param_values()

            self.model.checkboxes_params_variables = []
            for variable in self.checkboxes_params_variables:
                self.model.checkboxes_params_variables.append(variable.get())

            self.model.sm_shape_variables = []
            for variable in self.sm_shape_variables:
                self.model.sm_shape_variables.append(variable.get())

            self.model.sp_shape_variables = []
            for variable in self.sp_shape_variables:
                self.model.sp_shape_variables.append(variable.get())

            self.model.weighting_variables = []
            for variable in self.weighting_variables:
                self.model.weighting_variables.append(variable.get())

        self.model.estimation = helpers.convert_time_to_string(self.model.calculate_estimated_time_total())

    def load_values_from_config(self, config):
        """
        Fills the widgets of the page with data from the configuration. Only affects widgets where values can be
        changed manually.

        :param: config: The predefined configuration.
        """
        # Load Settings
        self.set_mode(config["mode"])
        self.set_skymodel(config["sm"])
        self.set_telescope(config["telescope"])
        self.entry_browse_antenna.delete(0, tk.END)
        self.entry_browse_antenna.insert(0, config["antennalist"])

        # Load varying parameter configuration
        if config["mode"] == "Multiple Runs":
            self.var_param_set.set(config["var_param_set"])
            self.get_var_param_options(config["var_param_set"])
            for i in range(len(config["checkboxes_params_variables"])):
                self.checkboxes_params_variables[i].set(config["checkboxes_params_variables"][i])
            self.get_selected_params()
            self.create_var_param_entries_num()
            helpers.load_table_from_df(self.table_var_params_num, config["var_params_values_num"])
            for i in range(len(self.sm_shape_variables)):
                self.sm_shape_checkboxes[i].config(variable=self.sm_shape_variables[i])
                self.sm_shape_variables[i].set(config["sm_shape_variables"][i])
            for i in range(len(self.sp_shape_variables)):
                self.sp_shape_checkboxes[i].config(variable=self.sp_shape_variables[i])
                self.sp_shape_variables[i].set(config["sp_shape_variables"][i])
            for i in range(len(self.weighting_variables)):
                self.weighting_checkboxes[i].config(variable=self.weighting_variables[i])
                self.weighting_variables[i].set(config["weighting_variables"][i])
            self.toggle_var_param_str_display()
            self.get_selected_sm_shapes()
            self.get_selected_sp_shapes()
            self.get_selected_weightings()

        # Load fixed parameter configuration
        helpers.destroy_slaves(self.table_fixed_params_sim)
        helpers.create_entry_table(config["fixed_params_sim"], self.table_fixed_params_sim)
        helpers.destroy_slaves(self.table_fixed_params_sm)
        helpers.create_entry_table(config["fixed_params_sm"], self.table_fixed_params_sm)
        self.number_of_sources.set(config["number_of_sources"])
        self.create_entry_table_sources(config["number_of_sources"])
        helpers.load_table_from_df(self.table_sources, config["fixed_params_sp"])

        self.save_values_to_model()
