import os

def find_layout_file():
    # This is a placeholder. A more robust implementation is needed.
    for name in ["keystone.yml", "layout.yml", ".keystone.yml"]:
        if os.path.exists(name):
            return name
    return None
