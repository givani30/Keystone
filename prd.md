# Keystone - Product Requirements Document

## Overview

A Python command-line tool that generates visually appealing keybind cheatsheets from JSON configuration files. The tool should produce both HTML and PDF outputs optimized for A4 printing and screen viewing.

## Problem Statement

Creating professional-looking keybind cheatsheets is time-consuming and requires manual HTML/CSS work. Users need a simple way to convert structured keybind data into beautiful, printable reference materials that work across different workflows (Hyprland, terminal tools, applications, etc.).

## Goals

- **Primary**: Generate beautiful cheatsheets from JSON configs with minimal effort
- **Secondary**: Support multiple visual styles and output formats
- **Future**: Enable easy customization and extensibility

## Target User

- Advanced Linux users (Arch/Hyprland users)
- Developers who customize their workflows
- Anyone who needs to document keybinds professionally

## Core Features

### 1. Data Architecture: Separation of Data and Layout

#### Keybind Data Files (Tool-Specific)
```json
{
  "tool": "zellij",
  "version": "1.0",
  "categories": [
    {
      "name": "Basic Navigation",
      "keybinds": [
        {
          "action": "Toggle Fullscreen",
          "keys": ["Ctrl", "Space", "f"],
          "description": "Toggle current pane fullscreen"
        },
        {
          "action": "Smart Jump",
          "keys": "zi",
          "description": "Jump to directory using zoxide"
        }
      ]
    }
  ]
}
```

#### Layout Configuration (Presentation Definition)
```yaml
title: "My Complete Workflow"
subtitle: "Personalized keybind reference"
template: "skill_tree"
theme: "default"
output_name: "my_workflow"

categories:
  - name: "Level 1: Shell Essentials"
    theme_color: "blue"        
    icon_name: "terminal"      
    sources:
      - file: "shell_essentials.json"
        pick_category: ["Basic Commands", "Advanced Commands"]  # Multiple categories
      - file: "fzf_config.json"
        pick_category: "Search Controls"
  
  - name: "Level 2: Multiplexer"
    theme_color: "purple"
    icon_name: "grid"
    sources:
      - file: "zellij.json"     # Import entire file
        
  # Inline keybinds have highest priority and will override imported ones
  - name: "Level 3: Custom Overrides"
    theme_color: "green"
    icon_name: "wrench"
    sources:
      - file: "custom_tools.json"
    keybinds:  # These override any conflicting keybinds from sources
      - action: "Custom Command"
        keys: ["Alt", "X"]
```

#### Data Merging Rules (KISS Approach)
1. **Inline keybinds** (in layout file) have highest priority
2. **Earlier sources** override later sources when categories have same name
3. **No complex merging** - simple override semantics
```

### 2. Robust Schema Design

#### Enhanced JSON Schema for Data Files
- **Keys field**: Accepts both `"keys": ["Ctrl", "R"]` and `"keys": "lastcp"`
- **Explicit validation**: Theme colors and icon names validated against manifests
- **Flexible structure**: Supports tool metadata and versioning

#### Theme Color Manifest
```json
{
  "blue": {
    "card_header": "bg-blue-50 text-blue-700 border-blue-200",
    "card_body": "bg-white text-gray-800",
    "accent": "text-blue-600"
  },
  "purple": {
    "card_header": "bg-purple-50 text-purple-700 border-purple-200", 
    "card_body": "bg-white text-gray-800",
    "accent": "text-purple-600"
  }
}
```

#### Icon Manifest (Heroicons)
```json
{
  "terminal": "<svg>...</svg>",
  "grid": "<svg>...</svg>",
  "wrench": "<svg>...</svg>"
}
```

### 3. Template System
- **Skill Tree Template**: Card-based layout like the provided example
  - Grid layout (responsive: 1-4 columns based on screen size)
  - Color-coded categories with icons
  - Hover effects and professional styling
  - Support for subcategories within cards
- **Reference Card Template**: Dense, traditional layout
  - Table-based design
  - Maximizes information density
  - Clean typography optimized for quick scanning

### 4. Decoupled Theme Architecture

Templates and themes are completely independent:

- **Templates** (`skill_tree.py`): Define structure and layout logic
- **Themes** (`default.json`): Define styling via class mappings
- **Manifest files**: Validate color and icon references

#### Simple Theme Inheritance
```json
{
  "name": "My Custom Dark",
  "inherits_from": "dark",     // Load base theme first
  "color_variants": {
    "blue": {                  // Override just blue colors
      "header": "bg-blue-900 text-blue-100",
      "accent": "text-blue-400"
    }
  }
}
```
```json
{
  "name": "Default Theme",
  "base_styles": {
    "body": "bg-gray-50 text-gray-800 font-inter",
    "container": "mx-auto p-4 sm:p-6 lg:p-8"
  },
  "card_styles": {
    "card": "bg-white rounded-xl border shadow-md hover:shadow-lg transition-all",
    "card_header": "flex items-center gap-3 p-4 border-b",
    "card_body": "p-6"
  },
  "keybind_styles": {
    "key": "bg-gray-200 border border-gray-300 rounded-md px-2 py-1 font-mono text-sm font-semibold",
    "key_group": "inline-flex items-center gap-1"
  },
  "color_variants": {
    "blue": { "header": "bg-blue-50 text-blue-700", "accent": "text-blue-600" },
    "purple": { "header": "bg-purple-50 text-purple-700", "accent": "text-purple-600" }
  }
}
```

Templates reference theme classes generically:
```python
# In skill_tree.py template
def generate_category_card(category, theme):
    color_variant = theme["color_variants"][category.theme_color]
    return f'''
    <div class="{theme["card_styles"]["card"]}">
        <div class="{theme["card_styles"]["card_header"]} {color_variant["header"]}">
            {category.icon_svg}
            <h2>{category.name}</h2>
        </div>
        <div class="{theme["card_styles"]["card_body"]}">
            {generate_keybinds(category.keybinds, theme)}
        </div>
    </div>
    '''
