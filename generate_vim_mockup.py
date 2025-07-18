from keystone.templates.skill_tree import generate_html
from keystone.utils.theme_loader import load_theme, load_icons

# Create Vim sample data
vim_data = {
    'tool': 'Vim',
    'version': '9.0',
    'categories': [
        {
            'name': 'Movement',
            'icon_name': 'grid',
            'keybinds': [
                {
                    'action': 'Move left',
                    'keys': 'h',
                    'description': 'Move cursor one character left'
                },
                {
                    'action': 'Move down',
                    'keys': 'j',
                    'description': 'Move cursor one line down'
                },
                {
                    'action': 'Move up',
                    'keys': 'k',
                    'description': 'Move cursor one line up'
                },
                {
                    'action': 'Move right',
                    'keys': 'l',
                    'description': 'Move cursor one character right'
                },
                {
                    'action': 'Word forward',
                    'keys': 'w',
                    'description': 'Move to beginning of next word'
                },
                {
                    'action': 'Word backward',
                    'keys': 'b',
                    'description': 'Move to beginning of previous word'
                }
            ]
        },
        {
            'name': 'Editing',
            'icon_name': 'wrench',
            'keybinds': [
                {
                    'action': 'Insert mode',
                    'keys': 'i',
                    'description': 'Enter insert mode'
                },
                {
                    'action': 'Insert at end',
                    'keys': 'a',
                    'description': 'Insert after cursor'
                },
                {
                    'action': 'Delete character',
                    'keys': 'x',
                    'description': 'Delete character under cursor'
                },
                {
                    'action': 'Delete line',
                    'keys': 'dd',
                    'description': 'Delete entire line'
                },
                {
                    'action': 'Yank line',
                    'keys': 'yy',
                    'description': 'Copy entire line'
                },
                {
                    'action': 'Paste',
                    'keys': 'p',
                    'description': 'Paste after cursor'
                }
            ]
        },
        {
            'name': 'File Operations',
            'icon_name': 'terminal',
            'keybinds': [
                {
                    'action': 'Save',
                    'keys': ':w',
                    'description': 'Write file to disk'
                },
                {
                    'action': 'Quit',
                    'keys': ':q',
                    'description': 'Quit vim'
                },
                {
                    'action': 'Save and quit',
                    'keys': ':wq',
                    'description': 'Write file and quit'
                },
                {
                    'action': 'Force quit',
                    'keys': ':q!',
                    'description': 'Quit without saving'
                }
            ]
        }
    ]
}

# Load theme and icons
theme = load_theme('default')
icons = load_icons()

# Generate HTML
html = generate_html(vim_data, theme, icons)

# Save mockup
with open('mockup_vim.html', 'w') as f:
    f.write(html)

print('✅ Generated mockup_vim.html')
print(f'   {len(vim_data["categories"])} categories')
print(f'   {sum(len(cat["keybinds"]) for cat in vim_data["categories"])} total keybinds')