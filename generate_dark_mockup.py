from keystone.templates.skill_tree import generate_html
from keystone.utils.theme_loader import load_theme, load_icons

# Create Git sample data
git_data = {
    'tool': 'Git',
    'version': '2.40.0',
    'categories': [
        {
            'name': 'Basic Commands',
            'icon_name': 'terminal',
            'keybinds': [
                {
                    'action': 'Initialize repository',
                    'keys': 'git init',
                    'description': 'Create a new Git repository'
                },
                {
                    'action': 'Clone repository',
                    'keys': 'git clone <url>',
                    'description': 'Clone a remote repository'
                },
                {
                    'action': 'Check status',
                    'keys': 'git status',
                    'description': 'Show working tree status'
                },
                {
                    'action': 'Add files',
                    'keys': 'git add <file>',
                    'description': 'Add files to staging area'
                },
                {
                    'action': 'Commit changes',
                    'keys': 'git commit -m "message"',
                    'description': 'Commit staged changes'
                }
            ]
        },
        {
            'name': 'Branching',
            'icon_name': 'grid',
            'keybinds': [
                {
                    'action': 'Create branch',
                    'keys': 'git branch <name>',
                    'description': 'Create a new branch'
                },
                {
                    'action': 'Switch branch',
                    'keys': 'git checkout <branch>',
                    'description': 'Switch to a branch'
                },
                {
                    'action': 'Create and switch',
                    'keys': 'git checkout -b <name>',
                    'description': 'Create and switch to new branch'
                },
                {
                    'action': 'Merge branch',
                    'keys': 'git merge <branch>',
                    'description': 'Merge branch into current'
                },
                {
                    'action': 'Delete branch',
                    'keys': 'git branch -d <name>',
                    'description': 'Delete a branch'
                }
            ]
        },
        {
            'name': 'Remote Operations',
            'icon_name': 'wrench',
            'keybinds': [
                {
                    'action': 'Fetch changes',
                    'keys': 'git fetch',
                    'description': 'Download changes from remote'
                },
                {
                    'action': 'Pull changes',
                    'keys': 'git pull',
                    'description': 'Fetch and merge changes'
                },
                {
                    'action': 'Push changes',
                    'keys': 'git push',
                    'description': 'Upload changes to remote'
                },
                {
                    'action': 'Add remote',
                    'keys': 'git remote add <name> <url>',
                    'description': 'Add a remote repository'
                }
            ]
        },
        {
            'name': 'History & Inspection',
            'icon_name': 'grid',
            'keybinds': [
                {
                    'action': 'View log',
                    'keys': 'git log',
                    'description': 'Show commit history'
                },
                {
                    'action': 'Show differences',
                    'keys': 'git diff',
                    'description': 'Show file differences'
                },
                {
                    'action': 'Show commit',
                    'keys': 'git show <commit>',
                    'description': 'Show commit details'
                },
                {
                    'action': 'Blame file',
                    'keys': 'git blame <file>',
                    'description': 'Show line-by-line history'
                }
            ]
        }
    ]
}

# Load dark theme and icons
theme = load_theme('dark_simple')
icons = load_icons()

# Generate HTML
html = generate_html(git_data, theme, icons)

# Save mockup
with open('mockup_git_dark.html', 'w') as f:
    f.write(html)

print('✅ Generated mockup_git_dark.html (Dark Theme)')
print(f'   {len(git_data["categories"])} categories')
print(f'   {sum(len(cat["keybinds"]) for cat in git_data["categories"])} total keybinds')