import pickle
import Tkinter as tk
import tkFileDialog
import os.path
import matplotlib.pyplot as plt

from UserInterface.UITools.util import load_fits_files, create_analysis_plot, check_folder
from UserInterface.util.popupwindow import PopupWindows

try:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk as navTool
except ImportError:
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg as navTool
import tkMessageBox


class AnalysisPage(tk.Frame):
    """
    Subclass of tk.Frame. This class creates and layouts widgets for the analysis page of the GUI.
    """

    def __init__(self, *args, **kwargs):
        """
        This methods will be called when an object of this class is instantiated. It initializes variables and calls
        methods.

        :param args: arguments
        :param kwargs: keyword arguments
        """
        tk.Frame.__init__(self, *args, **kwargs)
        self.popup = PopupWindows()
        self.initialize_widgets()
        self.layout_widgets()
        plt.ioff()
        plt.style.use('dark_background')

    def initialize_widgets(self):
        """Initializes all needed widgets for the page."""
        self.grid_top = tk.Frame(self)

        self.label_title = tk.Label(self.grid_top, text="Output Analysis", font=("Arial", 20, 'bold'), fg="white",
                                    bg="#7695e3")
        self.label = tk.Label(self.grid_top, text="Select directory")
        self.entry_browse = tk.Entry(self.grid_top, state="normal")
        self.button_browse = tk.Button(self.grid_top, text="Browse...", command=self.load_output_folder, state="normal")

        self.button_popup_help_analysis = tk.Button(self.grid_top, text="?", command=self.popup.popup_window_analysis,
                                                    width=4)

        self.grid_buttons = tk.Frame(self)
        self.button_image = tk.Button(self.grid_buttons, text="Show Image Plots", command=self.display_image,
                                      state="disabled")
        self.button_residual = tk.Button(self.grid_buttons, text="Show CLEAN-Residual Plots",
                                         command=self.display_residual, state="disabled")
        self.button_fidelity = tk.Button(self.grid_buttons, text="Show Fidelity Plots", command=self.display_fidelity,
                                         state="disabled")

    def layout_widgets(self):
        """Displays and layouts the widgets in the correct places."""
        self.label_title.grid(row=0, column=0, columnspan=100, sticky="nesw")
        self.button_popup_help_analysis.grid(row=1, column=99, sticky='e', padx=(10, 10), pady=(10, 0))

        self.label.grid(row=2, column=1, sticky="nesw", pady=(10, 0))
        self.entry_browse.grid(row=2, column=2, sticky="nesw", pady=(10, 0))
        self.button_browse.grid(row=2, column=3, sticky="nesw", pady=(10, 0))

        self.grid_top.grid_columnconfigure(0, weight=1)
        self.grid_top.grid_columnconfigure(99, weight=1)
        self.grid_top.pack(anchor="n", fill="x", expand=True)

        self.button_image.grid(row=0, column=1, sticky="nesw", pady=(5, 0))
        self.button_residual.grid(row=1, column=1, sticky="nesw", pady=(5, 0))
        self.button_fidelity.grid(row=2, column=1, sticky="nesw", pady=(5, 0))

        self.grid_buttons.grid_columnconfigure(0, weight=1)
        self.grid_buttons.grid_columnconfigure(99, weight=1)
        self.grid_buttons.pack(anchor="n", fill="x", expand=True)

    def load_output_folder(self):
        """Loads desired output folder for analysing the CASA images."""
        path_folder = tkFileDialog.askdirectory(parent=self, initialdir=os.getcwd(), title="Select output folder")
        self.master.lift()
        self.master.attributes('-topmost', False)
        self.entry_browse.delete(0, tk.END)
        self.entry_browse.insert(0, path_folder)
        if path_folder:  # Figures
            self.name_folder = os.path.split(path_folder)[1]
            valid, error_messages = check_folder(path_folder, self.name_folder)
            if not valid:
                error_string = "The selected folder is not a valid output folder."
                for msg in error_messages:
                    error_string = error_string + "\n" + msg
                tkMessageBox.showerror("Invalid Folder", error_string, parent=self)
                return

            self.fits_files = load_fits_files(path_folder + "/FITS_Files/" + self.name_folder)
            with open(path_folder + "/Skymodel/sources.pkl", "rb") as inputfile:
                self.sources = pickle.load(inputfile)

            self.button_image.configure(state="normal")
            self.button_residual.configure(state="normal")
            self.button_fidelity.configure(state="normal")

    def display_image(self):
        """Displays the image plots."""
        self.fig_image = create_analysis_plot(self.fits_files[0], self.name_folder + " Image", self.sources)
        self.fig_image.show()

    def display_residual(self):
        """Displays the residual plots."""
        self.fig_residual = create_analysis_plot(self.fits_files[1], self.name_folder + " CLEAN-Residual", self.sources)
        self.fig_residual.show()

    def display_fidelity(self):
        """Displays the fidelity plots."""
        self.fig_fidelity = create_analysis_plot(self.fits_files[2], self.name_folder + " Fidelity", self.sources)
        self.fig_fidelity.show()
