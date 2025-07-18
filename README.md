# Keystone

**Generate beautiful, customizable keybind cheatsheets from JSON data sources**

Keystone is a powerful command-line tool that transforms your keybind configurations into polished HTML and PDF cheatsheets. Perfect for documenting editor shortcuts, terminal commands, application hotkeys, and more.

## ✨ Features

- **Multiple Data Sources**: Combine keybinds from multiple JSON files
- **Smart Category Filtering**: Pick specific categories from each source
- **Flexible Templates**: Choose between skill tree and reference card layouts
- **Customizable Themes**: Built-in themes with override support
- **Multiple Output Formats**: Generate HTML and PDF files
- **Inline Data Support**: Add custom keybinds directly in layout files
- **Responsive Design**: Mobile-friendly layouts with print optimization
- **Data Validation**: Built-in validation for configurations and references

## 🚀 Quick Start

1. **Install Keystone**:
   ```bash
   pip install keystone-cheatsheets
   ```

2. **Create example files**:
   ```bash
   keystone --init
   ```

3. **Generate your first cheatsheet**:
   ```bash
   keystone my_workflow.yml
   ```

4. **Open the generated HTML file** in your browser to see your cheatsheet!

## 📦 Installation

### Using pip
```bash
pip install keystone-cheatsheets
```

### Using uv (recommended)
```bash
uv add keystone-cheatsheets
```

### From source
```bash
git clone https://github.com/your-username/keystone.git
cd keystone
uv install
```

## 📚 Usage

### Basic Usage

```bash
# Generate HTML cheatsheet
keystone my_layout.yml

# Generate PDF cheatsheet  
keystone my_layout.yml --format pdf

# Generate both HTML and PDF
keystone my_layout.yml --format both

# Use a different theme
keystone my_layout.yml --theme dark

# Use a different template
keystone my_layout.yml --template reference_card
```

### Helper Commands

```bash
# Create example files in current directory
keystone --init

# Validate configuration without generating output
keystone --validate my_layout.yml

# List available themes
keystone --list-themes

# Show help
keystone --help
```

### Auto-discovery

If you don't specify a layout file, Keystone will automatically search for:
- `keystone.yml`
- `layout.yml` 
- `.keystone.yml`

```bash
# These are equivalent if keystone.yml exists
keystone keystone.yml
keystone
```

## 📄 File Formats

### Layout File (YAML)

The layout file defines how to combine data sources and generate your cheatsheet:

```yaml
# Required fields
title: "My Development Workflow"
template: skill_tree  # or "reference_card"
theme: default
output_name: my_cheatsheet  # Base name for output files

# Define categories that combine multiple data sources
categories:
  - name: "Text Editing"
    theme_color: "blue"         # Optional: theme color variant
    icon_name: "terminal"       # Optional: icon reference
    sources:                    # Optional: external data sources
      - file: "vim.json"
        pick_category: "editing"  # Pick specific category from source
    keybinds:                   # Optional: inline keybinds (highest priority)
      - action: "Save All"
        keys: "Ctrl+Shift+S"
        description: "Save all open files"

  - name: "Navigation"
    theme_color: "purple"
    icon_name: "grid"
    sources:
      - file: "vim.json"
        pick_category: "navigation"

  - name: "Custom Shortcuts"
    theme_color: "blue"
    icon_name: "terminal"
    keybinds:                   # Pure inline category (no external sources)
      - action: "Open Terminal"
        keys: "Ctrl+Alt+T"
        description: "Quick terminal access"

# Optional: Theme customization
theme_overrides:
  base_styles:
    body: "bg-gradient-to-br from-blue-50 to-indigo-100"
  color_variants:
    custom:
      header: "bg-blue-600 text-white"
      accent: "text-blue-700"

# Optional: Grid layout settings
grid:
  columns: 3
  gap: "large"
  responsive: true
```

### Data File (JSON)

Data files contain your keybind definitions:

```json
{
  "tool": "Vim",
  "categories": [
    {
      "name": "editing",
      "keybinds": [
        {
          "action": "Copy",
          "keys": "Ctrl+C",
          "description": "Copy selected text to clipboard"
        },
        {
          "action": "Paste",
          "keys": "Ctrl+V",
          "description": "Paste text from clipboard"
        }
      ]
    },
    {
      "name": "navigation",
      "keybinds": [
        {
          "action": "Find",
          "keys": "Ctrl+F",
          "description": "Open search dialog"
        }
      ]
    }
  ]
}
```

## 🎨 Templates

Keystone includes two built-in templates:

### Skill Tree Template
- **Best for**: Complex workflows with many categories
- **Layout**: Card-based grid layout
- **Features**: Icons, color coding, responsive design

### Reference Card Template  
- **Best for**: Quick reference guides
- **Layout**: Compact table format
- **Features**: Minimal design, high information density

Choose with the `--template` flag or in your layout file:
```yaml
template: skill_tree  # or reference_card
```

## 🎭 Themes

### Built-in Themes

- **`default`**: Clean, professional look with subtle shadows
- **`dark`**: Dark mode with high contrast
- **`minimal`**: Ultra-clean design with minimal styling
- **`dark_simple`**: Simplified dark theme

Use themes with the `--theme` flag:
```bash
keystone layout.yml --theme dark
```

### Theme Customization

Override theme properties in your layout file:

