import json
import re
import threading
import pandas as pd
#import pandasgui
from IPython.display import clear_output
from tkinter import ttk
from browse_and_choose_file_paths import *


#file_paths=['C:/Users/fturi/Desktop/Dati/Test/tools-isocrone-out/RID_Z0.00163_He0.2504_ML1.90_55555555_AS09a0.DAT/AOUT_M0.83_Z0.00163_He0.2504_ML1.90_55555555_AS09a0.DAT']
folder_paths=['C:/Users/fturi/Desktop/Dati/Test/tools-driver-out/M0.76_Z0.00135_He0.2499_ML1.90_55555555_AS09a0', 'C:/Users/fturi/Desktop/Dati/Test/tools-isocrone-out/ISO_Z0.00135_He0.2499_ML1.90_55555555_AS09a0.DAT', 'C:/Users/fturi/Desktop/Dati/Test/tools-isocrone-out/RID_Z0.00135_He0.2499_ML1.90_55555555_AS09a0.DAT']
#folder_paths=[]
file_paths=[]

#Section of code for managing the files and folders paths and generate the data tree with the function gen_tree().

def extract_root_path_and_name(file_paths, folder_paths):
    """
    Extracts the common root path from the given file and folder paths.

    Args:
        file_paths (list): List of file paths.
        folder_paths (list): List of folder paths.

    Returns:
        string: A string containing the common root path.
    """
    # Get the common path
    common_path = os.path.commonpath(file_paths + folder_paths)

    return common_path

def manage_RID_folders(folder_path, file_paths):
    """
    Retrieves the file paths of DAT files within a specified folder and its subfolders.
    And append it to the list of files path.
    
    Args:
        folder_path (str): The path to the folder to search for DAT files.
        file_paths (list): A list to store the file paths of the DAT files.

    Returns:
        list: The updating list containing also the file paths of the DAT files found within the folder and its subfolders.
    """

    # Retrieve the list of files within the folder path
    sub_files = os.listdir(folder_path)

    # Iterate over each file in the list
    for sub_file in sub_files:
        # Check if the file has a ".DAT" extension
        if sub_file.endswith(".DAT"):
            # Construct the full file path
            file_path = folder_path + "/" + sub_file
            # Append the file path to the file_paths list
            file_paths.append(file_path)

    # Return the updated file_paths list
    return file_paths

def manage_folder(folder_paths, file_paths):
    """
    Manages the folder paths and generates a list of file paths of interest.

    The function processes the given folder paths and extracts relevant file paths based on specific conditions of formattation of the data file provided by FRANEC program.

    Args:
        folder_paths (list): A list of folder paths to be processed.
        file_paths (list): A list to store the file paths of interest.

    Returns:
        list: A list containing the file paths of interest.
    """

    for folder_path in folder_paths:
        folder_name = os.path.basename(folder_path)

        # Manage the tools-driver-out folder
        if folder_name == "tools-driver-out":
            sub_folders = os.listdir(folder_path)
            for sub_folder in sub_folders:
                # Generate the path of the sub folder
                sub_folder_path = folder_path + "/" + sub_folder
                # Generate the path of the only one file of interest in that folder
                file_dat_path = sub_folder_path + "/OUT.DAT"
                file_paths.append(file_dat_path)

        # Manage the Mass folder inside the tools-driver-out folder
        elif folder_name.startswith("M"):
            file_paths.append(folder_path + "/OUT.DAT")

        # Manage the ISO folders
        elif folder_name.startswith("ISO"):
            print("\033[31mISO folders are not implemented. Excluding:", folder_name, "\033[0m")

        # Manage the RID folders
        elif folder_name.startswith("RID"):
            file_paths = manage_RID_folders(folder_path, file_paths)

        # Manage the tools-isocrone-out folder
        elif folder_name == "tools-isocrone-out":
            sub_folders = os.listdir(folder_path)
            for sub_folder in sub_folders:
                if sub_folder.startswith("RID"):
                    sub_folder_path = folder_path + "/" + sub_folder
                    file_paths = manage_RID_folders(sub_folder_path, file_paths)
        
        #Manage the folders that aren't tools-isocrone-out or tools-driver-out
        else:
            print("\033[33m\ The biggests folders that i can manage are tools-isocrone-out and tools-driver-out.Excluding from the tree:",folder_name,"\033[0m")

    return file_paths

