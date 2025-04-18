import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import hashlib
from datetime import datetime
import shutil
import send2trash
from typing import List, Dict

class DuplicateFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate File Finder")
        self.root.geometry("800x600")

        # Variables
        self.master_path = tk.StringVar()
        self.removable_path = tk.StringVar()
        self.mode = tk.StringVar(value="single")
        self.include_subdirs = tk.BooleanVar(value=True)
        self.match_name = tk.BooleanVar(value=True)
        self.match_size = tk.BooleanVar(value=True)
        self.match_date = tk.BooleanVar(value=False)
        self.move_to_trash = tk.BooleanVar(value=True)
        
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
        options_frame = ttk.LabelFrame(self.root, text="Options", padding=5)
        options_frame.pack(fill='x', padx=5, pady=5)

        ttk.Checkbutton(options_frame, text="Include Subdirectories", 
                       variable=self.include_subdirs).pack(side='left', padx=5)
        ttk.Checkbutton(options_frame, text="Match Name", 
                       variable=self.match_name).pack(side='left', padx=5)
        ttk.Checkbutton(options_frame, text="Match Size", 
                       variable=self.match_size).pack(side='left', padx=5)
        ttk.Checkbutton(options_frame, text="Match Date", 
                       variable=self.match_date).pack(side='left', padx=5)

        # Results treeview
        self.tree = ttk.Treeview(self.root, columns=('select', 'name', 'path', 'size', 'date'), 
                                show='headings')
        self.tree.pack(fill='both', expand=True, padx=5, pady=5)

        self.tree.heading('select', text='Select')
        self.tree.heading('name', text='Name')
        self.tree.heading('path', text='Path')
        self.tree.heading('size', text='Size')
        self.tree.heading('date', text='Date Modified')

        self.tree.column('select', width=50)
        self.tree.column('name', width=200)
        self.tree.column('path', width=300)
        self.tree.column('size', width=100)
        self.tree.column('date', width=150)

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

            # Display results
            for file_info in duplicates:
                self.tree.insert('', 'end', values=(
                    False,
                    file_info['name'],
                    file_info['path'],
                    f"{file_info['size']:,} bytes",
                    file_info['date'].strftime('%Y-%m-%d %H:%M:%S')
                ))

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
