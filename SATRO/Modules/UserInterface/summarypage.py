import Tkinter as tk
import tkFileDialog
import ttk
import os

import util.helpers as helpers


class SummaryPage(tk.Frame):
    """
    Subclass of tk.Frame. This class creates and layouts widgets for the second page of the GUI. This class
    shows all previous settings and configurations for the radio observation.
    """

    def __init__(self, model, *args, **kwargs):
        """
        This methods will be called when an object of this class is instantiated. It initializes variables and calls
        methods.

        :param model: the input model
        :param args: arguments
        :param kwargs: keyword arguments
        """
        tk.Frame.__init__(self, *args, **kwargs)
        self.model = model

        #########################
        # call functions
        #########################
        self.initialize_widgets()
        self.layout_widgets()

    def initialize_widgets(self):
        """Initializes all needed widgets for the page."""
        self.label_title = tk.Label(self, text="Summary", font=("Arial", 20, 'bold'), fg="white", bg="#7695e3")

        #########################
        # Widgets for top grid
        #########################
        self.grid_top = tk.Frame(self)
        self.label_mode = tk.Label(self.grid_top, text='Mode: ')
        self.label_mode_value = tk.Label(self.grid_top)
        self.label_sm = tk.Label(self.grid_top, text='Sky-model: ')
        self.label_sm_value = tk.Label(self.grid_top)
        self.label_telescope = tk.Label(self.grid_top, text='Telescope: ')
        self.label_telescope_value = tk.Label(self.grid_top)
        self.label_antennalist = tk.Label(self.grid_top, text="Antenna list: ")
        self.label_antennalist_value = tk.Label(self.grid_top)

        #########################
        # Widgets for notebook
        #########################
        self.note = ttk.Notebook(self)
        self.tab1 = tk.Frame(self.note)
        self.tab2 = tk.Frame(self.note)
        self.tab3 = tk.Frame(self.note)
        self.tab4 = tk.Frame(self.note)
        self.note.add(self.tab1, text="Fixed Instrumental")
        self.note.add(self.tab2, text="Fixed Sky-model")
        self.note.add(self.tab3, text="Fixed Sources")
        self.note.add(self.tab4, text="Varying Params Num")
        self.treeview_def_sim = ttk.Treeview(self.tab1, height=18, show="headings")
        self.treeview_def_sm = ttk.Treeview(self.tab2, height=18, show="headings")
        self.treeview_def_sp = ttk.Treeview(self.tab3, height=18, show="headings")
        self.treeview_var_num = ttk.Treeview(self.tab4, height=18, show="headings")

        #########################
        # Widgets for bottom grid
        #########################
        self.grid_bottom = tk.Frame(self)
        self.label_sm_shp = tk.Label(self.grid_bottom, text="Sky-model shape values: ")
        self.label_sm_shp_value = tk.Label(self.grid_bottom)
        self.label_sp_shp = tk.Label(self.grid_bottom, text="Source shape values: ")
        self.label_sp_shp_value = tk.Label(self.grid_bottom)
        self.label_weightings = tk.Label(self.grid_bottom, text="Weightings values: ")
        self.label_weightings_value = tk.Label(self.grid_bottom)
        self.label_niter = tk.Label(self.grid_bottom, text='Number of iterations: ')
        self.label_niter_value = tk.Label(self.grid_bottom)
        self.label_estim = tk.Label(self.grid_bottom, text='Estimated time: ')
        self.label_estim_value = tk.Label(self.grid_bottom)

        # Output-path widget
        self.grid_bottom_path = tk.Frame(self)
        self.path = os.getcwd()
        self.label_browse = tk.Label(self.grid_bottom_path, text="Output folder path: ")
        self.entry_browse = tk.Entry(self.grid_bottom_path)
        self.entry_browse.insert(0, self.path)
        self.button_browse = tk.Button(self.grid_bottom_path, text="Browse...", command=self.browse_output_path)

    def layout_widgets(self):
        """Displays and layouts the widgets in the correct places."""
        self.label_title.pack(side="top", fill="x", expand=True, anchor="n")

        #########################
        # Top grid layout
        #########################
        self.grid_top.grid_columnconfigure(0, weight=1)
        self.grid_top.grid_columnconfigure(99, weight=1)
        self.label_mode.grid(row=0, column=1, sticky="W")
        self.label_mode_value.grid(row=0, column=2, sticky="W")
        self.label_sm.grid(row=1, column=1, sticky="W")
        self.label_sm_value.grid(row=1, column=2, sticky="W")
        self.label_telescope.grid(row=2, column=1, sticky="W")
        self.label_telescope_value.grid(row=2, column=2, sticky="W")
        self.label_antennalist.grid(row=3, column=1, sticky="W")
        self.label_antennalist_value.grid(row=3, column=2, sticky="W")
        self.grid_top.pack(fill="x", expand=True, anchor="n")

        #########################
        # Middle treeview layout
        #########################
        self.note.pack(fill="x", expand=True, anchor="n")
        self.treeview_def_sim.pack()
        self.treeview_def_sm.pack()
        self.treeview_def_sp.pack()
        self.treeview_var_num.pack()

        #########################
        # Bottom grid layout
        #########################
        self.grid_bottom.grid_columnconfigure(0, weight=1)
        self.grid_bottom.grid_columnconfigure(99, weight=1)
        self.label_sm_shp.grid(row=0, column=1, sticky="W")
        self.label_sm_shp_value.grid(row=0, column=2, sticky="W")
        self.label_sp_shp.grid(row=1, column=1, sticky="W")
        self.label_sp_shp_value.grid(row=1, column=2, sticky="W")
        self.label_weightings.grid(row=2, column=1, sticky="W")
        self.label_weightings_value.grid(row=2, column=2, sticky="W")
        self.label_niter.grid(row=3, column=1, sticky="W")
        self.label_niter_value.grid(row=3, column=2, sticky="W")
        self.label_estim.grid(row=4, column=1, sticky="W")
        self.label_estim_value.grid(row=4, column=2, sticky="W")
        self.grid_bottom.pack(fill="x", expand=True, anchor="n")

        #########################
        # Bottom path grid layout
        #########################
        self.grid_bottom_path.grid_columnconfigure(0, weight=1)
        self.grid_bottom_path.grid_columnconfigure(99, weight=1)
        self.label_browse.grid(row=1, column=1, sticky="W")
        self.entry_browse.grid(row=1, column=2, sticky="W")
        self.button_browse.grid(row=1, column=3, sticky="W")
        self.grid_bottom_path.pack(fill="x", expand=True, anchor="n")

    def fill_widgets(self):
        """
        Fills the widgets with data from input model.
        """
        self.label_mode_value.config(text=self.model.mode)
        self.label_sm_value.config(text=self.model.sm)
        self.label_telescope_value.config(text=self.model.telescope)
        self.label_antennalist_value.config(text=self.model.antennalist)

        if self.model.mode == "Multiple Runs":
            helpers.fill_treeview(self.treeview_var_num, self.model.var_params_values_num)
            self.label_sm_shp_value.config(text=str(self.model.sm_selected_shapes)[1:-1])
            self.label_sp_shp_value.config(text=str(self.model.sp_selected_shapes)[1:-1])
            self.label_weightings_value.config(text=str(self.model.selected_weightings)[1:-1])
        helpers.fill_treeview(self.treeview_def_sim, self.model.fixed_params_sim)
        helpers.fill_treeview(self.treeview_def_sm, self.model.fixed_params_sm)
        helpers.fill_treeview(self.treeview_def_sp, self.model.fixed_params_sp)
        self.label_niter_value.config(text=self.model.get_number_of_iterations())
        self.label_estim_value.config(text=self.model.estimation)

    def browse_output_path(self):
        """Select directory for storing the output data after the radio observations."""
        filename = tkFileDialog.askdirectory(initialdir=self.path)
        self.entry_browse.delete(0, tk.END)
        self.entry_browse.insert(0, filename)

    def save_output_path_to_model(self):
        """Saves the output-path to the input model."""
        self.model.output_path = self.path
