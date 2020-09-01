import Tkinter as tk

from UserInterface.mainview import MainView
from UserInterface.model import InputModel


class Controller:
    """
    This class starts the main application. It gets data from inputmodel and widgets from view.
    """

    def __init__(self, simobserve, simanalyze, imhead, exportfits):
        """
        This method will be called when an object of this class is instantiated. It initializes the model and the view
        :param simobserve: The CASA task simobserve.
        :param simanalyze: The CASA task simanalyze.
        :param imhead: The CASA task imhead.
        :param exportfits: The CASA task exportfits
        """
        self.root = tk.Tk()
        self.model = InputModel(simobserve, simanalyze, imhead, exportfits)
        self.view = MainView(self.model, self.root)
        self.view.pack(fill="both", expand=True)
        self.root.wm_geometry("850x750")
        self.root.minsize(700, 400)

    def run(self):
        """Runs the main application and shows title."""
        self.root.title("SATRO")
        self.root.mainloop()
