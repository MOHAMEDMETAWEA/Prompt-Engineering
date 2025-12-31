import nbformat
import os

def fix_notebook(path):
    print(f"Checking for UI issues in {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    updated = False
    for cell in nb.cells:
        if cell.cell_type == 'code':
            if "pn.pane.Markdown(response, width=600, style={'background-color': '#F6F6F6'})" in cell.source:
                # Fix the style argument for panel Markdown
                cell.source = cell.source.replace(
                    "pn.pane.Markdown(response, width=600, style={'background-color': '#F6F6F6'})",
                    "pn.pane.Markdown(response, width=600, styles={'background-color': '#F6F6F6'})"
                )
                updated = True
                print(f"  - Fixed pn.pane.Markdown style in {path}")

    if updated:
        with open(path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)

if __name__ == "__main__":
    notebooks = [f for f in os.listdir('.') if f.endswith('.ipynb')]
    for nb in notebooks:
        fix_notebook(nb)
