import tkinter as tk
from tkinter import ttk
from .widgets import create_mode_frame, create_path_frame, create_options_frame, create_filter_frame
from .widgets import create_tree_frame, create_button_frame
from .handlers import FileHandler

class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate File Finder")
        self.root.geometry("800x800")

        # Variables
        self.setup_variables()
        
        # File Handler
        self.file_handler = FileHandler(self)
        
        # Create GUI
        self.create_widgets()

    def setup_variables(self):
        self.master_path = tk.StringVar()
        self.removable_path = tk.StringVar()
        self.mode = tk.StringVar(value="single")
        self.include_subdirs = tk.BooleanVar(value=True)
        self.match_name = tk.BooleanVar(value=True)
        self.match_size = tk.BooleanVar(value=True)
        self.match_date = tk.BooleanVar(value=False)
        self.move_to_trash = tk.BooleanVar(value=True)
        self._last_sort = None
        
        # Filter activation variables
        self.use_filename_filter = tk.BooleanVar(value=False)
        self.use_directory_filter = tk.BooleanVar(value=False)
        self.use_date_filter = tk.BooleanVar(value=False)

    def create_widgets(self):
        self.mode_frame = create_mode_frame(self)
        self.path_frame = create_path_frame(self)
        self.options_frame = create_options_frame(self)
        self.filter_frame = create_filter_frame(self)
        self.tree_frame, self.tree = create_tree_frame(self)
        self.button_frame = create_button_frame(self)