```

### 5. Dependency Management & Installation

#### Core vs Optional Dependencies
```toml
[project]
name = "cheatsheet-generator"
dependencies = [
    "pyyaml",           # For layout files
    "jsonschema",       # Schema validation (lightweight)
]

[project.optional-dependencies]
pdf = ["weasyprint>=60.0"]        # Heavy PDF dependency
dev = ["pytest", "black", "mypy"]
```

#### Graceful PDF Handling
- Core tool works perfectly with zero heavy dependencies
- PDF generation requires explicit opt-in: `pip install cheatsheet-generator[pdf]`
- Clear error messages when PDF requested without weasyprint:
  ```
  Error: PDF generation requires weasyprint. Install with:
  pip install cheatsheet-generator[pdf]
  
  Alternatively, generate HTML and use browser's "Print to PDF" feature.
  ```
- **HTML**: Self-contained file with embedded CSS
- **PDF**: Generated from HTML using weasyprint
- Both optimized for:
  - A4 page size
  - Print-friendly styling
  - Screen viewing

### 6. Enhanced Command Line Interface
```bash
# Auto-discovery: looks for keystone.yml, layout.yml, or .keystone.yml
keystone                     # Run from anywhere in project

# Explicit file
keystone my_layout.yml

# Override layout settings  
keystone --template reference_card --theme dark

# Output control
keystone --format pdf --output ~/Desktop/cheatsheet.pdf

# Quick validation
keystone --validate

# Setup helpers
keystone --init              # Create example files in current directory
keystone --list-themes       # Show available themes
```

### 7. Advanced Features

#### Data Composition & Merging
- Import keybinds from multiple sources
- Filter and pick specific categories from source files
- Override and extend imported keybinds
- Merge strategies for conflicting data

#### Validation & Error Handling
- Schema validation for both data files and layout files
- Icon and theme color reference validation
- Clear error messages with suggestions
- Dependency checking with helpful install instructions

#### Extensibility
- Plugin system for custom templates
- Custom theme creation with validation
- Icon library extensions
- Layout file preprocessing hooks

## Technical Requirements

### Dependencies
- **Core**: `json`, `pathlib`, `argparse` (stdlib)
- **Validation**: `jsonschema` (optional but recommended)
- **PDF Generation**: `weasyprint` (optional)
- **Fallback PDF**: `pdfkit` + `wkhtmltopdf`

### Architecture
```
keystone/
├── __init__.py
├── main.py                   # CLI entry point
├── core/
│   ├── generator.py          # Core generation logic  
│   ├── validator.py          # Schema validation
│   ├── data_loader.py        # Data loading with simple merging
│   └── layout_parser.py      # YAML layout parsing
├── templates/
│   ├── skill_tree.py         # Card-based template
│   └── reference_card.py     # Dense table template  
├── themes/
│   ├── default.json          # Base themes
│   ├── dark.json
│   └── minimal.json
├── assets/
│   ├── icons.json            # Heroicons manifest
│   └── schemas/
│       ├── data_schema.json      # Keybind data validation
│       └── layout_schema.json    # Layout file validation
└── utils/
    ├── discovery.py          # Config file discovery
    ├── pdf_generator.py      # Optional PDF generation
    └── theme_loader.py       # Theme inheritance logic
