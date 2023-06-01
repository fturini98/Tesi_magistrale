import pandas as pd
import numpy as np
import re

def get_second_row_length(file_path):
    """
    Read the second row of a .dat file using read_csv() and return its length.

    Args:
        file_path (str): The path to the .dat file.

    Returns:
        int: The length of the second row.
    """

    # Read the .dat file using read_csv() and skip the first row
    data = pd.read_csv(file_path, sep='\s+', header=None, skiprows=[0])

    # Get the second row and calculate its length
    second_row_length = len(data.iloc[0])

    return second_row_length

def check_and_append_array_length(file_path, name_array):
    """
    Compare the length of an array with the length of the second row of a .dat file.
    If the lengths are unequal, append the number of columns from the second row to the array.

    Args:
        file_path (str): The path to the .dat file.
        data_array (list): The array to be checked and modified.

    Returns:
        list: The modified array.
    """

    # Read the .dat file and get the length of the second row
    second_row_length = get_second_row_length(file_path)

    # Compare the lengths of the array and the second row
    if len(name_array) < second_row_length:
        num_columns_to_append = second_row_length - len(name_array)
        appended_columns = [f"Var_{i}" for i in range(num_columns_to_append)]
        name_array.extend(appended_columns)

    return name_array

def names_of_variables(file_path):
    """
    Read the first row of a file, split it into an array using a minimum double space as delimiter,
    and replace spaces with underscores in each element of the array.

    Args:
        file_path (str): The path to the file.

    Returns:
        list: The modified array of column names.
    """

    # Read the first row of the file
    with open(file_path, 'r') as file:
        first_row = file.readline().strip()

    # Convert the string into an array using a minimum double space as delimiter
    output_array = re.split(r'\s{2,}', first_row)

    # Replace spaces with underscores in each element of the array using a list comprehension
    output_array = [element.replace(' ', '_') for element in output_array]
    
    #Check if all the variables are named and else give a "Var_i" name to each one
    output_array=check_and_append_array_length(file_path,output_array)

    return output_array


def read_data(file_path):
    """
    Read a CSV file, skip the first line, and assign specific column names.

    Args:
        file_path (str): The path to the CSV file.

    Returns:
        pandas.DataFrame: The DataFrame containing the data.
    """

    
    # Read the CSV file skipping the first line and using specified column names
    data = pd.read_csv(file_path, delimiter='\s+', header=None, skiprows=1)
    data.columns=names_of_variables(file_path)

    return data