from IPython.display import clear_output
from tkinter import ttk
import threading
import time
#import pandasgui
from build_tree import *
from browse_and_choose_file_paths import *


#Section of the code for load or create the tree, on dependence what the user choose

def choose_open_or_create_tree():
    while True:
        user_input= input("\033[34mDo you want load trees or create a new one?(create=c/load=l)\033[0m ")
        choice=user_input.lower()
        if choice in ["q","quit"]:
            print("\033[31mProgram stopped.\033[0m")
            # Perform any necessary cleanup or additional actions before exiting
            sys.exit(0)
        elif choice in ["c","create"]:
            return "create"
        elif choice in ["l","load"]:
            return "load"
        else:
            print("\033[33mInvalid choice! Please try again.\033[0m")

def load_trees(tree_paths):
    trees={}
    for tree_path in tree_paths:
        tree,tree_name=load_tree_from_path(tree_path)
        trees[tree_name]=tree
    
    #create a branch for saving all the trees paths
    trees["paths"]=tree_paths
    
    return trees

def browse_load_trees(data_folder_paths):
    
    tree_paths=jupyter_choose_tree_paths(data_folder_paths)
    trees=load_trees(tree_paths)
    
    return trees

def tree_call(standard_data_folder="C:/Users/fturi/Desktop/Dati"):
    data_folder_path=get_main_data_folder_path(standard_data_folder)
    user_choice=choose_open_or_create_tree()
    if user_choice=="create":
        file_paths,folder_paths=jupyter_choose_file_paths(data_folder_path)
        tree=generate_tree(file_paths,folder_paths)
        print("\033[32mTree created\033[0m")
        save_tree_with_shell(tree,standard_data_folder)
        while True:
            user_input=input("\033[34mDo you want use this tree or others?(this= Enter/ others=o)\033[0m ")
            if not user_input:
                return tree
            elif user_input.lower() in ["n","no"]:
                print("\033[31m Program stopped!\033[0m")
                sys.exit(0)
            elif user_input.lower() in ["other","others","o"]:
                trees=browse_load_trees(standard_data_folder)
                print("\033[32mTrees loaded \033[0m")
                return trees
            else:
                print("\033[33mInvalid choice! Please try again.\033[0m")
    else:
        trees=browse_load_trees(standard_data_folder)
        print("\033[32mTrees loaded \033[0m")
        return trees

#Section of the code for show the tree structure and work on it

def simple_browse(tree,root=None):
    if root==None:
        root=tk.Tk()
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

#Section for porting the program to the jupyter notebook

#Function whith gui and return
def jupyter_run_gui_function(tkinter_function, callback, *args, **kwargs):
    """
    Run a tkinter function in a separate thread within a Jupyter Notebook.

    Parameters:
        tkinter_function (callable): The tkinter function to run.
        callback (callable): The callback function to store the result.
        *args: Variable length argument list to be passed to the tkinter function.
        **kwargs: Arbitrary keyword arguments to be passed to the tkinter function.

    Returns:
        None
    """
    # Clear the current output in the Jupyter Notebook cell
    clear_output(wait=True)
    
    # Create a separate thread to run the tkinter function
    def thread_func():
        root = kwargs.get('root', tk.Tk())
        
        # This is needed if you call the interactive function multiple times
        root.protocol("WM_DELETE_WINDOW", root.destroy)  # Handle window close event
        result = tkinter_function(root=root, *args, **kwargs)
        root.mainloop()
        
        # Invoke the callback function with the result
        callback(result)
    
    # Create a separate thread to run the tkinter function
    thread = threading.Thread(target=thread_func)
    thread.start()

def jupyter_choose_file_paths(data_folder_path):
    file_paths = []
    folder_paths = []
    result_holder = {'file_paths': file_paths, 'folder_paths': folder_paths}
    thread_event = threading.Event()
    
    def store_paths(selected_file_paths, selected_folder_paths):
        result_holder['file_paths'] = selected_file_paths
        result_holder['folder_paths'] = selected_folder_paths
        thread_event.set()  # Set the event to indicate that the thread has finished
    
    def choose_file_paths_wrapper(root=None):
        # Call the choose_file_paths function and store the result
        selected_file_paths, selected_folder_paths = choose_file_paths(data_folder_path, root=root)
        if not thread_event.is_set():  # Check if the event has been set (window closed)
            store_paths(selected_file_paths, selected_folder_paths)
    
    # Run the GUI function in a separate thread
    thread = threading.Thread(target=choose_file_paths_wrapper)
    thread.start()
    
    # Wait for the thread to finish or the window to be closed
    while thread.is_alive() and not thread_event.is_set():
        time.sleep(0.1)
    
    # Check if the window was closed before the thread finished
    if not thread_event.is_set():
        thread.join()  # Ensure the thread is terminated
        #Because the window was running in a separated tread the call to the exit inside the choose_file_paths hasn't stopped the program, so you mast call it another time.
        #You want to stop the progam if the file_paths and folders_paths are empty.
        if not result_holder['file_paths'] and not result_holder['folder_paths']:
            sys.exit(0)
    
    # Return the result
    return result_holder['file_paths'], result_holder['folder_paths']

def jupyter_choose_tree_paths(data_folder_path):
    tree_paths = []
    result_holder = {'tree_paths': tree_paths}
    thread_event = threading.Event()
    
    def store_paths(selected_tree_paths):
        result_holder['tree_paths'] = selected_tree_paths
        thread_event.set()  # Set the event to indicate that the thread has finished
    
    def choose_file_paths_wrapper(root=None):
        # Call the choose_file_paths function and store the result
        selected_tree_paths= browse_and_select_trees(data_folder_path, root=root)
        if not thread_event.is_set():  # Check if the event has been set (window closed)
            store_paths(selected_tree_paths)
    
    # Run the GUI function in a separate thread
    thread = threading.Thread(target=choose_file_paths_wrapper)
    thread.start()
    
    # Wait for the thread to finish or the window to be closed
    while thread.is_alive() and not thread_event.is_set():
        time.sleep(0.1)
    
    # Check if the window was closed before the thread finished
    if not thread_event.is_set():
        thread.join()  # Ensure the thread is terminated
        #Because the window was running in a separated tread the call to the exit inside the choose_file_paths hasn't stopped the program, so you mast call it another time.
        #You want to stop the progam if the file_paths and folders_paths are empty.
        if not result_holder['tree_paths']:
            sys.exit(0)
    
    # Return the result
    return result_holder['tree_paths']


#Function whitout return
def jupyter_run_gui_function_whitout_return(tkinter_function, *args, **kwargs):
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

def jupyter_simple_browse(tree):
    jupyter_run_gui_function_whitout_return(simple_browse,tree)


