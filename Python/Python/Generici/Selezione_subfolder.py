import os
import tkinter as tk
from tkinter import messagebox

# Set the path to your folder
folder_path = "C:/Users/fturi/Desktop/Test/tools-isocrone-out"

# Get a list of all the subfolders starting with "RID"
subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f)) and f.startswith("RID")]

# Create a Tkinter window
window = tk.Tk()

# Set the window title
window.title("Select Subfolder")

# Create a variable to store the selected subfolder path
selected_subfolder_path = tk.StringVar()

# Function to handle the confirm button click event
def confirm_selection():
    selected_subfolder = selected_subfolder_path.get()
    if selected_subfolder:
        selected_subfolder_path.set(os.path.join(folder_path, selected_subfolder))
        window.quit()
    else:
        messagebox.showwarning("Warning", "Please select a subfolder.")

# Create a dropdown widget to choose the subfolder
subfolder_label = tk.Label(window, text="Subfolder:")
subfolder_label.pack()

subfolder_dropdown = tk.OptionMenu(window, selected_subfolder_path, *subfolders)
subfolder_dropdown.pack()

# Create a confirm button
confirm_button = tk.Button(window, text="Confirm", command=confirm_selection)
confirm_button.pack()

# Run the Tkinter event loop
window.mainloop()

# Get the selected subfolder path
selected_subfolder_path = selected_subfolder_path.get()

selected_subfolder_path=selected_subfolder_path.replace("\\","/")

# Print the selected subfolder path
print("Selected subfolder:", selected_subfolder_path)

# Continue with the rest of your code using the selected subfolder
