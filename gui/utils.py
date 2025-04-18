import tkinter as tk
import hashlib
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import fnmatch

def create_checkbox(checked: bool) -> tk.Canvas:
    """
    Create a checkbox image for the treeview.
    
    Args:
        checked (bool): Whether the checkbox should be displayed as checked.
    
    Returns:
        tk.Canvas: A canvas widget containing the checkbox drawing.
    """
    size = 20
    checkbox = tk.Canvas(width=size, height=size, highlightthickness=0)
    checkbox.create_rectangle(2, 2, size-2, size-2, outline='black')
    if checked:
        # Draw checkmark
        checkbox.create_line(4, size//2, size//2, size-4, width=2)
        checkbox.create_line(size//2, size-4, size-4, 4, width=2)
    return checkbox

def get_file_hash(filepath: str, chunk_size: int = 65536) -> str:
    """
    Calculate MD5 hash of a file.
    
    Args:
        filepath (str): Path to the file to hash.
        chunk_size (int): Size of chunks to read, defaults to 64KB.
    
    Returns:
        str: Hexadecimal representation of the file's MD5 hash.
    
    Raises:
        OSError: If there are problems reading the file.
        PermissionError: If there are permission issues accessing the file.
    """
    hasher = hashlib.md5()
    with open(filepath, 'rb') as f:
        buf = f.read(chunk_size)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(chunk_size)
    return hasher.hexdigest()

def format_file_size(size: int) -> str:
    """
    Format file size in bytes to human-readable format.
    
    Args:
        size (int): File size in bytes.
    
    Returns:
        str: Formatted size string (e.g., "1.5 MB", "800 KB", etc.).
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:,.1f} {unit}"
        size /= 1024.0
    return f"{size:,.1f} PB"

def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string in YYYY-MM-DD format.
    
    Args:
        date_str (str): Date string to parse.
    
    Returns:
        Optional[datetime]: Parsed datetime object or None if invalid format.
    """
    try:
        return datetime.strptime(date_str.strip(), '%Y-%m-%d')
    except ValueError:
        return None

def matches_pattern(filename: str, pattern: str) -> bool:
    """
    Check if filename matches the given pattern.
    
    Args:
        filename (str): Name of the file to check.
        pattern (str): Pattern to match against (supports wildcards).
    
    Returns:
        bool: True if filename matches pattern, False otherwise.
    """
    return fnmatch.fnmatch(filename, pattern)

def is_in_directory(filepath: str, directory: str) -> bool:
    """
    Check if a file is in the specified directory or its subdirectories.
    
    Args:
        filepath (str): Path to the file to check.
        directory (str): Directory to check against.
    
    Returns:
        bool: True if file is in directory or its subdirectories, False otherwise.
    """
    return os.path.normpath(filepath).startswith(os.path.normpath(directory))

def is_in_date_range(file_date: datetime, start_date: datetime, end_date: datetime) -> bool:
    """
    Check if a file's date falls within the specified range.
    
    Args:
        file_date (datetime): File's date to check.
        start_date (datetime): Start of date range.
        end_date (datetime): End of date range.
    
    Returns:
        bool: True if file's date is within range, False otherwise.
    """
    return start_date <= file_date <= end_date

def get_file_info(filepath: str) -> Dict[str, any]:
    """
    Get comprehensive file information.
    
    Args:
        filepath (str): Path to the file.
    
    Returns:
        Dict[str, any]: Dictionary containing file information:
            - name: filename
            - path: full path
            - size: size in bytes
            - date: modification datetime
            - hash: MD5 hash
    
    Raises:
        OSError: If there are problems accessing the file.
        PermissionError: If there are permission issues.
    """
    stat = os.stat(filepath)
    return {
        'name': os.path.basename(filepath),
        'path': filepath,
        'size': stat.st_size,
        'date': datetime.fromtimestamp(stat.st_mtime),
        'hash': get_file_hash(filepath)
    }

def find_duplicates(files: List[Dict[str, any]], 
                   match_name: bool = True,
                   match_size: bool = True,
                   match_date: bool = False) -> List[Tuple[Dict[str, any], Dict[str, any]]]:
    """
    Find duplicate files based on specified criteria.
    
    Args:
        files (List[Dict[str, any]]): List of file information dictionaries.
        match_name (bool): Whether to match filenames.
        match_size (bool): Whether to match file sizes.
        match_date (bool): Whether to match modification dates.
    
    Returns:
        List[Tuple[Dict[str, any], Dict[str, any]]]: List of duplicate file pairs.
    """
    duplicates = []
    for i, file1 in enumerate(files):
        for file2 in files[i + 1:]:
            if match_name and file1['name'] != file2['name']:
                continue
            if match_size and file1['size'] != file2['size']:
                continue
            if match_date and abs((file1['date'] - file2['date']).total_seconds()) > 1:
                continue
            if file1['hash'] == file2['hash']:
                duplicates.append((file1, file2))
    return duplicates

def create_log_filename() -> str:
    """
    Create a unique log filename based on current timestamp.
    
    Returns:
        str: Log filename in format 'delete_log_YYYYMMDD_HHMMSS.txt'
    """
    return f"delete_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

def log_operation(log_file: str, action: str, filepath: str, error: Optional[Exception] = None):
    """
    Log a file operation to the log file.
    
    Args:
        log_file (str): Path to the log file.
        action (str): Action performed (e.g., "Moved to trash", "Deleted").
        filepath (str): Path of the file operated on.
        error (Optional[Exception]): Exception if operation failed.
    """
    timestamp = datetime.now()
    with open(log_file, 'a', encoding='utf-8') as f:
        if error:
            f.write(f"{timestamp}: Error {action} - {filepath} - {str(error)}\n")
        else:
            f.write(f"{timestamp}: {action} - {filepath}\n")
