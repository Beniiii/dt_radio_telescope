import csv
import webbrowser
import Tkinter as tk
import numpy as np
import pandas as pd


def fill_treeview(treeview, dataframe):
    """
    Fills the table with items from given dataFrame

    :param treeview: tkinter table
    :param dataframe: pandas dataFrame
    """
    treeview.delete(*treeview.get_children())
    if not dataframe.empty:
        cols = list(dataframe.columns)
        treeview["columns"] = cols
        for col in cols:
            if len(cols) > 5:
                treeview.column(col, width=130, anchor="w", stretch=True)
            else:
                treeview.column(col, width=155, anchor="w", stretch=True)
            treeview.heading(col, text=col, anchor="w")

        for index, row in dataframe.iterrows():
            treeview.insert("", index, text=index, values=list(row))


def destroy_slaves(frame):
    """Destroys all widgets in a given frame

    :param frame: tkinter frame
    """
    for widget in frame.grid_slaves():
        widget.destroy()


def read_values_from_entry_table(grid, columns):
    """
    Creates dataFrame and fills it with given column headers. Reads values from given grid and appends it to
    created dataFrame.

    :param grid: tkinter grid
    :param columns: column headers for dataFrame
    :return: pandas dataFrame
    """
    cols = grid.grid_size()[0]
    rows = grid.grid_size()[1]
    df_columns = []
    df = pd.DataFrame(columns=columns)
    if rows != 0:
        for col in range(1, cols - 1):
            df_columns.append(grid.grid_slaves(0, col)[0].cget("text"))
        df = pd.DataFrame(columns=df_columns)

        for row in range(1, rows):
            df_row = {}
            for col in range(len(df_columns)):
                if col == 0:
                    df_row.update({df_columns[col]: grid.grid_slaves(row, col + 1)[0].cget("text")})
                else:
                    df_row.update({df_columns[col]: grid.grid_slaves(row, col + 1)[0].get()})
            df = df.append(df_row, ignore_index=True)
    return df


def read_fixed_params_from_file(csv_file, columns):
    """
     Reads fixed parameter values from csv-file and appends it to created dataFrame

    :param csv_file: csv-file
    :param columns: columns header for dataFrame
    :return:  pandas dataFrame
    """
    df = pd.DataFrame(columns=columns)
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            df = df.append(row, ignore_index=True)
    return df


def transform_to_number(string):
    """
    Transforms and returns a given string to either int or float.

    :param string: The input string.
    :return: number: The transformed number.
    """
    number = -1
    if string:
        if string.isdigit():
            number = int(string)
        else:
            number = float(string)
        return number


def create_param_values_list(min_value, max_value, steps, units):
    """
    Creates and returns a list of parameter values calculated from min to max
    with given amount of steps.

    :param min_value: The minimum value of the parameter.
    :param max_value: The maximum value of the parameter.
    :param steps: The amount of steps in between.
    :param units: The units added to the value.
    :return: values: A list of values for a parameter.
    """
    values = np.linspace(min_value, max_value, steps)

    if isinstance(min_value, int) and isinstance(max_value, int):
        values_int = []
        for value in values:
            values_int.append(int(value))
        values = values_int

    if units:
        values_str = []
        for value in values:
            values_str.append(str(value) + units)
        values = values_str
    return values


def create_entry_table(df, grid):
    """
    Creates labels and entries for alphabetic varying parameter from a DataFrame and displays them
    correctly in a grid.

    :param df: pandas DataFrame
    :param grid: tkinter Frame
    """
    label_header_name = tk.Label(grid, text="Name", borderwidth=1, relief="solid")
    label_header_value = tk.Label(grid, text="Value", borderwidth=1, relief="solid")
    label_header_units = tk.Label(grid, text="Units", borderwidth=1, relief="solid")

    label_header_name.grid(row=0, column=1, sticky="nesw")
    label_header_value.grid(row=0, column=2, sticky="nesw")
    label_header_units.grid(row=0, column=3, sticky="nesw")

    for index, row in df.iterrows():
        label_name = tk.Label(grid, text=row["Name"])
        entry_value = tk.Entry(grid)
        entry_units = tk.Entry(grid)

        entry_value.insert(0, row["Value"])
        entry_units.insert(0, row["Units"])

        label_name.grid(row=index + 1, column=1)
        entry_value.grid(row=index + 1, column=2)
        entry_units.grid(row=index + 1, column=3)


def calulate_estimated_time(integrations, imsize, sm_size, haslam, beam_size):
    """
    Calculates and returns estimated computation time for one iteration.

    :param integrations: The number of integrations.
    :param imsize: The size of the image.
    :param sm_size: The size of the sky-model image.
    :param haslam: Boolean if Haslam-Map is selected.
    :param beam_size: The beam size.
    :return: estimation: The estimated time in seconds.
    """
    haslam_time = 0
    interpolation_time = 0

    if haslam:
        haslam_time = 20
        if beam_size > 1:
            interpolation_time = 0.0004 * sm_size**2 - 0.02 * sm_size + 4

    integration_time = integrations / 30
    imsize_time = imsize * 0.04
    sm_size_time = sm_size * 0.03
    estimation = 20 + integration_time + imsize_time + sm_size_time + haslam_time + interpolation_time
    return estimation


def convert_time_to_string(time):
    """
    Converts time in seconds as float to a string in the format 2h 30min or "less than 1min" if time is smaller than
    30s and returns it.

    :param time: Time in seconds as float.
    :return: time_string: The time as string.
    """
    time_string = ""
    if time < 30:
        time_string = "less than 1min"
    else:
        minutes = time / 60
        if minutes > 60:
            hours = int(minutes / 60)
            rest = (minutes / 60 - hours) * 60
            minutes = int(round(rest))
            time_string = str(hours) + "h " + str(minutes) + "min"
        else:
            time_string = str(int(round(minutes))) + "min"
    return time_string


def open_manual():
    """Opens the user manual for the GUI."""
    webbrowser.open_new(r"user_manual.pdf")


def get_param_tags(csv_files):
    """Returns read parameters from csv.

    :param csv_files: the csv files
    :return: parameters: the read parameters
    """
    parameters = []
    for csv_file in csv_files:
        with open(csv_file, 'r') as param_file:
            reader = csv.DictReader(param_file)
            for parameter in reader.fieldnames:
                parameters.append(parameter)
    return parameters


def load_table_from_df(table, df):
    """
    Fills a tables widgets with values from the dataframe. The dataframe must not be of smaller shape than the table.

    :param table: The table to fill, tkinter frame object.
    :param df: The pandas dataframe object to take data from.
    """
    for index, row in df.iterrows():
        for col in range(1, len(df.columns)):
            entry = table.grid_slaves(row=index + 1, column=col + 1)[0]
            entry.delete(0, tk.END)
            entry.insert(0, row[col])
