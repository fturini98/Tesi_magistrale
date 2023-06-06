from browse_and_choose_file_paths import *
from tkinter import ttk
#import pandasgui
import pandas as pd

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
            if component not in current_node:
                current_node[component] = {}
            if i == len(components) - 1 and component.endswith(".DAT"):
                df = pd.read_csv(path)  # Adjust the delimiter as per your file format
                current_node[component] = df
            current_node = current_node[component]

    return tree


def browse_tree(tree):
    node_dataframes = {}
    def on_tree_select(event):
        item = treeview.focus()
        #node_id = treeview.item(item, "text")
        #if node_id in node_dataframes:
            #df = node_dataframes[node_id]
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

browse_tree(tree)