def build_tree_from_paths(file_paths, common_path):
    """
    Builds a hierarchical tree structure from a list of file paths.

    The function analyzes the file paths, extracts relevant information, and organizes it into a tree-like structure.

    The tree structure is organized for having at the same level the branch of "tools-driver-out" and "tools-isocrone-out", inside thath
    there are three sub branchs, RAW, RID and ISO (thath must be implemented).
    Inside of this three branchs, there are the branch of the metallictys and iside there, there are the pandas dataframe divide for each mass.
    
    Args:
        file_paths (list): A list of file paths to be processed.
        common_path (str): The common path shared by all the file paths.

    Returns:
        dict: A hierarchical tree structure representing the organization of the file paths.
    """

    tree = {}

    # Adjust the format of the common folder path
    common_path = os.path.dirname(common_path) + "/"
    common_path = common_path.replace("\\", "/")
       
    for path in file_paths:

        # Remove the common folder path
        rel_path = path.replace(common_path, "", 1)

        components = rel_path.split("/")  # Adjust the delimiter as per your file system

        current_node = tree
        for i, component in enumerate(components):

            # Check if the component of the path is a RID folder
            if component.startswith("RID"):
                # Find and extract the metallicity value
                matches = re.match(r"RID_(Z[\d.]+_He[\d.]+_ML[\d.]+)_", component)
                
                z_he__mx = matches.group(1)

                # If the RID branch doesn't already exist, create it
                if "RID" not in current_node:
                    current_node["RID"] = {}

                # Move to the RID branch
                current_node = current_node["RID"]

                # Create the metallicity branch if it doesn't exist
                if z_he__mx not in current_node:
                    current_node[z_he__mx] = {}

                # Move to the metallicity branch
                current_node = current_node[z_he__mx]

            # Manage the folder inside the tools/driver/out folder
            elif component.startswith("M"):
                # Create the RAW branch if it isn't already present, this is done to have the same depth for all dataframes
                if "RAW" not in current_node:
                    current_node["RAW"] = {}

                # Move to the RAW node
                current_node = current_node["RAW"]

                # Extract the value of metallicty and Helium, etc.
                matches = re.match(r"M([\d.]+)_(Z[\d.]+_He[\d.]+_ML[\d.]+)_", component)
                
                Mass_value = "M" + matches.group(1)
                z_he__mx = matches.group(2)

                # Create the metallicity branch if it doesn't exist
                if z_he__mx not in current_node:
                    current_node[z_he__mx] = {}

                # Move to the metallicity branch
                current_node = current_node[z_he__mx]

                # Create the mass branch if it doesn't exist
                if Mass_value not in current_node:
                    current_node[Mass_value] = {}

            # Load the RID.dat as a dataframe with their specific formatting
            elif i == len(components) - 1 and component.endswith(".DAT") and component.startswith("AOUT"):
                # Extract the mass value
                matches = re.match(r"AOUT_(M[\d.]+)_", component)
                
                Mass_value = matches.group(1)

                # Define the variable/column names
                variable_names = ['MOD', 'Time', 'LOG_L/Lo', 'LOG_TE_(K)', 'M', '[Fe/H]', 'R', 'logg', 'Dni', 'nimax']

                # Read the data from the file into a dataframe
                df = pd.read_csv(path, comment='#', delimiter='\s+', header=None, engine='python')

                # Assign the variable/column names to the dataframe columns
                df.columns = variable_names

                current_node[Mass_value] = df

            # Load the raw file.dat as a dataframe with their specific formatting
            elif i == len(components) - 1 and component.endswith(".DAT") and component.startswith("OUT"):
                # Define the variable/column names
                variable_names = ["NMOD", "LOG(T)", "H/HE", "LOG L", "LOG TE", "MASS", "L-GRA", "L-3A", "log(Fe/H)", "[Fe/H]", "R", "Logg", "Dni", "nimax", "Mix_Len"]

                # Read the data from the file into a dataframe
                df = pd.read_csv(path, comment='#', delimiter='\s+', header=None, engine='python')

                # Assign the variable/column names to the dataframe columns
                df.columns = variable_names

                # In difference from the RID file, the leaf is already created, and the program remembers the mass value from the procedure of creating the branch from the folder name.
                # So the only thing to do is to link the dataframe at the leaf address.
                current_node[Mass_value] = df

            if not component.startswith("RID") and not component.startswith("AOUT") and not component.startswith("M") and not component.startswith("OUT"):
                # Check if the component branch exists; if not, create it
                if component not in current_node:
                    current_node[component] = {}
                # Move to the branch just created
                current_node = current_node[component]

    return tree

def gen_tree(file_paths, folder_paths):
    """
    Generates a hierarchical tree structure based on file paths and folder paths.

    The function extracts the common path, manages the folder paths, and builds a tree-like structure based on the file paths.

    Args:
        file_paths (list): A list of file paths to be processed.
        folder_paths (list): A list of folder paths to be processed.

    Returns:
        dict: A hierarchical tree structure representing the organization of the file paths.
    """

    common_path = extract_root_path_and_name(file_paths, folder_paths)

    # Manage the folder paths and generate the file paths of interest
    file_paths = manage_folder(folder_paths, file_paths)

    # Build the tree structure from the file paths
    tree = build_tree_from_paths(file_paths, common_path)
    
    return tree

#Section for implementing the saving and loading of trees

