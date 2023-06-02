import os

def get_folder_path():
    """
    Ask the user to input the main folder path where all the data are saved.
    If no input is provided, a default folder path is used.

    Returns:
    - The user-provided folder path if it's valid.
    - None if the folder path is invalid.
    """
    # Prompt user for folder path
    user_input = input("Enter the data folder path (or press Enter for default): ")

    # Check if user input is empty
    if not user_input:
        # Assign a default or standard path
        folder_path = "C:/Users/fturi/Desktop/Dati"
    else:
        folder_path = user_input

    # Validate the folder path
    if os.path.isdir(folder_path):
        return folder_path
    else:
        print("Invalid folder path!")
        return None

main_data_folder=get_folder_path()

import tkinter as tk
import os


def browse_files(folder_path):
    selected_files = []  # Array to store selected file paths

    def browse_directory(path):
        nonlocal current_path
        nonlocal selected_files
        current_path = path
        entry.delete(0, tk.END)  # Clear the entry field
        entry.insert(tk.END, current_path)  # Update the entry field with the current path

        listbox.delete(0, tk.END)  # Clear the listbox

        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                listbox.insert(tk.END, "[D] " + item)  # Prefix subfolders with "[D]"
            else:
                listbox.insert(tk.END, "[F] " + item)  # Prefix files with "[F]"

    def select_item(event):
        selection = listbox.curselection()
        if selection:
            selected_item = listbox.get(selection[0])
            item_name = selected_item[4:]  # Remove the "[D] " or "[F] " prefix
            item_path = os.path.join(current_path, item_name)
            if os.path.isfile(item_path):
                if item_path not in selected_files:
                    selected_files.append(item_path)

    def go_inside():
        selection = listbox.curselection()
        if selection:
            selected_item = listbox.get(selection[0])
            item_name = selected_item[4:]  # Remove the "[D] " or "[F] " prefix
            item_path = os.path.join(current_path, item_name)
            if os.path.isdir(item_path):
                browse_directory(item_path)

    def go_back():
        parent_path = os.path.dirname(current_path)
        browse_directory(parent_path)

    def stop_browsing():
        print("Selected Files:")
        for file_path in selected_files:
            print(file_path)
        root.quit()

    root = tk.Tk()
    root.title("File Browser")

    # Path Entry Field
    entry = tk.Entry(root, width=50)
    entry.pack()

    # File Listbox
    listbox = tk.Listbox(root, width=100, height=20)
    listbox.pack()
    listbox.bind("<<ListboxSelect>>", select_item)

    # Buttons Frame
    buttons_frame = tk.Frame(root)
    buttons_frame.pack()

    # Add File Button
    add_button = tk.Button(buttons_frame, text="Add File", command=select_item)
    add_button.pack(side=tk.LEFT)

    # Go Inside Button
    go_inside_button = tk.Button(buttons_frame, text="Go Inside", command=go_inside)
    go_inside_button.pack(side=tk.LEFT)

    # Back Button
    back_button = tk.Button(buttons_frame, text="Go Back", command=go_back)
    back_button.pack(side=tk.LEFT)

    # Stop Button
    stop_button = tk.Button(buttons_frame, text="Stop and Print", command=stop_browsing)
    stop_button.pack(side=tk.LEFT)

    # Initial browsing
    current_path = folder_path
    browse_directory(folder_path)

    root.mainloop()

    return selected_files



file_paths = browse_files(main_data_folder)

print("Selected Files:")
for file_path in file_paths:
    print(file_path)