```yaml
theme_overrides:
  base_styles:
    body: "bg-gradient-to-br from-purple-50 to-pink-100"
    container: "mx-auto p-6"
  
  card_styles:
    card: "bg-white rounded-xl border-2 border-purple-200 shadow-lg"
    card_header: "bg-purple-100 p-4 rounded-t-xl"
  
  keybind_styles:
    key: "bg-purple-600 text-white px-3 py-1 rounded font-mono"
  
  color_variants:
    purple:
      header: "bg-purple-500 text-white"
      accent: "text-purple-600"
```

## 🔄 Advanced Features

### Category Filtering

Pick specific categories from data sources:

```yaml
categories:
  - name: "Essential Commands"
    sources:
      - file: "vim.json"
        pick_category: "editing"  # Single category
      - file: "comprehensive_shortcuts.json"  
        pick_category: ["essential", "basic"]  # Multiple categories
```

### Multiple Data Sources

Combine keybinds from multiple tools in one category:

```yaml
categories:
  - name: "Development Workflow" 
    sources:
      - file: "vim.json"
      - file: "tmux.json"  
      - file: "git.json"
      - file: "shell_essentials.json"
```

### Inline Data

Add custom keybinds directly in categories:

```yaml
categories:
  - name: "Custom Shortcuts"
    theme_color: "blue"
    icon_name: "terminal"
    keybinds:
      - action: "App Launcher"
        keys: "Super+Space"
        description: "Open application launcher"
      - action: "Quick Terminal"
        keys: "Ctrl+Alt+T"
        description: "Fast terminal access"
```

### Priority System

Data is merged with this priority (highest to lowest):

1. **Inline keybinds** (in category `keybinds` field)
2. **External sources** (in category `sources` field, in order listed)

Later sources override earlier ones for duplicate action names.

## 🔧 Configuration Reference

### Layout File Schema

```yaml
# Required
title: string              # Cheatsheet title
template: string           # "skill_tree" or "reference_card"  
theme: string             # Theme name
output_name: string       # Base name for output files (without extension)

# Optional
categories:               # List of categories to display
  - name: string         # Category name (required)
    theme_color: string  # Theme color variant (optional)
    icon_name: string    # Icon reference (optional)
    sources:             # External data sources (optional)
      - file: string     # Path to JSON file
        pick_category: string|array  # Category/categories to include
    keybinds:           # Inline keybind definitions (optional)
      - action: string  # Action name (required)
        keys: string|array  # Key combination(s) (required)
        description: string  # Detailed description (optional)

theme_overrides:         # Theme customization (optional)
  base_styles: object   # Base styling overrides
  card_styles: object   # Card component overrides
  keybind_styles: object # Keybind styling overrides
  color_variants: object # Color scheme variants

grid:                    # Grid layout settings (optional)
  columns: number       # Number of columns
  gap: string          # Gap size ("small", "medium", "large")
  responsive: boolean   # Enable responsive behavior
```

### Data File Schema

```json
{
  "tool": "string",         // Tool name (required)
  "version": "string",      // Tool version (optional)
  "categories": [
    {
      "name": "string",     // Category name (required)
      "keybinds": [
        {
          "action": "string",      // Action name (required)
          "keys": "string|array",  // Key combination(s) (required)
          "description": "string"  // Description (optional)
        }
      ]
    }
  ]
}
```

## 🎯 Examples

The `--init` command creates several example files to get you started:

### `my_workflow.yml`

Advanced layout showcasing:

- Multiple data sources
- Category filtering  
- Inline data
- Theme overrides
- Grid customization

### Data Files
- **`vim.json`**: Vim editor keybindings
- **`tmux.json`**: Terminal multiplexer commands  
- **`git.json`**: Git version control workflow
- **`shell_essentials.json`**: Essential shell commands

### Usage Examples

```bash
# Generate the example workflow
keystone my_workflow.yml

# Create a quick vim reference
keystone --init
echo 'title: "Vim Quick Reference"
template: reference_card
theme: minimal
output_name: vim_quick
categories:
  - name: "Essential Editing"
    sources:
      - file: "vim.json"
        pick_category: ["editing", "navigation"]' > vim_quick.yml
keystone vim_quick.yml

# Generate a dark-themed git cheatsheet
echo 'title: "Git Commands"
template: skill_tree  
theme: dark
output_name: git_dark
categories:
  - name: "Git Workflow"
    sources:
      - file: "git.json"' > git_dark.yml
keystone git_dark.yml
```

## 🐛 Troubleshooting

### Common Issues

**"Layout file not found"**
- Ensure the file path is correct
- Check file permissions
- Use `--validate` to test your configuration

**"Theme not found"**
- Use `--list-themes` to see available themes
- Check theme name spelling
- Ensure custom theme files are in the themes directory

**"Template not found"**
- Valid templates are: `skill_tree`, `reference_card`
- Check spelling in layout file or `--template` flag

**"Validation failed"**
- Use `--validate` to see specific errors
- Check JSON syntax in data files
- Verify all referenced files exist

### Getting Help

```bash
# Validate your configuration
keystone --validate my_layout.yml

# Check available options
keystone --help

# List available themes
keystone --list-themes
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/keystone.git
cd keystone

# Install with development dependencies
uv install --dev

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=keystone
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with modern Python tooling (uv, pytest)
- Styled with Tailwind CSS classes
- Icons from Unicode emoji set
- PDF generation powered by WeasyPrint
