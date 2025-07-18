import os
from pathlib import Path
from typing import Optional


def find_layout_file(start_dir: Optional[str] = None, max_depth: int = 10) -> Optional[str]:
    """
    Find a layout configuration file by searching up the directory tree.
    
    Searches for files named:
    - keystone.yml
    - layout.yml  
    - .keystone.yml
    
    Args:
        start_dir: Directory to start search from. Defaults to current working directory.
        max_depth: Maximum number of parent directories to check. Defaults to 10.
        
    Returns:
        Path to the first layout file found, or None if not found.
        
    Raises:
        OSError: If there are permission issues accessing directories.
    """
    # Start from current working directory if not specified
    if start_dir is None:
        start_dir = os.getcwd()
    
    current_path = Path(start_dir).resolve()
    config_filenames = ["keystone.yml", "layout.yml", ".keystone.yml"]
    
    # Keep track of depth to avoid infinite traversal
    depth = 0
    
    while depth < max_depth:
        # Check for config files in current directory
        for filename in config_filenames:
            config_path = current_path / filename
            if config_path.is_file():
                try:
                    # Test if file is readable
                    with open(config_path, 'r') as f:
                        f.read(1)  # Try to read one character
                    return str(config_path)
                except (OSError, PermissionError):
                    # If we can't read this file, continue searching
                    continue
        
        # Move to parent directory
        parent = current_path.parent
        
        # Stop if we've reached the filesystem root
        if parent == current_path:
            break
            
        current_path = parent
        depth += 1
    
    return None