```

### Command Line Interface
```bash
# Basic usage
python -m cheatsheet_generator config.json

# Specify output format
python -m cheatsheet_generator config.json --format html
python -m cheatsheet_generator config.json --format pdf
python -m cheatsheet_generator config.json --format both

# Specify template and theme
python -m cheatsheet_generator config.json --template reference_card --theme dark

# Specify output file
python -m cheatsheet_generator config.json --output my_cheatsheet

# Validate only
python -m cheatsheet_generator config.json --validate-only

# Generate example config
python -m cheatsheet_generator --example > example_config.json
```

## User Stories

### As a user, I want to...
1. **Generate from JSON**: Convert my keybind JSON to a beautiful cheatsheet with one command
2. **Print-ready output**: Get A4-optimized PDF I can print immediately
3. **Screen viewing**: Get responsive HTML I can reference on my monitor
4. **Validation feedback**: Get clear error messages when my JSON is malformed
5. **Template choice**: Choose between dense reference cards and visual skill trees
6. **Theme options**: Switch between light, dark, and minimal themes
7. **LLM integration**: Use the JSON format with AI tools to auto-generate configs

## Success Metrics

- **Ease of use**: Generate cheatsheet with single command
- **Quality**: Output looks professional and print-ready
- **Flexibility**: Support multiple keybind workflows
- **Reliability**: Clear validation and error handling

## Implementation Phases

### Phase 1: Core Functionality (MVP)
- JSON schema and validation
- Skill tree template (based on provided example)
- HTML output with embedded CSS
- Basic CLI interface
- Default theme only

### Phase 2: Enhanced Features
- PDF generation
- Reference card template
- Theme system (default, dark, minimal)
- Icon system
- Better error handling and validation

### Phase 3: Polish & Extensions
- Responsive design improvements
- Additional templates
- Custom CSS injection
- Performance optimizations
- Documentation and examples

## Technical Considerations

### A4 Print Optimization
- CSS `@media print` rules
- Page break control
- Optimal font sizes for printing
- Margin and spacing adjustments

### Responsive Design
- CSS Grid with responsive breakpoints
- Mobile-friendly sizing
- Flexible layouts that work 1-4 columns

### Performance
- Single-file HTML output (no external dependencies)
- Embedded CSS and icons
- Fast generation for large configs

### Extensibility
- Plugin-like template system
- Easy theme customization
- Modular architecture for future features

## Example Usage Workflows

### Workflow 1: Modular Setup (Recommended)
1. Create tool-specific data files:
   ```bash
   # zellij_keybinds.json, hyprland_keybinds.json, etc.
   ```
2. Create layout configuration:
   ```bash
   # my_workflow.yml - defines which data to use and how to present it
   ```
3. Generate cheatsheet:
   ```bash
   cheatsheet-gen my_workflow.yml --format both
   ```
4. Output: `my_workflow.html` and `my_workflow.pdf`

### Workflow 2: LLM Integration
1. Use AI to parse existing configs:
   ```
   "Convert my Hyprland config to the cheatsheet data format"
   ```
2. AI generates `hyprland_keybinds.json`
3. Create layout file referencing the generated data
4. Generate beautiful cheatsheet

### Workflow 3: Legacy Single-File
1. Create monolithic JSON with all keybinds
2. Run: `cheatsheet-gen keybinds.json --legacy-mode`
3. Works like the original design but less flexible

## Risk Mitigation

- **No dependencies**: Graceful degradation when optional packages missing
- **Validation**: Comprehensive JSON validation prevents runtime errors
- **Fallbacks**: Multiple PDF generation options
- **Self-contained**: HTML output has no external dependencies
