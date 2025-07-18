import json

def load_theme(theme_name):
    # This is a placeholder. A more robust implementation is needed.
    # This should handle theme inheritance.
    file_path = f"keystone/themes/{theme_name}.json"
    with open(file_path, 'r') as f:
        return json.load(f)
