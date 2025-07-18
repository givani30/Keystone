import json
import os
from pathlib import Path
from typing import Dict, Any

from .validator import validate_schema

def load_keybind_source(file_path: str) -> Dict[str, Any]:
    """
    Load and validate keybind data from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file containing keybind data
        
    Returns:
        Dict[str, Any]: Parsed and validated keybind data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file cannot be read due to permissions
        json.JSONDecodeError: If the file contains invalid JSON
        ValueError: If the data doesn't match the expected schema
        IOError: For other file-related errors
    """
    # Step 1: File Reading and Error Handling
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Keybind data file not found: {file_path}")
    
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except PermissionError:
        raise PermissionError(f"Permission denied when reading file: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {str(e)}")
    
    # Step 2: JSON Parsing and Error Handling
    try:
        data = json.loads(file_content)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Invalid JSON in file {file_path}: {str(e)}", 
            e.doc, 
            e.pos
        )
    
    # Step 3: Schema Validation Using validator.py
    try:
        # Load the data schema
        schema_path = Path(__file__).parent.parent / "assets" / "schemas" / "data_schema.json"
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        # Validate the data against the schema
        is_valid, error = validate_schema(data, schema)
        if not is_valid:
            raise ValueError(f"Schema validation failed for {file_path}: {str(error)}")
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Data schema file not found: {schema_path}")
    except Exception as e:
        raise ValueError(f"Schema validation error for {file_path}: {str(e)}")
    
    return data

