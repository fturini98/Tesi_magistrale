import tkinter as tk
import os
import sys

def get_main_data_folder_path(data_folder_path="C:/Users/fturi/Desktop/Dati"):
    """
    Prompts the user to input the main folder path where all the data are saved.

    If no input is provided, a default folder path is used.
    If the user inputs 'quit' or 'q', the program stops.
    If the folder path is invalid, the user is prompted to input a valid path.

    Returns:
    - The user-provided folder path if it's valid.
    - None if the program is stopped or the folder path is invalid.
    """
    while True:
        # Prompt user for folder path
        user_input = input("\033[34mEnter the data folder path (or press Enter for default), 'quit' or 'q' to stop:\033[0m ")

        # Check if user wants to quit
        if user_input.lower() in ["quit", "q"]:
            print("\033[31mProgram stopped.\033[0m")
            # Perform any necessary cleanup or additional actions before exiting(the sys library is for working on jupyter)
            sys.exit(0)

        # Check if user input is empty
        if not user_input:
            # Assign a default or standard path
            folder_path = data_folder_path
        else:
            folder_path = user_input

        # Validate the folder path
        if os.path.isdir(folder_path):
            return folder_path
        else:
            print("\033[33mInvalid folder path! Please try again.\033[0m")

def browse_and_select_files(folder_path,root=None):
    """Browse and select files and folders from a specified folder path.

    This function provides a file browsing interface that allows the user to browse and select files and folders from a specified folder path. The selected files and folders are stored in separate lists and returned at the end of the browsing session.

    Args:
        folder_path (str): The path of the folder to browse.

    Returns:
        tuple: A tuple containing two lists. The first list contains the selected file paths, and the second list contains the selected folder paths.
    """

    selected_files = []  # Array to store selected file paths
    selected_folders = [] # Array to store selected folder paths

    def browse_directory(path):
        """Browse the specified directory and populate the file listbox with its contents.

        This function is called when browsing a directory. It takes a path as input and populates the file listbox with the contents of the directory. The function updates the current_path variable and displays the path in the entry field.

        Args:
            path (str): The path of the directory to browse.

        Returns:
            None
        """
        nonlocal current_path
        nonlocal selected_files
        nonlocal selected_folders
        current_path = path
        entry.delete(0, tk.END)  # Clear the entry field
        entry.insert(tk.END, current_path)  # Update the entry field with the current path

        listbox.delete(0, tk.END)  # Clear the listbox

        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                item_signature = "[D] "
                if item_path in selected_folders:
                    item_signature += "[X] "
                listbox.insert(tk.END, item_signature + item)  # Prefix subfolders with "[D]"
            else:
                item_signature = "[F] "
                if item_path in selected_files:
                    item_signature += "[X] "
                listbox.insert(tk.END, item_signature + item)  # Prefix files with "[F]"

    def add_item():
        """Add the selected item to the selected files or folders list.

        This function is called when the user clicks the "Add File" button in the file browsing interface. It retrieves the selected item from the listbox, adds the corresponding file or folder to the selected files or folders list, and updates the listbox by marking the item as selected.

        Returns:
            None
        """
        selection = listbox.curselection()
        if selection:
            selected_item = listbox.get(selection[0])
            item_name = selected_item[4:]  # Remove the "[D] " or "[F] " prefix
            item_path = os.path.join(current_path, item_name)
            if os.path.isfile(item_path):
                if "[X] " in item_name:
                    item_name = item_name.replace("[X] ", "")  # Remove "[X]" from the item name
                if item_path not in selected_files:
                    selected_files.append(item_path)
                    selected_item = selected_item[:4] + "[X] " + item_name  # Add "[X]" immediately after "[F]"
                    listbox.delete(selection[0])
                    listbox.insert(selection[0], selected_item)  # Update the listbox item
            elif os.path.isdir(item_path):
                if "[X] " in item_name:
                    item_name = item_name.replace("[X] ", "")  # Remove "[X]" from the item name
                if item_path not in selected_folders:
                    selected_folders.append(item_path)
                    selected_item = selected_item[:4] + "[X] " + item_name  # Add "[X]" immediately after "[D]"
                    listbox.delete(selection[0])
                    listbox.insert(selection[0], selected_item)  # Update the listbox item
    
    def remove_item():
        """Remove the selected item from the listbox and the corresponding file or folder from the selected files or folders list.

        This function is called when the user clicks the "Remove File" button in the file browsing interface. It retrieves the selected item from the listbox, removes the corresponding file or folder from the selected files or folders list, and updates the listbox by removing the item from the display.

        Returns:
         None
        """
        selection = listbox.curselection()
        if selection:
            selected_item = listbox.get(selection[0])
            
            item_name=selected_item.replace("[X] ","") # Remove the "[X] " prefix
            item_name = item_name[4:]  # Remove the "[D] " or "[F] " prefix
            
            item_path = os.path.join(current_path, item_name)
            item_signature = ""  # Initialize item_signature
            if os.path.isfile(item_path):
                if item_path in selected_files:
                    selected_files.remove(item_path)
                item_signature = "[F] "  # Set item_signature for files
            elif os.path.isdir(item_path):
                if item_path in selected_folders:
                    selected_folders.remove(item_path)
                item_signature = "[D] "  # Set item_signature for folders
            selected_item = item_signature + item_name  # Recreate the item with the correct signature
            listbox.delete(selection[0])
            listbox.insert(selection[0], selected_item)  # Update the listbox item
    
    def go_inside(event):
        """Browse inside the selected folder when double-clicked.

        This function is called when the user double-clicks on a folder item in the file listbox. It retrieves the selected folder item, removes any selection marker from its name, and browses inside the selected folder.

        Args:
            event: The event object triggered by the double-click action.

        Returns:
            None
        """
        selection = listbox.curselection()
        if selection:
            selected_item = listbox.get(selection[0])
            item_name = selected_item[4:]  # Remove the "[D] " or "[F] " prefix
            if "[X] " in item_name:
                    item_name = item_name.replace("[X] ", "")  # Remove "[X]" from the item name
            item_path = os.path.join(current_path, item_name)
            if os.path.isdir(item_path):
                browse_directory(item_path)

    def go_back():
        """Browse back to the parent directory.

        This function is called when the user clicks the "Go Back" button in the file browsing interface. It retrieves the parent path of the current directory and browses to that directory.

        Returns:
            None
        """
        if current_path == folder_path:
            print("Already at the start folder.")
        else:
            parent_path = os.path.dirname(current_path)
            browse_directory(parent_path)

    def stop_browsing():
        """Stop browsing and print the selected files and folders.

        This function is called when the user clicks the "Stop and Print" button in the file browsing interface. 
        It checks if any files or folders have been selected and prints the selected files and folders to the console.(this part is disabled)
        The function then terminates the browsing session.

        Returns:
            None
        """
        if not selected_files and not selected_folders:
            print("\033[31mNo selected files or folders.Program stoped.\033[0m")
            sys.exit(0)
        '''
        else:
            if len(selected_files) > 3:
                print("Selected Files:")
                print(*selected_files[:2], sep="\n")  # Print first 2 files
                print("...")
                print(*selected_files[-1:], sep="\n")  # Print last file
            elif not selected_files:
                print("No selected files.")
            else:
                print("Selected Files:")
                print(*selected_files, sep="\n")

            if len(selected_folders) > 3:
                print("Selected Folders:")
                print(*selected_folders[:2], sep="\n")  # Print first 2 folders
                print("...")
                print(*selected_folders[-1:], sep="\n")  # Print last folder
            elif not selected_folders:
                print("No selected folders.")
            else:
                print("Selected Folders:")
                print(*selected_folders, sep="\n")
        '''   
        root.quit()

    if root==None:
        root = tk.Tk()
    root.title("Select data to analyzes")

    # Path Entry Field
    entry = tk.Entry(root, width=50)
    entry.pack()

    # File Listbox
    listbox = tk.Listbox(root, width=100, height=20)
    listbox.pack()
    #Bind of the action: for example ""<Double-Button-1>"" ensure that when there is a double click the function go_inside is call.
    listbox.bind("<Double-Button-1>", go_inside)

    # Buttons Frame positions
    buttons_frame_center = tk.Frame(root)
    buttons_frame_center.pack()
    
    buttons_frame_left= tk.Frame(root)
    buttons_frame_left.pack(side=tk.LEFT)
    
    buttons_frame_right= tk.Frame(root)
    buttons_frame_right.pack(side=tk.RIGHT)
    
    # Add File Button
    add_button = tk.Button(buttons_frame_center, text="Add File", command=add_item)
    add_button.pack()
    
    #Remove file Button
    add_button = tk.Button(buttons_frame_center, text="Remove File", command=remove_item)
    add_button.pack()

    # Back Button
    back_button = tk.Button(buttons_frame_left, text="Go Back", command=go_back)
    back_button.pack()

    # Stop Button
    stop_button = tk.Button(buttons_frame_right, text="Stop and Print", command=stop_browsing)
    stop_button.pack()

    # Initial browsing
    current_path = folder_path
    browse_directory(folder_path)

    root.mainloop()

    return selected_files,selected_folders

