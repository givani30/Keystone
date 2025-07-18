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

def generate_keybinds(keybinds, theme):
    # This is a placeholder. A more robust implementation is needed.
    return "<ul>" + "".join([f"<li>{kb['action']}</li>" for kb in keybinds]) + "</ul>"