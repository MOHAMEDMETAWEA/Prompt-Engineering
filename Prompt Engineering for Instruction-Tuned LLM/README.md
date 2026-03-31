# Prompt Engineering for Instruction-Tuned LLM

## Folder Purpose
Contains scripts and notebooks for instruction-tuning style prompt engineering patterns, context restoration, and standardization for demo notebooks.

## File Structure
- `fix_ui_notebooks.py` - patch known Panel UI problems in notebooks.
- `restore_context.py` - reinject or validate conversation context for demos.
- `standardize_all_notebooks.py` - normalize notebook scaffold across all .ipynb files.
- `test_moderation.py` - quick moderation API connectivity check.
- `utils.py` - shared dataset and OpenAI helpers.
- `products.json` - sample product dataset.
- many `.ipynb` notebooks demonstrating prompt patterns.

## Data Flow
- `utils.py` provides shared data loading and prompt extraction utilities.
- Scripts operate on notebooks in the same directory to clean and standardize.

## Key Components
- API client setup (OpenAI, dotenv)
- Notebook mutation logic using nbformat
- Products/categories dataset helpers

## Usage Instructions
1. Activate Python env, install required libs.
2. Fill `.env` with OpenAI credentials.
3. Run scripts:
   ```bash
   python standardize_all_notebooks.py
   python fix_ui_notebooks.py
   python restore_context.py
   python test_moderation.py
   ```
4. Open notebooks to verify behavior.
