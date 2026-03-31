"""Fix Notebook UI script.

Purpose:
- Scan and patch known Panel UI issues in Jupyter notebooks.
- Specifically fixes `pn.pane.Markdown` style keyword mismatch.

Main components:
- fix_notebook(path): reads and updates notebook code cells.
- __main__ uses current directory `.ipynb` files.

Dependencies:
- nbformat
- os

TODO:
- Add file-wide “dry-run” mode to view changes without writing.
"""

import nbformat
import os

def fix_notebook(path):
    """Read notebook and correct recognized UI syntax issues.

    Parameters:
    - path: str path to the target .ipynb file.

    Returns:
    - None. Writes the notebook back if any replacements occur.

    Example:
    >>> fix_notebook('sample.ipynb')
    """
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
