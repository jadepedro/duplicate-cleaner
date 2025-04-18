import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import hashlib
from datetime import datetime
import send2trash
from typing import List, Dict
import fnmatch
from tkcalendar import DateEntry

class DuplicateFinderApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate File Finder")
        self.root.geometry("800x800")  # Increased height to accommodate filters

        # Variables
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
        
        self.create_widgets()
        self.files_data = []

    def create_widgets(self):
        # Mode selection
        mode_frame = ttk.LabelFrame(self.root, text="Mode", padding=5)
        mode_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Radiobutton(mode_frame, text="Single Directory", 
                       variable=self.mode, value="single",
                       command=self.update_mode).pack(side='left', padx=5)
        ttk.Radiobutton(mode_frame, text="Master and Removable", 
                       variable=self.mode, value="master",
                       command=self.update_mode).pack(side='left', padx=5)

        # Path selection
        path_frame = ttk.LabelFrame(self.root, text="Directories", padding=5)
        path_frame.pack(fill='x', padx=5, pady=5)

        # Master directory
        ttk.Label(path_frame, text="Master Directory:").grid(row=0, column=0, sticky='w')
        ttk.Entry(path_frame, textvariable=self.master_path).grid(row=0, column=1, sticky='ew')
        ttk.Button(path_frame, text="Browse", command=self.browse_master).grid(row=0, column=2, padx=5)

        # Removable directory
        ttk.Label(path_frame, text="Removable Directory:").grid(row=1, column=0, sticky='w')
        self.removable_entry = ttk.Entry(path_frame, textvariable=self.removable_path)
        self.removable_entry.grid(row=1, column=1, sticky='ew')
        self.removable_button = ttk.Button(path_frame, text="Browse", command=self.browse_removable)
        self.removable_button.grid(row=1, column=2, padx=5)
        
        path_frame.grid_columnconfigure(1, weight=1)

        # Options
        options_frame = ttk.LabelFrame(self.root, text="Match Options", padding=5)
        options_frame.pack(fill='x', padx=5, pady=5)

        ttk.Checkbutton(options_frame, text="Include Subdirectories", 
                       variable=self.include_subdirs).pack(side='left', padx=5)
        ttk.Checkbutton(options_frame, text="Match Name", 
                       variable=self.match_name).pack(side='left', padx=5)
        ttk.Checkbutton(options_frame, text="Match Size", 
                       variable=self.match_size).pack(side='left', padx=5)
        ttk.Checkbutton(options_frame, text="Match Date", 
                       variable=self.match_date).pack(side='left', padx=5)

        # Filter frame
        filter_frame = ttk.LabelFrame(self.root, text="Selection Filters", padding=5)
        filter_frame.pack(fill='x', padx=5, pady=5)

        # Filename filter
        ttk.Checkbutton(filter_frame, text="Use filename filter:", 
                       variable=self.use_filename_filter).grid(row=0, column=0, sticky='w')
        self.filename_pattern = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.filename_pattern).grid(row=0, column=1, sticky='ew')
        ttk.Label(filter_frame, text="(e.g., *.txt, doc*.*)").grid(row=0, column=2, sticky='w')

        # Directory filter
        ttk.Checkbutton(filter_frame, text="Use directory filter:", 
                       variable=self.use_directory_filter).grid(row=1, column=0, sticky='w')
        self.filter_directory = tk.StringVar()
        ttk.Entry(filter_frame, textvariable=self.filter_directory).grid(row=1, column=1, sticky='ew')
        ttk.Button(filter_frame, text="Browse", command=self.browse_filter_dir).grid(row=1, column=2)

        # Date range filter
        ttk.Checkbutton(filter_frame, text="Use date filter:", 
                       variable=self.use_date_filter).grid(row=2, column=0, sticky='w')
        date_frame = ttk.Frame(filter_frame)
        date_frame.grid(row=2, column=1, columnspan=2, sticky='w')
        
        self.date_from = ttk.Entry(date_frame, width=12)
        self.date_from.grid(row=0, column=0, padx=5)
        ttk.Label(date_frame, text="to").grid(row=0, column=1, padx=5)
        self.date_to = ttk.Entry(date_frame, width=12)
        self.date_to.grid(row=0, column=2, padx=5)
        ttk.Label(date_frame, text="(YYYY-MM-DD)").grid(row=0, column=3, padx=5)

        # Filter buttons
        filter_buttons_frame = ttk.Frame(filter_frame)
        filter_buttons_frame.grid(row=3, column=0, columnspan=3, pady=5)
        ttk.Button(filter_buttons_frame, text="Apply Filters", 
                  command=self.apply_selection_filters).pack(side='left', padx=5)
        ttk.Button(filter_buttons_frame, text="Reset Selection", 
                  command=self.reset_selection).pack(side='left', padx=5)

        filter_frame.grid_columnconfigure(1, weight=1)

        # Create frame for treeview and scrollbar
        tree_frame = ttk.Frame(self.root)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Results treeview
        self.tree = ttk.Treeview(tree_frame, columns=('select', 'name', 'path', 'size', 'date'), 
                                show='headings')
        
        # Add scrollbars
        yscroll = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        xscroll = ttk.Scrollbar(tree_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

        # Grid layout for treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        yscroll.grid(row=0, column=1, sticky='ns')
        xscroll.grid(row=1, column=0, sticky='ew')

        # Configure grid weights
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        # Configure columns and headings
        self.tree.heading('select', text='Select')
        for col in ('name', 'path', 'size', 'date'):
            self.tree.heading(col, text=col.title(),
                            command=lambda c=col: self.sort_treeview(c))

        self.tree.column('select', width=50, anchor='center')
        self.tree.column('name', width=200)
        self.tree.column('path', width=300)
        self.tree.column('size', width=100)
        self.tree.column('date', width=150)

        # Create checkboxes in the treeview
        self.tree.tag_configure('checked', image=self.create_checkbox(True))
        self.tree.tag_configure('unchecked', image=self.create_checkbox(False))

        # Bind checkbox click
        self.tree.bind('<Button-1>', self.toggle_checkbox)

        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(button_frame, text="Search", command=self.search).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Select All", command=self.select_all).pack(side='left', padx=5)
        ttk.Checkbutton(button_frame, text="Move to Trash", 
                       variable=self.move_to_trash).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Delete Selected", 
                  command=self.delete_selected).pack(side='left', padx=5)

        self.update_mode() 

    def create_checkbox(self, checked):
        """Create a checkbox image"""
        size = 20
        checkbox = tk.Canvas(self.root, width=size, height=size, highlightthickness=0)
        checkbox.create_rectangle(2, 2, size-2, size-2, outline='black')
        if checked:
            checkbox.create_line(4, size//2, size//2, size-4, width=2)
            checkbox.create_line(size//2, size-4, size-4, 4, width=2)
        return checkbox

    def apply_selection_filters(self):
        """Apply filters to select files"""
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            file_info = {
                'name': values[1],
                'path': values[2],
                'size': int(values[3].split()[0].replace(',', '')),
                'date': datetime.strptime(values[4], '%Y-%m-%d %H:%M:%S')
            }
            
            should_select = True
            
            # Apply filename filter
            if self.use_filename_filter.get() and self.filename_pattern.get():
                if not fnmatch.fnmatch(file_info['name'], self.filename_pattern.get()):
                    should_select = False

            # Apply directory filter
            if self.use_directory_filter.get() and self.filter_directory.get():
                if not file_info['path'].startswith(self.filter_directory.get()):
                    should_select = False

            # Apply date filter
            if self.use_date_filter.get():
                from_date = self.date_from.get().strip()
                to_date = self.date_to.get().strip()
                if from_date and to_date:
                    try:
                        from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
                        to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
                        file_date = file_info['date'].date()
                        if not (from_date <= file_date <= to_date):
                            should_select = False
                    except ValueError:
                        pass

            # Update selection
            self.tree.set(item, 'select', should_select)
            self.tree.item(item, tags=('checked' if should_select else 'unchecked',))

    def reset_selection(self):
        """Reset all selections to unchecked"""
        for item in self.tree.get_children():
            self.tree.set(item, 'select', False)
            self.tree.item(item, tags=('unchecked',))
    def update_mode(self):
        if self.mode.get() == "single":
            self.removable_entry.config(state='disabled')
            self.removable_button.config(state='disabled')
        else:
            self.removable_entry.config(state='normal')
            self.removable_button.config(state='normal')

    def browse_master(self):
        path = filedialog.askdirectory()
        if path:
            self.master_path.set(path)

    def browse_removable(self):
        path = filedialog.askdirectory()
        if path:
            self.removable_path.set(path)

    def browse_filter_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.filter_directory.set(path)

    def toggle_checkbox(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == '#1':  # Select column
                item = self.tree.identify_row(event.y)
                if item:
                    current_val = self.tree.set(item, 'select')
                    new_val = not bool(current_val)
                    self.tree.set(item, 'select', new_val)
                    self.tree.item(item, tags=('checked' if new_val else 'unchecked',))
                    return "break"  # Prevent default handling

    def sort_treeview(self, col):
        """Sort treeview content when header is clicked."""
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Determine sort order
        reverse = False
        if hasattr(self, '_last_sort') and self._last_sort == (col, False):
            reverse = True
        self._last_sort = (col, reverse)
        
        # Convert values for proper sorting
        if col == 'size':
            items = [(int(val.split()[0].replace(',', '')), item) for val, item in items]
        elif col == 'date':
            items = [(datetime.strptime(val, '%Y-%m-%d %H:%M:%S'), item) for val, item in items]
        
        # Sort items
        items.sort(reverse=reverse)
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)

    def get_file_hash(self, filepath: str) -> str:
        """Calculate MD5 hash of file."""
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            buf = f.read(65536)  # Read in 64kb chunks
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(65536)
        return hasher.hexdigest()

    def get_file_info(self, filepath: str) -> Dict:
        """Get file information."""
        stat = os.stat(filepath)
        return {
            'name': os.path.basename(filepath),
            'path': filepath,
            'size': stat.st_size,
            'date': datetime.fromtimestamp(stat.st_mtime),
            'hash': self.get_file_hash(filepath)
        }

    def is_duplicate(self, file1: Dict, file2: Dict) -> bool:
        """Check if files are duplicates based on selected criteria."""
        if self.match_name.get() and file1['name'] != file2['name']:
            return False
        if self.match_size.get() and file1['size'] != file2['size']:
            return False
        if self.match_date.get() and abs((file1['date'] - file2['date']).total_seconds()) > 1:
            return False
        return True

    def apply_filters(self, file_info: Dict) -> bool:
        """Apply all filters to a file."""
        # Filename pattern filter
        if self.filename_pattern.get():
            if not fnmatch.fnmatch(file_info['name'], self.filename_pattern.get()):
                return False

        # Directory filter
        if self.filter_directory.get():
            if not file_info['path'].startswith(self.filter_directory.get()):
                return False

        # Date range filter
        if self.date_from.get_date() and self.date_to.get_date():
            file_date = file_info['date'].date()
            if not (self.date_from.get_date() <= file_date <= self.date_to.get_date()):
                return False

        return True

    def get_files(self, directory: str) -> List[Dict]:
        """Get all files in directory."""
        files = []
        walk_fn = os.walk if self.include_subdirs.get() else lambda x: [(x, [], os.listdir(x))]
        
        for root, _, filenames in walk_fn(directory):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                try:
                    files.append(self.get_file_info(filepath))
                except (OSError, PermissionError):
                    continue
        return files

    def search(self):
        if not self.master_path.get():
            messagebox.showerror("Error", "Please select master directory")
            return

        if self.mode.get() == "master" and not self.removable_path.get():
            messagebox.showerror("Error", "Please select removable directory")
            return

        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.root.config(cursor="wait")
            self.root.update()

            master_files = self.get_files(self.master_path.get())
            
            if self.mode.get() == "single":
                # Find duplicates within single directory
                duplicates = []
                for i, file1 in enumerate(master_files):
                    for file2 in master_files[i+1:]:
                        if self.is_duplicate(file1, file2):
                            if file1 not in duplicates:
                                duplicates.append(file1)
                            if file2 not in duplicates:
                                duplicates.append(file2)
            else:
                # Find duplicates between master and removable
                removable_files = self.get_files(self.removable_path.get())
                duplicates = [
                    removable_file for removable_file in removable_files
                    if any(self.is_duplicate(master_file, removable_file) 
                          for master_file in master_files)
                ]

            # Apply filters and display results
            for file_info in duplicates:
                if self.apply_filters(file_info):
                    item = self.tree.insert('', 'end', values=(
                        False,
                        file_info['name'],
                        file_info['path'],
                        f"{file_info['size']:,} bytes",
                        file_info['date'].strftime('%Y-%m-%d %H:%M:%S')
                    ))
                    self.tree.item(item, tags=('unchecked',))

        finally:
            self.root.config(cursor="")

    def select_all(self):
        for item in self.tree.get_children():
            self.tree.set(item, 'select', True)

    def delete_selected(self):
        selected = [
            self.tree.item(item)['values'][2]  # Get file path
            for item in self.tree.get_children()
            if self.tree.item(item)['values'][0]  # Check if selected
        ]

        if not selected:
            messagebox.showinfo("Info", "No files selected")
            return

        if not messagebox.askyesno("Confirm", f"Delete {len(selected)} files?"):
            return

        log_file = f"delete_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        for filepath in selected:
            try:
                if self.move_to_trash.get():
                    send2trash.send2trash(filepath)
                    action = "Moved to trash"
                else:
                    os.remove(filepath)
                    action = "Deleted"
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.now()}: {action} - {filepath}\n")
                    
            except Exception as e:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.now()}: Error processing {filepath} - {str(e)}\n")

        # Refresh the display
        self.search()

def main():
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
