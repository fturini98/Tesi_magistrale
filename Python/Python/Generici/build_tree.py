from browse_and_choose_file_paths import *
from tkinter import ttk
import pandasgui
import pandas as pd
import re

file_paths=['C:/Users/fturi/Desktop/Dati/Test/tools-isocrone-out/RID_Z0.00163_He0.2504_ML1.90_55555555_AS09a0.DAT/AOUT_M0.83_Z0.00163_He0.2504_ML1.90_55555555_AS09a0.DAT']
folder_paths=['C:/Users/fturi/Desktop/Dati/Test/tools-driver-out/M0.76_Z0.00135_He0.2499_ML1.90_55555555_AS09a0', 'C:/Users/fturi/Desktop/Dati/Test/tools-isocrone-out/ISO_Z0.00135_He0.2499_ML1.90_55555555_AS09a0.DAT', 'C:/Users/fturi/Desktop/Dati/Test/tools-isocrone-out/RID_Z0.00135_He0.2499_ML1.90_55555555_AS09a0.DAT']

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
    sub_files = os.listdir(folder_path)
    for sub_file in sub_files:
        if sub_file.endswith(".DAT"):
            file_path = folder_path + "/" + sub_file
            file_paths.append(file_path)
    return file_paths


def build_tree_from_paths(file_paths, common_path):
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
            
            #check if the component of the path is a RID folder
            if component.startswith("RID"):
                #find and extract the metallicity value
                matches = re.match(r"RID_(Z[\d.]+_He[\d.]+_ML[\d.]+)_", component)
                
                z_he__mx = matches.group(1)

                #if the RID branch is't alredy created it will create
                if "RID" not in current_node:
                    current_node["RID"]={}
                
                #move to the RID branch
                current_node=current_node["RID"]
                
                #cerate the matallicity branch if it not exist
                if z_he__mx not in current_node:
                        current_node[z_he__mx] = {}
                
                #move to the metallicity branch
                current_node=current_node[z_he__mx]
            
            #manage the folder inside the tools/driver/out folder
            elif component.startswith("M"):
                #create the RAW branch if it isn't already present, this is done for having the same deepnes for all dataframes
                if "RAW" not in current_node:
                    current_node["RAW"]={}
                
                #Move to the RAW node
                current_node=current_node["RAW"]
                
                #extract the value of metallicty and Helium etc...
                matches = re.match(r"M([\d.]+)_(Z[\d.]+_He[\d.]+_ML[\d.]+)_", component)
                
                Mass_value="M"+matches.group(1)
                z_he__mx = matches.group(2)
                
                #cerate the matallicity branch if it not exist
                if z_he__mx not in current_node:
                        current_node[z_he__mx] = {}
                
                #move to the metallicity branch
                current_node=current_node[z_he__mx]
                
                #create the mass branch if it not exist
                if Mass_value not in current_node:
                        current_node[Mass_value] = {}
              
            #Load the RID.dat as dataframe with their specific formattation.    
            elif i == len(components) - 1 and component.endswith(".DAT") and component.startswith("AOUT"):
                
                #Extract the mass value
                matches = re.match(r"AOUT_(M[\d.]+)", component)
                
                Mass_value=matches.groups(1)
                
                # Define the variable/column names
                variable_names = ['MOD', 'Time', 'LOG_L/Lo', 'LOG_TE_(K)', 'M', '[Fe/H]', 'R', 'logg', 'Dni', 'nimax']
    
                # Read the data from the file into a dataframe
                df = pd.read_csv(path, comment='#', delimiter='\s+', header=None, engine='python')
    
                # Assign the variable/column names to the dataframe columns
                df.columns = variable_names
                
                current_node[Mass_value] = df
            
            #Load the raw file.dat as dataframe with their specific formattation.
            elif i == len(components) - 1 and component.endswith(".DAT") and component.startswith("OUT"):
                # Define the variable/column names
                variable_names = ["NMOD","LOG(T)","H/HE","LOG L","LOG TE","MASS","L-GRA","L-3A","log(Fe/H)","[Fe/H]","R","Logg","Dni","nimax","Mix_Len"]
    
                # Read the data from the file into a dataframe
                df = pd.read_csv(path, comment='#', delimiter='\s+', header=None, engine='python')

                # Assign the variable/column names to the dataframe columns
                df.columns = variable_names
                
                #In difference from the RID file there the leaf is alredy created, and the program remeber the mass value from the procedure of creating the branch from the folder name.
                #So the only thing to do is to link the dataframe at the leaf address.
                current_node[Mass_value] = df 
            
            if not component.startswith("RID") and not component.startswith("AOUT") and not component.startswith("M") and not component.startswith("OUT") :
                #ceck if the component branch exist if not it will create
                if component not in current_node:
                    current_node[component] = {}
                #move tho the branch just created
                current_node = current_node[component]

    return tree


def browse_tree(tree):
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

    root = tk.Tk()
    root.title("Tree Browser")

    treeview = ttk.Treeview(root)
    treeview.pack(expand=True, fill="both")

    populate_treeview("", tree)

    treeview.bind("<<TreeviewSelect>>", on_tree_select)

    root.mainloop()


def manage_folder(folder_paths, file_paths):
    for folder_path in folder_paths:
        folder_name = os.path.basename(folder_path)

        # Manage the tools-driver-out
        if folder_name == "tools-driver-out":
            sub_folders = os.listdir(folder_path)
            for sub_folder in sub_folders:
                # Generate the path of the sub folder
                sub_folder_path = folder_path + "/" + sub_folder
                # Generate the path of the only one file of interest in that folder
                file_dat_path = sub_folder_path + "/OUT.DAT"
                file_paths.append(file_dat_path)

        # Manage the Mass folder inside the tools-driver-out
        if folder_name.startswith("M"):
            file_paths.append(folder_path + "/OUT.DAT")

        # Manage the ISO folders
        if folder_name.startswith("ISO"):
            print("\033[31mISO folders are not implemented. Excluding:", folder_name, "\033[0m")

        # Manage the RID folders
        if folder_name.startswith("RID"):
            file_paths = manage_RID_folders(folder_path, file_paths)

        # Manage the tools-isocrone-out
        if folder_name == "tools-isocrone-out":
            sub_folders = os.listdir(folder_path)
            for sub_folder in sub_folders:
                if sub_folder.startswith("RID"):
                    sub_folder_path = folder_path + "/" + sub_folder
                    file_paths = manage_RID_folders(sub_folder_path, file_paths)

    return file_paths


def gen_tree(file_paths, folder_paths):
    
    common_path = extract_root_path_and_name(file_paths, folder_paths)

    file_paths = manage_folder(folder_paths, file_paths)

    tree = build_tree_from_paths(file_paths, common_path)
    return tree


tree = gen_tree(file_paths, folder_paths)
test=tree["Test"]["tools-driver-out"]["RAW"]["Z0.00135_He0.2499_ML1.90"]["M0.76"]["LOG(T)"]
#print(test)
browse_tree(tree)