import os
import pickle
import Tkinter as tk
import tkFileDialog
import tkMessageBox
from Pipeline import pipeline
from UserInterface.UITools.image_comparison import ComparisonPage
from UserInterface.UITools.output_analysis import AnalysisPage
from UserInterface.configurationpage import ConfigurationPage
from UserInterface.progresspage import ProgressPage
from UserInterface.summarypage import SummaryPage
from UserInterface.util import helpers as helpers
from UserInterface.util.scrollbarframe import ScrollbarFrame


class MainView(tk.Frame):
    """
       Subclass of tk.Frame. This class creates and layouts main widgets for all pages of the GUI. This class starts the
       AppPipeline by clicking on the run button.
       """

    def __init__(self, model, *args, **kwargs):
        """
        This method will be called when an object of this class is instantiated. It initializes variables and objects
        and calls methods.
        :param model: the input model
        :param args: arguments
        :param kwargs: keyword arguments
        """
        tk.Frame.__init__(self, *args, **kwargs)
        self.model = model
        self.analysis_window = None
        self.comparison_window = None
        self.initialize_widgets()
        self.layout_widgets()

    def initialize_widgets(self):
        """Initializes all needed widgets for the page."""
        self.menu = tk.Menu(self)
        self.master.config(menu=self.menu)

        self.menu_file = tk.Menu(self.menu)
        self.menu_file.add_command(label="Save", command=self.save_config)
        self.menu_file.add_command(label="Load", command=self.load_config)
        self.menu_help = tk.Menu(self.menu)
        self.menu_help.add_command(label="Open Manual", command=helpers.open_manual)

        self.menu_tools = tk.Menu(self.menu)
        self.menu_tools.add_command(label="Output Analysis", command=self.open_analysis_tool)
        self.menu_tools.add_command(label="Image Comparison", command=self.open_comparison_tool)

        self.menu.add_cascade(label="File", menu=self.menu_file)
        self.menu.add_cascade(label="Tools", menu=self.menu_tools)
        self.menu.add_cascade(label="Help", menu=self.menu_help)

        self.grid_buttons = tk.Frame(self)

        self.sb1 = ScrollbarFrame(self)
        frame1 = self.sb1.scrolled_frame

        self.page1 = ConfigurationPage(self.model, frame1)
        self.page2 = SummaryPage(self.model, frame1)
        self.page3 = ProgressPage(self.model)

        self.button_next = tk.Button(self.grid_buttons, text="Next", command=self.next_page, height=2, width=10)
        self.button_prev = tk.Button(self.grid_buttons, text="Previous", command=self.previous_page, height=2, width=10)
        self.button_run = tk.Button(self.grid_buttons, text="Run", command=self.confirm_run, height=2, width=10,
                                    bg="#40A229", activebackground="#4CC530")

    def layout_widgets(self):
        """Displays and layouts the widgets in the correct places"""
        self.grid_buttons.pack(side="bottom", fill="x", expand=False, anchor="s")
        self.grid_buttons.grid_columnconfigure(1, weight=1)

        self.sb1.pack(side="top", fill="both", expand=True)
        self.button_next.grid(row=0, column=2, sticky="E", padx=15, pady=15)
        self.page1.pack(side="top", fill="both", expand=True)

    def check_save_config(self):
        """
        Checks varying parameter values for saving configuration as pkl file and returns true if valid else returns
        false.
        """
        self.page1.check_var_values_selected()
        if self.page1.valid_selected is False:
            return False
        self.page1.check_var_values_num()
        self.page1.check_var_values_str()
        if self.page1.valid_num is False:
            return False
        if self.page1.valid_str is False:
            return False
        return True

    def save_config(self):
        """Saves a pkl file with current configurations from the model."""
        valid = self.check_save_config()
        if not valid:
            return
        filename = tkFileDialog.asksaveasfilename(initialfile="config.pkl", initialdir="./Configurations",
                                                  title="Select file", filetypes=(("pkl files", "*.pkl"), ))
        if filename:
            with open(filename, 'wb') as output:
                self.page1.save_values_to_model()
                config = {"mode": self.model.mode,
                          "sm": self.model.sm,
                          "telescope": self.model.telescope,
                          "antennalist": self.model.antennalist,
                          "var_param_set": self.model.var_param_set,
                          "checkboxes_params_variables": self.model.checkboxes_params_variables,
                          "var_params_values_num": self.model.var_params_values_num,
                          "sm_shape_variables": self.model.sm_shape_variables,
                          "sp_shape_variables": self.model.sp_shape_variables,
                          "weighting_variables": self.model.weighting_variables,
                          "fixed_params_sim": self.model.fixed_params_sim,
                          "fixed_params_sm": self.model.fixed_params_sm,
                          "number_of_sources": self.model.number_of_sources,
                          "fixed_params_sp": self.model.fixed_params_sp}
                pickle.dump(config, output, pickle.HIGHEST_PROTOCOL)

    def load_config(self):
        """Loads a pkl file with saved configurations into the model."""
        filename = tkFileDialog.askopenfilename(initialdir="./Configurations", title="Select file",
                                                filetypes=(("pkl files", "*.pkl"),))
        if filename:
            with open(filename, 'rb') as input_file:
                config = pickle.load(input_file)
                self.page1.load_values_from_config(config)
                self.master.update()

    def next_page(self):
        """
        Displays widgets on the next page (summary page) corresponding to the selected mode and saves
        values to input model. Checks input validation for entered varying parameter values.
        """
        if self.page1.mode.get() == "Multiple Runs":
            valid = self.check_save_config()
            if not valid:
                return
        if self.page1.mode.get() == "Single Run":
            pass
        try:
            self.page1.save_values_to_model()
            self.page2.save_output_path_to_model()
        except:
            tkMessageBox.showerror("Invalit Input", "Invalid input. \nPlease check your configuration.\n"
                                   "If you require further information about input configurations please check out "
                                                    "the user manual.")
        else:
            self.page1.pack_forget()
            self.page2.pack(side="top", fill="both", expand=True)
            self.page2.fill_widgets()
            self.button_next.grid_remove()
            self.button_prev.grid(row=0, column=0, sticky="W", padx=15, pady=15)
            self.button_run.grid(row=0, column=2, sticky="E", padx=15, pady=15)

    def previous_page(self):
        """
        Displays widgets on the previous page (configuration page) and hides summary page.
        """
        self.page1.valid_num_steps = False
        self.page2.pack_forget()
        self.button_prev.grid_remove()
        self.button_run.grid_remove()
        self.button_next.grid(row=0, column=2, sticky="E", padx=15, pady=15)
        self.page1.pack(side="top", fill="both", expand=True)

    def confirm_run(self):
        """
        Shows dialog to confirm the AppPipeline run and starts the AppPipeline if "yes" is pressed. Shows the progress
        page while the AppPipeline is running.
        """
        path = self.page2.entry_browse.get()
        if len(path) == 0:
            error_message = "Choose an output path."
            tkMessageBox.showerror("Missing Output Path", error_message)
            return
        if not os.path.isdir(path):
            os.mkdir(path)
        self.model.output_path = path

        message_box = tkMessageBox.askquestion("Run Confirmation", "Are you sure you want to start the simulation?",
                                               icon="warning")
        if message_box == "yes":
            self.page2.pack_forget()
            self.button_run.grid_remove()
            self.button_prev.grid_remove()
            self.sb1.pack_forget()
            self.page3.pack(side="top", fill="both", expand=True)

            self.master.update()
            self.master.after(3000, pipeline.run(self.model))

            self.page3.pack_forget()
            self.sb1.pack(side="top", fill="both", expand=True)
            self.button_prev.grid(row=0, column=0, sticky="W", padx=15, pady=15)
            self.button_run.grid(row=0, column=2, sticky="E", padx=15, pady=15)
            self.page2.pack(side="top", fill="both", expand=True)

    def open_analysis_tool(self):
        """Opens a new window of the Analysis page and displays widgets."""
        if self.analysis_window:
            self.analysis_window.destroy()
        self.analysis_window = tk.Toplevel()
        self.analysis_window.attributes('-topmost', True)
        self.analysis_window.title("Output Analysis Tool")
        self.analysis_window.wm_geometry("500x250")
        self.analysis_window.minsize(460, 220)
        page_analysis = AnalysisPage(self.analysis_window)
        page_analysis.pack(side="top", fill="both", expand=True)

    def open_comparison_tool(self):
        """Opens a new window of the Comparison page and displays widgets."""
        if self.comparison_window:
            self.comparison_window.destroy()
        self.comparison_window = tk.Toplevel()
        self.comparison_window.attributes('-topmost', True)
        self.comparison_window.title("Image Comparison Tool")
        self.comparison_window.wm_geometry("500x290")
        self.comparison_window.minsize(460, 240)
        page_comparison = ComparisonPage(self.comparison_window)
        page_comparison.pack(side="top", fill="both", expand=True)