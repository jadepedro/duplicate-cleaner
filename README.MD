# Duplicate File Finder

A Python application with a graphical user interface for finding and managing duplicate files across directories.

## Features

- **Two Operation Modes**:
  - Single Directory: Find duplicates within one directory
  - Master-Removable: Compare files between two directories

- **Flexible Matching Criteria**:
  - File name matching
  - File size comparison
  - Date modified comparison
  - Content hash comparison (MD5)

- **Advanced Filtering**:
  - Filename pattern filtering (e.g., *.txt, doc*.*)
  - Directory path filtering
  - Date range filtering

- **File Management**:
  - Option to move files to trash instead of permanent deletion
  - Detailed operation logging
  - Batch selection and deletion capabilities

- **User Interface Features**:
  - Progress tracking during search
  - Sortable results
  - Checkbox selection
  - Cancel operation support
  - Recursive subdirectory search option

## Requirements

- Python 3.7 or higher
- Required packages:


## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/duplicate-finder.git
cd duplicate-finder
```

2. Create and activate a virtual environment (optional but recommended):
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate

3. Install required packages:

pip install -r requirements.txt

## Projec Structure

duplicate_finder/
├── main.py                 # Application entry point
├── requirements.txt        # Project dependencies
├── gui/
│   ├── __init__.py
│   ├── app.py             # Main application window
│   ├── widgets.py         # UI components
│   ├── handlers.py        # Event handlers
│   ├── utils.py           # Utility functions
│   └── progress_dialog.py # Progress window

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
Uses send2trash for safe file deletion

Built with Python's tkinter for the GUI

Implements MD5 hashing for file comparison

## Safety Notes
Always verify selections before deleting files

Use "Move to Trash" option for safer file removal

Keep backups of important files before using the application

Check operation logs for any errors or issues

## Known Issues
This is just an ALPHA VERSION, with many bugs and work still to be done. 
It is more an exercise than a product!

Long paths on Windows may require enabling long path support

Large directories may take significant time to process

Memory usage increases with the number of files being compared
