import Tkinter as tk
import tkFileDialog
import tkMessageBox
import matplotlib.pyplot as plt
import numpy as np
import os
from astropy.io import fits

from UserInterface.UITools.util import create_comparison_plot
from UserInterface.util.popupwindow import PopupWindows


class ComparisonPage(tk.Frame):
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
        self.loaded_fits1 = False
        self.loaded_fits2 = False
        self.popup = PopupWindows()
        self.initialize_widgets()
        self.layout_widgets()
        plt.ioff()
        plt.style.use('dark_background')

    def initialize_widgets(self):
        """Initializes all needed widgets for the page."""
        self.grid_top = tk.Frame(self)

        self.label_title = tk.Label(self.grid_top, text="Image Comparison", font=("Arial", 20, 'bold'), fg="white",
                                    bg="#7695e3")
        self.label1 = tk.Label(self.grid_top, text="Select first fits-image")
        self.entry_browse1 = tk.Entry(self.grid_top, state="normal")
        self.button_browse1 = tk.Button(self.grid_top, text="Browse...", command=self.load_fits_file_1, state="normal")

        self.button_popup_help_comparison = tk.Button(self.grid_top, text="?",
                                                      command=self.popup.popup_window_comparison, width=4)

        self.label2 = tk.Label(self.grid_top, text="Select second fits-image")
        self.entry_browse2 = tk.Entry(self.grid_top, state="normal")
        self.button_browse2 = tk.Button(self.grid_top, text="Browse...", command=self.load_fits_file_2, state="normal")

        self.button_show1 = tk.Button(self.grid_top, text="Show Image", command=self.display_image1, state="disabled")
        self.button_show2 = tk.Button(self.grid_top, text="Show Image", command=self.display_image2, state="disabled")

        self.label_compare = tk.Label(self.grid_top, text="Comparing the two images")
        self.button_compare = tk.Button(self.grid_top, text="Compare Images", command=self.compare_images,
                                        state="disabled")

    def layout_widgets(self):
        """Displays and layouts the widgets in the correct places."""
        self.label_title.grid(row=0, column=0, columnspan=100, sticky="nesw")
        self.button_popup_help_comparison.grid(row=1, column=99, sticky='e', padx=(10, 10), pady=(10, 0))

        self.label1.grid(row=2, column=1, sticky="nesw", pady=(10, 0))
        self.entry_browse1.grid(row=2, column=2, sticky="nesw", pady=(10, 0))
        self.button_browse1.grid(row=2, column=3, sticky="nesw", pady=(10, 0))
        self.button_show1.grid(row=3, column=2, sticky="nesw")

        self.label2.grid(row=4, column=1, sticky="nesw", pady=(20, 0))
        self.entry_browse2.grid(row=4, column=2, sticky="nesw", pady=(20, 0))
        self.button_browse2.grid(row=4, column=3, sticky="nesw", pady=(20, 0))
        self.button_show2.grid(row=5, column=2, sticky="nesw")

        self.label_compare.grid(row=6, column=1, sticky="nesw", pady=(20, 0))
        self.button_compare.grid(row=6, column=2, sticky="nesw", pady=(20, 0))

        self.grid_top.grid_columnconfigure(0, weight=1)
        self.grid_top.grid_columnconfigure(99, weight=1)
        self.grid_top.pack(anchor="n", fill="x", expand=True)

    def load_fits_file_1(self):
        """Loads first fits-file for comparing two CASA images."""
        self.filename1 = tkFileDialog.askopenfilename(parent=self, initialdir=os.getcwd(),
                                                      title="Select First Fits-Image",
                                                      filetypes=(("fits files", "*.fits"),))
        self.master.lift()
        self.master.attributes('-topmost', False)
        self.entry_browse1.delete(0, tk.END)
        self.entry_browse1.insert(0, self.filename1)
        if self.filename1:
            self.fits_file1 = fits.open(self.filename1)
            self.button_show1.configure(state="normal")
            self.loaded_fits1 = True
            self.activate_compare_button()

    def load_fits_file_2(self):
        """Loads second fits-file for comparing two CASA images."""
        self.filename2 = tkFileDialog.askopenfilename(parent=self, initialdir=os.getcwd(),
                                                      title="Select Second Fits-Image",
                                                      filetypes=(("fits files", "*.fits"),))
        self.master.lift()
        self.master.attributes('-topmost', False)
        self.entry_browse2.delete(0, tk.END)
        self.entry_browse2.insert(0, self.filename2)
        if self.filename2:
            self.fits_file2 = fits.open(self.filename2)
            self.button_show2.configure(state="normal")
            self.loaded_fits2 = True
            self.activate_compare_button()

    def display_image1(self):
        """Displays the first image plots."""
        self.fig1 = create_comparison_plot(self.fits_file1, os.path.split(self.filename1)[1])
        self.fig1.show()

    def display_image2(self):
        """Displays the second image plots."""
        self.fig2 = create_comparison_plot(self.fits_file2, os.path.split(self.filename2)[1])
        self.fig2.show()

    def activate_compare_button(self):
        """Displays the button for comparison."""
        if self.loaded_fits1 and self.loaded_fits2:
            self.button_compare.configure(state="normal")

    def compare_images(self):
        """
        Compares the given and valid fits-files. Calculates the first image minus the second image and calls method
        to create the comparison plot
        """
        valid, error_messages = check_fits_files(self.fits_file1, self.fits_file2)
        if not valid:
            error_string = "Not possible to compare images:"
            for msg in error_messages:
                error_string = error_string + "\n" + msg
            tkMessageBox.showerror("Invalid Folder", error_string, parent=self)
            return

        residual = np.array(self.fits_file1[0].data).squeeze() - np.array(self.fits_file2[0].data).squeeze()
        hdu = fits.PrimaryHDU(residual)
        fig_residual = create_comparison_plot([hdu], "Residual of " + os.path.split(self.filename1)[1] + " - \n" +
                                              os.path.split(self.filename2)[1])
        fig_residual.show()


def check_fits_files(fits1, fits2):
    """
    Checks if the given two fits-files are valid for comparison.

    :param fits1: The first fits-file
    :param fits2: The second fits-file
    :return: valid, error_message: Boolean if valid with error message
    """
    valid = True
    error_messages = []

    header1 = fits1[0].header
    data1 = np.array(fits1[0].data).squeeze()
    b_unit1 = header1["BUNIT"]
    if not b_unit1:
        b_unit1 = "None"

    header2 = fits2[0].header
    data2 = np.array(fits2[0].data).squeeze()
    b_unit2 = header2["BUNIT"]
    if not b_unit2:
        b_unit2 = "None"

    if not data1.shape == data2.shape:
        error_messages.append("- Shapes of the images are not equal. \nShape image1: " + str(data1.shape) +
                              "\nShape image2: " + str(data2.shape))
        valid = False
    if not b_unit1 == b_unit2:
        error_messages.append("- Brightness (pixel) unit  of the images are not equal. \nUnit image1: " + b_unit1 +
                              "\nUnit image2: " + b_unit2)
        valid = False
    return valid, error_messages
