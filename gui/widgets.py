import tkinter as tk
from tkinter import ttk
from .utils import create_checkbox

def create_mode_frame(app):
    frame = ttk.LabelFrame(app.root, text="Mode", padding=5)
    frame.pack(fill='x', padx=5, pady=5)
    
    ttk.Radiobutton(frame, text="Single Directory", 
                   variable=app.mode, value="single",
                   command=app.file_handler.update_mode).pack(side='left', padx=5)
    ttk.Radiobutton(frame, text="Master and Removable", 
                   variable=app.mode, value="master",
                   command=app.file_handler.update_mode).pack(side='left', padx=5)
    return frame

def create_path_frame(app):
    frame = ttk.LabelFrame(app.root, text="Directories", padding=5)
    frame.pack(fill='x', padx=5, pady=5)

    # Master directory
    ttk.Label(frame, text="Master Directory:").grid(row=0, column=0, sticky='w')
    ttk.Entry(frame, textvariable=app.master_path).grid(row=0, column=1, sticky='ew')
    ttk.Button(frame, text="Browse", 
              command=app.file_handler.browse_master).grid(row=0, column=2, padx=5)

    # Removable directory
    ttk.Label(frame, text="Removable Directory:").grid(row=1, column=0, sticky='w')
    app.removable_entry = ttk.Entry(frame, textvariable=app.removable_path)
    app.removable_entry.grid(row=1, column=1, sticky='ew')
    app.removable_button = ttk.Button(frame, text="Browse", 
                                    command=app.file_handler.browse_removable)
    app.removable_button.grid(row=1, column=2, padx=5)
    
    frame.grid_columnconfigure(1, weight=1)
    return frame

def create_options_frame(app):
    frame = ttk.LabelFrame(app.root, text="Match Options", padding=5)
    frame.pack(fill='x', padx=5, pady=5)

    ttk.Checkbutton(frame, text="Include Subdirectories", 
                   variable=app.include_subdirs).pack(side='left', padx=5)
    ttk.Checkbutton(frame, text="Match Name", 
                   variable=app.match_name).pack(side='left', padx=5)
    ttk.Checkbutton(frame, text="Match Size", 
                   variable=app.match_size).pack(side='left', padx=5)
    ttk.Checkbutton(frame, text="Match Date", 
                   variable=app.match_date).pack(side='left', padx=5)
    return frame

def create_filter_frame(app):
    frame = ttk.LabelFrame(app.root, text="Selection Filters", padding=5)
    frame.pack(fill='x', padx=5, pady=5)

    # Filename filter
    ttk.Checkbutton(frame, text="Use filename filter:", 
                   variable=app.use_filename_filter).grid(row=0, column=0, sticky='w')
    app.filename_pattern = tk.StringVar()
    ttk.Entry(frame, textvariable=app.filename_pattern).grid(row=0, column=1, sticky='ew')
    ttk.Label(frame, text="(e.g., *.txt, doc*.*)").grid(row=0, column=2, sticky='w')

    # Directory filter
    ttk.Checkbutton(frame, text="Use directory filter:", 
                   variable=app.use_directory_filter).grid(row=1, column=0, sticky='w')
    app.filter_directory = tk.StringVar()
    ttk.Entry(frame, textvariable=app.filter_directory).grid(row=1, column=1, sticky='ew')
    ttk.Button(frame, text="Browse", 
              command=app.file_handler.browse_filter_dir).grid(row=1, column=2)

    # Date range filter
    ttk.Checkbutton(frame, text="Use date filter:", 
                   variable=app.use_date_filter).grid(row=2, column=0, sticky='w')
    date_frame = ttk.Frame(frame)
    date_frame.grid(row=2, column=1, columnspan=2, sticky='w')
    
    app.date_from = ttk.Entry(date_frame, width=12)
    app.date_from.grid(row=0, column=0, padx=5)
    ttk.Label(date_frame, text="to").grid(row=0, column=1, padx=5)
    app.date_to = ttk.Entry(date_frame, width=12)
    app.date_to.grid(row=0, column=2, padx=5)
    ttk.Label(date_frame, text="(YYYY-MM-DD)").grid(row=0, column=3, padx=5)

    # Filter buttons
    filter_buttons_frame = ttk.Frame(frame)
    filter_buttons_frame.grid(row=3, column=0, columnspan=3, pady=5)
    ttk.Button(filter_buttons_frame, text="Apply Filters", 
              command=app.file_handler.apply_selection_filters).pack(side='left', padx=5)
    ttk.Button(filter_buttons_frame, text="Reset Selection", 
              command=app.file_handler.reset_selection).pack(side='left', padx=5)

    frame.grid_columnconfigure(1, weight=1)
    return frame

def create_tree_frame(app):
    frame = ttk.Frame(app.root)
    frame.pack(fill='both', expand=True, padx=5, pady=5)

    # Create treeview
    tree = ttk.Treeview(frame, columns=('select', 'name', 'path', 'size', 'date'), 
                        show='headings')
    
    # Add scrollbars
    yscroll = ttk.Scrollbar(frame, orient='vertical', command=tree.yview)
    xscroll = ttk.Scrollbar(frame, orient='horizontal', command=tree.xview)
    tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

    # Grid layout
    tree.grid(row=0, column=0, sticky='nsew')
    yscroll.grid(row=0, column=1, sticky='ns')
    xscroll.grid(row=1, column=0, sticky='ew')

    # Configure grid weights
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)

    # Configure columns and headings
    tree.heading('select', text='Select')
    for col in ('name', 'path', 'size', 'date'):
        tree.heading(col, text=col.title(),
                    command=lambda c=col: app.file_handler.sort_treeview(c))

    tree.column('select', width=50, anchor='center')
    tree.column('name', width=200)
    tree.column('path', width=300)
    tree.column('size', width=100)
    tree.column('date', width=150)

    # Configure checkbox images
    tree.tag_configure('checked', image=create_checkbox(True))
    tree.tag_configure('unchecked', image=create_checkbox(False))

    # Bind events
    tree.bind('<Button-1>', app.file_handler.toggle_checkbox)

    # Store tree reference in app
    app.tree = tree

    return frame, tree

def create_button_frame(app):
    frame = ttk.Frame(app.root)
    frame.pack(fill='x', padx=5, pady=5)

    ttk.Button(frame, text="Search", 
              command=app.file_handler.search).pack(side='left', padx=5)
    ttk.Button(frame, text="Select All", 
              command=app.file_handler.select_all).pack(side='left', padx=5)
    ttk.Checkbutton(frame, text="Move to Trash", 
                   variable=app.move_to_trash).pack(side='left', padx=5)
    ttk.Button(frame, text="Delete Selected", 
              command=app.file_handler.delete_selected).pack(side='left', padx=5)
    
    return frame