def choose_file_paths(main_data_folder_path,root=None):
    """
    Allows the user to select files and folders through browsing, removes nested paths, and returns the cleared file paths and parent folder paths.
    
    Args:
        main_data_folder_path (str): The path of the main data folder to browse.
    
    Returns:
        tuple: A tuple containing two lists - cleared_file_paths (list[str]): A list of cleared file paths that are not nested within any of the parent folder paths, and parent_folder_paths (list[str]): A list of parent folder paths without any nested folder paths.
    """
    
    #choose the files via browsing
    file_paths,folder_paths=browse_and_select_files(main_data_folder_path,root)
    
    #This handel if the window is closed whit the cross and not whit the button
    if not file_paths and not folder_paths:
            print("\033[31mNo selected files or folders.Program stoped.\033[0m")
            sys.exit(0)
    
    #Change the paths format for future use
    file_paths=[s.replace("\\", "/") for s in file_paths]
    folder_paths=[s.replace("\\", "/") for s in folder_paths]
    
    def are_paths_nested(path, parent_paths):
        """
        Check if a given path is nested within any of the parent paths.

        Args:
            path (str): The path to check.
            parent_paths (list[str]): A list of parent paths to compare against.

        Returns:
            bool: True if the path is nested within any of the parent paths, False otherwise.

        Example:
            >>> parent_paths = ['/home/user', '/var/log']
            >>> path = '/home/user/documents'
            >>> are_paths_nested(path, parent_paths)
            True
        """
        return any(not os.path.relpath(path, parent_path).startswith("..") for parent_path in parent_paths)

    def remove_innested_folder_paths(paths):
        """
        Remove nested folder paths from the given list of paths.

        Args:
            paths (list[str]): A list of paths to process.

        Returns:
            list[str]: A list of parent paths without any nested folder paths.

        Example:
            >>> paths = ['/var/log', '/var/log/messages', '/home/user', '/home/user/documents']
            >>> remove_innested_folder_paths(paths)
            ['/var/log', '/home/user']
        """
        # Sort the paths
        paths.sort()
    
        # Create a array to keep track of parent folders to return
        parent_paths = []
        for path in paths:
            if not are_paths_nested(path,parent_paths):
                parent_paths.append(path)
        return parent_paths
    
    def remove_innested_file_paths(parent_folder_paths,file_paths):
        """
        Removes nested file paths from the given list based on the parent folder paths.

        Args:
            parent_folder_paths (list): A list of parent folder paths.
            file_paths (list): A list of file paths.

        Returns:
            list: A list of cleared file paths that are not nested within any of the parent folder paths.
        """
        
        #create an arry for save the list of files thath are not in the folders
        cleared_file_paths=[]
        for path in file_paths:
            if not are_paths_nested(path,parent_folder_paths):
                cleared_file_paths.append(path)
        return cleared_file_paths
    
    #eliminate the mulitple files and folder
    parent_folder_paths=remove_innested_folder_paths(folder_paths)
    
    cleared_file_paths=remove_innested_file_paths(parent_folder_paths,file_paths)
    
    #print the cleared files and folders lists
    if len(parent_folder_paths) > 3:
        print("\033[32mEffective selected folders:\033[0m")
        print(*parent_folder_paths[:2], sep="\n")  # Print first 2 folders
        print("...")
        print(*parent_folder_paths[-1:], sep="\n")  # Print last folder
    elif not parent_folder_paths:
        print("\033[33mNo effective selected folders.\033[0m")
    else:
        print("\033[32mEffective selected folders:\033[0m")
        print(*parent_folder_paths, sep="\n")
    
    if len(cleared_file_paths) > 3:
        print("\033[32mEffective selected extra files:\033[0m")
        print(*cleared_file_paths[:2], sep="\n")  # Print first 2 files
        print("...")
        print(*cleared_file_paths[-1:], sep="\n")  # Print last file
    elif not cleared_file_paths:
       print("\033[33mNo selected extra file.\033[0m")
    else:
        print("\033[32mEffective selected extra files:\033[0m")
        print(*cleared_file_paths, sep="\n")
    
    return cleared_file_paths,parent_folder_paths