def save_tree_with_shell(tree, folder_path):
    save_tree = input("Do you want to save the tree? (y/n): ")
    if save_tree.lower() != "y":
        print("Tree not saved.")
        return

    file_name = input("Enter a file name: ")
    if not file_name:
        print("File name is empty. Tree not saved.")
        return

    # Create the DataTrees folder if it doesn't exist
    data_trees_folder = os.path.join(folder_path, "DataTrees")
    if not os.path.exists(data_trees_folder):
        os.makedirs(data_trees_folder)

    file_path = os.path.join(data_trees_folder, file_name)

    # Check if the file already exists
    while os.path.exists(file_path):
        overwrite = input("A file with the same name already exists. Do you want to overwrite it? (y/n): ")
        if overwrite.lower() == "y":
            break
        confirm = input("Do you want to choose a different file name? (y/n): ")
        if confirm.lower() != "y":
            print("Tree not saved. Exiting.")
            return
        file_name = input("Enter a different file name: ")
        if not file_name:
            print("File name is empty. Tree not saved.")
            return
        file_path = os.path.join(data_trees_folder, file_name)

    # Serialize the tree to JSON
    def serialize_tree(node):
        if isinstance(node, dict):
            return {k: serialize_tree(v) for k, v in node.items()}
        elif isinstance(node, pd.DataFrame):
            return {"type": "DataFrame", "data": node.to_dict(orient="split")}
        return node

    serialized_tree = serialize_tree(tree)

    # Save the serialized tree to a file
    with open(file_path, "w") as file:
        json.dump(serialized_tree, file)

    print(f"Tree saved to {file_path}")

def load_tree_from_file(folder_path, file_name):
    # Check if the DataTrees folder exists
    data_trees_folder = os.path.join(folder_path, "DataTrees")
    if not os.path.exists(data_trees_folder):
        raise FileNotFoundError("DataTrees folder does not exist in the specified path.")

    # Check if the file exists
    file_path = os.path.join(data_trees_folder, file_name)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The specified file '{file_name}' does not exist in the DataTrees folder.")

    # Load the serialized tree from the file
    with open(file_path, "r") as file:
        serialized_tree = json.load(file)

    # Deserialize the tree, including DataFrames
    def deserialize_tree(node):
        if isinstance(node, dict):
            if "type" in node and node["type"] == "DataFrame":
                # Convert the serialized DataFrame back to a DataFrame object
                data = node["data"]["data"]
                index = node["data"]["index"]
                columns = node["data"]["columns"]
                return pd.DataFrame(data, index=index, columns=columns)
            return {k: deserialize_tree(v) for k, v in node.items()}
        return node

    tree = deserialize_tree(serialized_tree)

    return tree

#Section of the code for show the tree structure and work on it

def simple_browse_tree(tree,root=tk.Tk()):
    node_dataframes = {}
    def on_tree_select(event):
        item = treeview.focus()
        node_id = treeview.item(item, "text")
        if node_id in node_dataframes:
            df = node_dataframes[node_id]
            #pandasgui.show(df)

    def populate_treeview(parent, node):
        for key, value in node.items():
            item = treeview.insert(parent, "end", text=key)
            if isinstance(value, pd.DataFrame):
                node_id = treeview.item(item, "text")
                node_dataframes[node_id] = value
            elif isinstance(value, dict):
                populate_treeview(item, value)

    #calling root=tk.Tk() is need it for porting to the jupyter function
    root.title("Tree Browser")

    treeview = ttk.Treeview(root)
    treeview.pack(expand=True, fill="both")

    populate_treeview("", tree)

    treeview.bind("<<TreeviewSelect>>", on_tree_select)

    root.mainloop()

#Section for porting the program to the jupyter notebook(remeber to execute the generation of the three only one time)

def jupyter_run_gui_function(tkinter_function, *args, **kwargs):
    """
    Run a tkinter function in a separate thread within a Jupyter Notebook.

    Parameters:
        tkinter_function (callable): The tkinter function to run.
        *args: Variable length argument list to be passed to the tkinter function.
        **kwargs: Arbitrary keyword arguments to be passed to the tkinter function.

    Returns:
        None
    """
    # Clear the current output in the Jupyter Notebook cell
    clear_output(wait=True)
    
    # Create a separate thread to run the tkinter function
    def thread_func():
        root = tk.Tk()
        
        #This is need it if you call the interactives function form multiple time, whitout this the kernell crash
        root.protocol("WM_DELETE_WINDOW", root.destroy)  # Handle window close event
        tkinter_function(root=root,*args, **kwargs)
        root.mainloop()
    
    # Create a separate thread to run the tkinter function
    thread = threading.Thread(target=thread_func)
    thread.start()

def jupyter_simple_browse_tree(tree):
    jupyter_run_gui_function(simple_browse_tree,tree)

#Tests


data_folder_path="C:/Users/fturi/Desktop/Dati"

#tree=load_tree_from_file(data_folder_path,"pippo")

#simple_browse_tree(tree)


#browse_tree(tree)
#save_tree_with_gui(tree,data_folder_path)
#tree_test=load_tree_from_file(data_folder_path,"tree_test5")
#browse_tree(tree_test)
