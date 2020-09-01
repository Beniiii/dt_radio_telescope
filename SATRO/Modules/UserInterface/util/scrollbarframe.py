import Tkinter as tk


# Taken from here with some modifications:
# https://stackoverflow.com/questions/3085696/adding-a-scrollbar-to-a-group-of-widgets-in-tkinter/3092341#3092341
class ScrollbarFrame(tk.Frame):
    """
    Extends class tk.Frame to support a scrollable Frame
    This class is independent from the widgets to be scrolled and
    can be used to replace a standard tk.Frame
    """

    def __init__(self, parent, **kwargs):
        """
        This methods will be called when an object of this class is instantiated. It initializes variables and calls
        methods.

        :param args: arguments
        :param kwargs: keyword arguments
        """
        tk.Frame.__init__(self, parent, **kwargs)

        # The Scrollbar, layout to the right
        vsb = tk.Scrollbar(self, orient="vertical")
        vsb.pack(side="right", fill="y")

        # The Canvas which supports the Scrollbar Interface, layout to the left
        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")
        self.canvas.pack(side="top", fill="both", expand=True)

        # Bind the Scrollbar to the self.canvas Scrollbar Interface
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.configure(command=self.canvas.yview)

        # The Frame to be scrolled, layout into the canvas
        # All widgets to be scrolled have to use this Frame as parent
        self.scrolled_frame = tk.Frame(self.canvas, background=self.canvas.cget('bg'))
        self.canvas.create_window((0, 0), window=self.scrolled_frame, anchor="n", tags="frame")

        # Configures the scrollregion of the Canvas dynamically
        self.scrolled_frame.bind("<Configure>", self.on_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def on_configure(self, event):
        """Set the scroll region to encompass the scrolled frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """Set the scroll region to encompass the scrolled frame"""
        self.canvas.itemconfig('frame', width=self.canvas.winfo_width())