def browse_and_select_trees(standard_data_folder="C:/Users/fturi/Desktop/Dati",root=None):

    tree_folder=standard_data_folder+"/DataTrees"

    selected_trees=[]

    def browse_directory(path):
        """Browse the specified directory and populate the file listbox with its contents.

        This function is called when browsing a directory. It takes a path as input and populates the file listbox with the contents of the directory. The function updates the current_path variable and displays the path in the entry field.

        Args:
            path (str): The path of the directory to browse.

        Returns:
            None
        """
        nonlocal current_path
        nonlocal selected_trees
        current_path = path
        entry.delete(0, tk.END)  # Clear the entry field
        entry.insert(tk.END, current_path)  # Update the entry field with the current path

        listbox.delete(0, tk.END)  # Clear the listbox

        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                item_signature = "[F] "
                if item_path in selected_trees:
                    item_signature += "[X] "
                listbox.insert(tk.END, item_signature + item)  # Prefix files with "[F]"

    def on_double_click(event):
        selection = listbox.curselection()
        if selection:
            selected_item = listbox.get(selection[0])
            item_name = selected_item[4:]  # Remove the "[D] " or "[F] " prefix
            if "[X] " in item_name:
                item_name = item_name.replace("[X] ", "")  # Remove "[X]" from the item name
            item_path = os.path.join(current_path, item_name)
            if item_path in selected_trees:
                selected_trees.remove(item_path)
                selected_item = "[F] " + item_name  # Remove "[X]" from the item name
                listbox.delete(selection[0])
                listbox.insert(selection[0], selected_item)  # Update the listbox item
            else:
                selected_trees.append(item_path)
                selected_item = "[F] [X] " + item_name  # Add "[X]" immediately after "[F]"
                listbox.delete(selection[0])
                listbox.insert(selection[0], selected_item)  # Update the listbox item

    def stop_browsing():
        """Stop browsing and print the selected files and folders.

        This function is called when the user clicks the "Stop and Print" button in the file browsing interface. 
        It checks if any files or folders have been selected and prints the selected files and folders to the console.(this part is disabled)
        The function then terminates the browsing session.

        Returns:
            None
        """
        if not selected_trees:
            print("\033[31mNo selected trees or folders.Program stoped.\033[0m")
            sys.exit(0)
        
        root.quit()
                    
    if root==None:
        root = tk.Tk()
    root.title("Select trees to analyzes")

    # Path Entry Field
    entry = tk.Entry(root, width=50)
    entry.pack()

    # File Listbox
    listbox = tk.Listbox(root, width=100, height=20)
    listbox.pack()
    #Bind of the action: for example ""<Double-Button-1>"".
    listbox.bind("<Double-Button-1>", on_double_click)

    # Buttons Frame positions
    buttons_frame_center = tk.Frame(root)
    buttons_frame_center.pack()
    
    buttons_frame_left= tk.Frame(root)
    buttons_frame_left.pack(side=tk.LEFT)
    
    buttons_frame_right= tk.Frame(root)
    buttons_frame_right.pack(side=tk.RIGHT)
    

    # Stop Button
    stop_button = tk.Button(buttons_frame_right, text="Stop and Load", command=stop_browsing)
    stop_button.pack()

    # Initial browsing
    current_path = tree_folder
    browse_directory(tree_folder)

    root.mainloop()

    #Change the paths format for future use
    selected_trees=[s.replace("\\", "/") for s in selected_trees]
    return selected_trees

#main_data_folder=get_main_data_folder_path()
#test_file_paths,test_folder_paths = choose_file_paths(main_data_folder)
