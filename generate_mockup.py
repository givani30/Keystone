from keystone.templates.skill_tree import generate_html
from keystone.utils.theme_loader import load_theme, load_icons
import json

# Create comprehensive sample data
sample_data = {
    'tool': 'VSCode',
    'version': '1.85.0',
    'categories': [
        {
            'name': 'File Operations',
            'icon_name': 'terminal',
            'keybinds': [
                {
                    'action': 'Open file',
                    'keys': 'Ctrl+O',
                    'description': 'Open a file from the filesystem'
                },
                {
                    'action': 'Save file',
                    'keys': 'Ctrl+S',
                    'description': 'Save the current file'
                },
                {
                    'action': 'Save as',
                    'keys': 'Ctrl+Shift+S',
                    'description': 'Save file with a new name'
                },
                {
                    'action': 'New file',
                    'keys': 'Ctrl+N'
                },
                {
                    'action': 'Close file',
                    'keys': 'Ctrl+W'
                }
            ]
        },
        {
            'name': 'Editing',
            'icon_name': 'wrench',
            'keybinds': [
                {
                    'action': 'Copy',
                    'keys': 'Ctrl+C',
                    'description': 'Copy selected text'
                },
                {
                    'action': 'Cut',
                    'keys': 'Ctrl+X',
                    'description': 'Cut selected text'
                },
                {
                    'action': 'Paste',
                    'keys': 'Ctrl+V',
                    'description': 'Paste from clipboard'
                },
                {
                    'action': 'Undo',
                    'keys': 'Ctrl+Z'
                },
                {
                    'action': 'Redo',
                    'keys': 'Ctrl+Y'
                },
                {
                    'action': 'Select all',
                    'keys': 'Ctrl+A'
                }
            ]
        },
        {
            'name': 'Navigation',
            'icon_name': 'grid',
            'keybinds': [
                {
                    'action': 'Go to line',
                    'keys': 'Ctrl+G',
                    'description': 'Jump to a specific line number'
                },
                {
                    'action': 'Find',
                    'keys': 'Ctrl+F',
                    'description': 'Find text in current file'
                },
                {
                    'action': 'Find and replace',
                    'keys': 'Ctrl+H',
                    'description': 'Find and replace text'
                },
                {
                    'action': 'Go to definition',
                    'keys': 'F12'
                },
                {
                    'action': 'Go back',
                    'keys': 'Alt+Left'
                }
            ]
        },
        {
            'name': 'Multi-key Commands',
            'icon_name': 'terminal',
            'keybinds': [
                {
                    'action': 'Open command palette',
                    'keys': ['Ctrl+Shift+P'],
                    'description': 'Access all available commands'
                },
                {
                    'action': 'Split editor',
                    'keys': ['Ctrl+K', 'Ctrl+S'],
                    'description': 'Split the editor window'
                },
                {
                    'action': 'Toggle terminal',
                    'keys': ['Ctrl+Shift+`'],
                    'description': 'Show or hide the integrated terminal'
                }
            ]
        }
    ]
}

# Load theme and icons
theme = load_theme('default')
icons = load_icons()

# Generate HTML
html = generate_html(sample_data, theme, icons)

# Save mockup
with open('mockup_vscode.html', 'w') as f:
    f.write(html)

print('✅ Generated mockup_vscode.html')
print(f'   {len(sample_data["categories"])} categories')
print(f'   {sum(len(cat["keybinds"]) for cat in sample_data["categories"])} total keybinds')