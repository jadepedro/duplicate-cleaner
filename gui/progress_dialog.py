import tkinter as tk
from tkinter import ttk
from typing import Callable
import queue

class ProgressDialog:
    def __init__(self, parent, title="Progress"):
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.transient(parent)
        self.top.grab_set()  # Make it modal
        
        # Center the dialog
        window_width = 500
        window_height = 200
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.top.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        self.queue = queue.Queue()
        self.cancelled = False
        self.create_widgets()
        
    def create_widgets(self):
        # Current folder frame
        folder_frame = ttk.LabelFrame(self.top, text="Current Location", padding=5)
        folder_frame.pack(fill='x', padx=5, pady=5)
        
        self.folder_label = ttk.Label(folder_frame, text="", wraplength=450)
        self.folder_label.pack(fill='x')
        
        self.file_label = ttk.Label(folder_frame, text="", wraplength=450)
        self.file_label.pack(fill='x')
        
        # Progress frame
        progress_frame = ttk.LabelFrame(self.top, text="Progress", padding=5)
        progress_frame.pack(fill='x', padx=5, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="Files matched: 0")
        self.progress_label.pack(fill='x')
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=5)
        self.progress_bar.start(10)
        
        # Cancel button
        self.cancel_button = ttk.Button(self.top, text="Cancel", command=self.cancel)
        self.cancel_button.pack(pady=10)
        
        # Start checking queue
        self.check_queue()
        
    def check_queue(self):
        """Check for updates in the queue"""
        try:
            while True:
                msg = self.queue.get_nowait()
                if msg is None:  # Signal to close
                    self.close()
                    return
                folder, filename, matches = msg
                self.folder_label.config(text=f"Folder: {folder}")
                self.file_label.config(text=f"File: {filename}")
                self.progress_label.config(text=f"Files matched: {matches}")
        except queue.Empty:
            if not self.cancelled:
                self.top.after(100, self.check_queue)
    
    def update(self, folder: str, filename: str, matches: int):
        """Queue an update to the dialog"""
        self.queue.put((folder, filename, matches))
        
    def cancel(self):
        """Handle cancel button click"""
        self.cancelled = True
        self.cancel_button.config(state='disabled')
        
    def close(self):
        """Close the dialog"""
        self.top.grab_release()
        self.top.destroy()
