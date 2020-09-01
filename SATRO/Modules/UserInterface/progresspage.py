import Tkinter as tk


class ProgressPage(tk.Frame):
    """
    Subclass of tk.Frame. This class creates and layouts widgets for the third page of the GUI. This class shows a
    loading label until pipeline is finished.
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

        self.initialize_widgets()
        self.layout_widgets()

    def initialize_widgets(self):
        """Initializes all needed widgets for the page."""
        self.grid_progress = tk.Frame(self)
        self.label_title = tk.Label(self.grid_progress, text="Simulating radio observations...",
                                    font=("Arial", 20, 'bold'))
        self.label_info = tk.Label(self.grid_progress, text="Check console and the CASA logger for more details ",
                                   font=("Arial", 16))

    def layout_widgets(self):
        """Displays and layouts the widgets in the correct places."""
        self.grid_progress.grid_columnconfigure(0, weight=1)
        self.grid_progress.grid_columnconfigure(99, weight=1)
        self.label_title.grid(row=0, column=1, sticky="nesw")
        self.label_info.grid(row=1, column=1, sticky="nesw")

        self.grid_progress.pack(side="top", fill="both", expand=True, anchor="n")
