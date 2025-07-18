from keystone.templates.skill_tree import generate_html
from keystone.utils.theme_loader import load_theme, load_icons

# Create compact terminal shortcuts data
terminal_data = {
    'tool': 'Terminal Shortcuts',
    'categories': [
        {
            'name': 'Navigation',
            'icon_name': 'terminal',
            'keybinds': [
                {
                    'action': 'Beginning of line',
                    'keys': 'Ctrl+A'
                },
                {
                    'action': 'End of line',
                    'keys': 'Ctrl+E'
                },
                {
                    'action': 'Forward word',
                    'keys': 'Alt+F'
                },
                {
                    'action': 'Backward word',
                    'keys': 'Alt+B'
                }
            ]
        },
        {
            'name': 'Editing',
            'icon_name': 'wrench',
            'keybinds': [
                {
                    'action': 'Cut to end',
                    'keys': 'Ctrl+K'
                },
                {
                    'action': 'Cut to beginning',
                    'keys': 'Ctrl+U'
                },
                {
                    'action': 'Cut word',
                    'keys': 'Ctrl+W'
                },
                {
                    'action': 'Paste',
                    'keys': 'Ctrl+Y'
                }
            ]
        },
        {
            'name': 'Process Control',
            'icon_name': 'grid',
            'keybinds': [
                {
                    'action': 'Interrupt',
                    'keys': 'Ctrl+C'
                },
                {
                    'action': 'Suspend',
                    'keys': 'Ctrl+Z'
                },
                {
                    'action': 'EOF',
                    'keys': 'Ctrl+D'
                },
                {
                    'action': 'Clear screen',
                    'keys': 'Ctrl+L'
                }
            ]
        }
    ]
}

# Load theme and icons
theme = load_theme('default')
icons = load_icons()

# Generate HTML
html = generate_html(terminal_data, theme, icons)

# Save mockup
with open('mockup_terminal_compact.html', 'w') as f:
    f.write(html)

print('✅ Generated mockup_terminal_compact.html (Compact Layout)')
print(f'   {len(terminal_data["categories"])} categories')
print(f'   {sum(len(cat["keybinds"]) for cat in terminal_data["categories"])} total keybinds')