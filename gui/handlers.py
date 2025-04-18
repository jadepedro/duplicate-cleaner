from tkinter import filedialog, messagebox
import os
from datetime import datetime
import send2trash
import fnmatch
from typing import List, Dict
from .utils import get_file_hash
from pathlib import Path

class FileHandler:
    def __init__(self, app):
        self.app = app
        self._last_sort = None
        self.files_data = []

    def update_mode(self):
        """Update UI based on selected mode"""
        if self.app.mode.get() == "single":
            self.app.removable_entry.config(state='disabled')
            self.app.removable_button.config(state='disabled')
        else:
            self.app.removable_entry.config(state='normal')
            self.app.removable_button.config(state='normal')

    def browse_master(self):
        """Browse for master directory"""
        path = filedialog.askdirectory()
        if path:
            self.app.master_path.set(path)

    def browse_removable(self):
        """Browse for removable directory"""
        path = filedialog.askdirectory()
        if path:
            self.app.removable_path.set(path)

    def browse_filter_dir(self):
        """Browse for filter directory"""
        path = filedialog.askdirectory()
        if path:
            self.app.filter_directory.set(path)

    def get_file_info(self, filepath: str) -> Dict:
        """Get file information including hash"""
        try:
            # Convert to Path object and resolve to absolute path
            path = Path(filepath).resolve()
            stat = path.stat()
            return {
                'name': path.name,
                'path': str(path),
                'size': stat.st_size,
                'date': datetime.fromtimestamp(stat.st_mtime),
                'hash': get_file_hash(str(path))
            }
        except Exception as e:
            raise OSError(f"Error accessing file {filepath}: {str(e)}")

    def get_files(self, directory: str) -> List[Dict]:
        """Get all files in directory"""
        files = []
        try:
            # Convert to Path object
            dir_path = Path(directory).resolve()
            
            if self.app.include_subdirs.get():
                # Use rglob for recursive search
                file_paths = dir_path.rglob('*')
            else:
                # Use glob for single directory
                file_paths = dir_path.glob('*')

            # Filter for files only (exclude directories)
            file_paths = [f for f in file_paths if f.is_file()]
            
            for filepath in file_paths:
                try:
                    files.append(self.get_file_info(str(filepath)))
                except (OSError, PermissionError) as e:
                    # Log the error but continue processing
                    print(f"Error processing {filepath}: {str(e)}")
                    continue
                    
        except Exception as e:
            messagebox.showerror("Error", f"Error accessing directory {directory}: {str(e)}")
            
        return files

    def is_duplicate(self, file1: Dict, file2: Dict) -> bool:
        """Check if files are duplicates based on selected criteria"""
        if self.app.match_name.get() and file1['name'] != file2['name']:
            return False
        if self.app.match_size.get() and file1['size'] != file2['size']:
            return False
        if self.app.match_date.get() and abs((file1['date'] - file2['date']).total_seconds()) > 1:
            return False
        return file1['hash'] == file2['hash']

    def search(self):
        """Search for duplicate files"""
        if not self.app.master_path.get():
            messagebox.showerror("Error", "Please select master directory")
            return

        if self.app.mode.get() == "master" and not self.app.removable_path.get():
            messagebox.showerror("Error", "Please select removable directory")
            return

        # Clear previous results
        for item in self.app.tree.get_children():
            self.app.tree.delete(item)

        try:
            self.app.root.config(cursor="wait")
            self.app.root.update()

            master_files = self.get_files(self.app.master_path.get())
            
            if self.app.mode.get() == "single":
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
                removable_files = self.get_files(self.app.removable_path.get())
                duplicates = [
                    removable_file for removable_file in removable_files
                    if any(self.is_duplicate(master_file, removable_file) 
                          for master_file in master_files)
                ]

            # Display results
            for file_info in duplicates:
                item = self.app.tree.insert('', 'end', values=(
                    False,
                    file_info['name'],
                    file_info['path'],
                    f"{file_info['size']:,} bytes",
                    file_info['date'].strftime('%Y-%m-%d %H:%M:%S')
                ))
                self.app.tree.item(item, tags=('unchecked',))

        finally:
            self.app.root.config(cursor="")

    def apply_selection_filters(self):
        """Apply filters to select files"""
        for item in self.app.tree.get_children():
            values = self.app.tree.item(item)['values']
            file_info = {
                'name': values[1],
                'path': values[2],
                'size': int(values[3].split()[0].replace(',', '')),
                'date': datetime.strptime(values[4], '%Y-%m-%d %H:%M:%S')
            }
            
            should_select = True
            
            # Apply filename filter
            if self.app.use_filename_filter.get() and self.app.filename_pattern.get():
                if not fnmatch.fnmatch(file_info['name'], self.app.filename_pattern.get()):
                    should_select = False

            # Apply directory filter
            if self.app.use_directory_filter.get() and self.app.filter_directory.get():
                if not file_info['path'].startswith(self.app.filter_directory.get()):
                    should_select = False

            # Apply date filter
            if self.app.use_date_filter.get():
                from_date = self.app.date_from.get().strip()
                to_date = self.app.date_to.get().strip()
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
            self.app.tree.set(item, 'select', should_select)
            self.app.tree.item(item, tags=('checked' if should_select else 'unchecked',))

    def reset_selection(self):
        """Reset all selections to unchecked"""
        for item in self.app.tree.get_children():
            self.app.tree.set(item, 'select', False)
            self.app.tree.item(item, tags=('unchecked',))

    def select_all(self):
        """Select all files in the list"""
        for item in self.app.tree.get_children():
            self.app.tree.set(item, 'select', True)
            self.app.tree.item(item, tags=('checked',))

    def toggle_checkbox(self, event):
        """Handle checkbox toggle in treeview"""
        region = self.app.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.app.tree.identify_column(event.x)
            if column == '#1':  # Select column
                item = self.app.tree.identify_row(event.y)
                if item:
                    current_val = self.app.tree.set(item, 'select')
                    new_val = not bool(current_val)
                    self.app.tree.set(item, 'select', new_val)
                    self.app.tree.item(item, tags=('checked' if new_val else 'unchecked',))
                    return "break"  # Prevent default handling

    def sort_treeview(self, col):
        """Sort treeview content when header is clicked"""
        items = [(self.app.tree.set(item, col), item) for item in self.app.tree.get_children('')]
        
        # Determine sort order
        reverse = False
        if self._last_sort == (col, False):
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
            self.app.tree.move(item, '', index)

    def delete_selected(self):
        """Delete selected files"""
        selected = [
            self.app.tree.item(item)['values'][2]  # Get file path
            for item in self.app.tree.get_children()
            if self.app.tree.item(item)['values'][0]  # Check if selected
        ]

        if not selected:
            messagebox.showinfo("Info", "No files selected")
            return

        if not messagebox.askyesno("Confirm", f"Delete {len(selected)} files?"):
            return

        log_file = f"delete_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        for filepath in selected:
            try:
                # Convert to Path object and resolve to absolute path
                path = Path(filepath).resolve()
                
                if self.app.move_to_trash.get():
                    try:
                        send2trash.send2trash(str(path))
                        action = "Moved to trash"
                    except Exception as trash_error:
                        # If send2trash fails, try direct deletion
                        os.remove(str(path))
                        action = "Deleted (fallback)"
                else:
                    os.remove(str(path))
                    action = "Deleted"
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.now()}: {action} - {path}\n")
                    
            except Exception as e:
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{datetime.now()}: Error processing {filepath} - {str(e)}\n")
                messagebox.showerror("Error", f"Could not process file:\n{filepath}\n\nError: {str(e)}")

        # Refresh the display
        self.search()
