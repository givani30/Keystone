import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from copy import deepcopy

from .data_loader import load_keybind_source
from .validator import validate_schema


def parse_layout(file_path: str) -> Dict[str, Any]:
    """
    Parse a layout file and return the merged data structure.
    
    Args:
        file_path: Path to the layout YAML file
        
    Returns:
        Dictionary containing the merged layout data
        
    Raises:
        FileNotFoundError: If the layout file doesn't exist
        yaml.YAMLError: If the YAML is invalid
        ValueError: If the layout doesn't match the schema
    """
    layout_path = Path(file_path)
    
    if not layout_path.exists():
        raise FileNotFoundError(f"Layout file not found: {layout_path}")
    
    # Load and validate the layout file
    try:
        with open(layout_path, 'r', encoding='utf-8') as f:
            layout_data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in layout file {layout_path}: {str(e)}")
    
    # Validate layout against schema
    try:
        layout_schema_path = Path(__file__).parent.parent / "assets" / "schemas" / "layout_schema.json"
        with open(layout_schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        
        is_valid, error = validate_schema(layout_data, schema)
        if not is_valid:
            raise ValueError(f"Layout schema validation failed for {layout_path}: {str(error)}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Layout schema file not found: {layout_schema_path}")
    
    # Process the layout and merge data
    merged_data = process_layout(layout_data, layout_path.parent)
    
    return merged_data


def process_layout(layout_data: Dict[str, Any], base_path: Path) -> Dict[str, Any]:
    """
    Process the layout data and merge keybinds from all sources.
    
    Args:
        layout_data: Raw layout data from YAML
        base_path: Base path for resolving relative file paths
        
    Returns:
        Processed layout data with merged keybinds
    """
    # Start with a copy of the layout data
    result = deepcopy(layout_data)
    
    # Process each category
    for category in result.get("categories", []):
        merged_keybinds = merge_category_data(category, base_path)
        category["keybinds"] = merged_keybinds
        
        # Remove sources field as it's no longer needed
        category.pop("sources", None)
    
    return result


def merge_category_data(category: Dict[str, Any], base_path: Path) -> List[Dict[str, Any]]:
    """
    Merge keybinds from all sources for a single category.
    
    Args:
        category: Category data from layout
        base_path: Base path for resolving relative file paths
        
    Returns:
        List of merged keybinds
    """
    merged_keybinds = []
    
    # Step 1: Load and merge keybinds from all sources (lowest priority)
    sources = category.get("sources", [])
    for source in sources:
        source_keybinds = load_source_keybinds(source, base_path)
        merged_keybinds = merge_keybinds(merged_keybinds, source_keybinds)
    
    # Step 2: Merge inline keybinds (highest priority)
    inline_keybinds = category.get("keybinds", [])
    if inline_keybinds:
        merged_keybinds = merge_keybinds(merged_keybinds, inline_keybinds)
    
    return merged_keybinds


def load_source_keybinds(source: Dict[str, Any], base_path: Path) -> List[Dict[str, Any]]:
    """
    Load keybinds from a single source file.
    
    Args:
        source: Source configuration from layout
        base_path: Base path for resolving relative file paths
        
    Returns:
        List of keybinds from the source
    """
    file_path = source["file"]
    
    # Resolve relative paths
    if not Path(file_path).is_absolute():
        file_path = base_path / file_path
    
    # Load the source data
    source_data = load_keybind_source(str(file_path))
    
    # Extract keybinds from the specified categories
    pick_category = source.get("pick_category")
    if pick_category:
        return extract_categories(source_data, pick_category)
    else:
        # Return all keybinds from all categories
        all_keybinds = []
        for category in source_data.get("categories", []):
            all_keybinds.extend(category.get("keybinds", []))
        return all_keybinds


def extract_categories(source_data: Dict[str, Any], pick_category: Any) -> List[Dict[str, Any]]:
    """
    Extract keybinds from specified categories.
    
    Args:
        source_data: Loaded source data
        pick_category: Category name(s) to pick
        
    Returns:
        List of keybinds from the specified categories
    """
    if isinstance(pick_category, str):
        pick_category = [pick_category]
    
    extracted_keybinds = []
    
    for category in source_data.get("categories", []):
        if category.get("name") in pick_category:
            extracted_keybinds.extend(category.get("keybinds", []))
    
    return extracted_keybinds


def merge_keybinds(base_keybinds: List[Dict[str, Any]], new_keybinds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Merge two lists of keybinds, with new_keybinds taking priority.
    
    Args:
        base_keybinds: Existing keybinds (lower priority)
        new_keybinds: New keybinds to merge in (higher priority)
        
    Returns:
        Merged list of keybinds
    """
    # Create a copy of base keybinds
    merged = deepcopy(base_keybinds)
    
    # Track actions we've seen to handle overrides
    action_to_index = {}
    for i, keybind in enumerate(merged):
        action = keybind.get("action")
        if action:
            action_to_index[action] = i
    
    # Process new keybinds
    for new_keybind in new_keybinds:
        action = new_keybind.get("action")
        if action and action in action_to_index:
            # Override existing keybind
            merged[action_to_index[action]] = deepcopy(new_keybind)
        else:
            # Add new keybind
            merged.append(deepcopy(new_keybind))
            if action:
                action_to_index[action] = len(merged) - 1
    
    return merged
