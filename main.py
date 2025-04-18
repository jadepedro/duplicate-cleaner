import tkinter as tk
from gui.app import DuplicateFinderApp

def main():
    root = tk.Tk()
    app = DuplicateFinderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
