# Prompt Engineerings Repository

## Project Overview

A collection of hands-on notebooks, scripts, and resources for prompt engineering, LangChain, and instruction-tuned LLM workflows. This workspace spans three main modules:
- `Hands-On LangChain`
- `Prompt Engineering`
- `Prompt Engineering for Instruction-Tuned LLM`

This repo is designed for learning and prototyping around LLM patterns.

## Architecture Diagram (text)

Root
├─ Hands-On LangChain
│  └─ notebooks + requirements
├─ Prompt Engineering
│  └─ training and learning notebooks
└─ Prompt Engineering for Instruction-Tuned LLM
   ├─ helper scripts (`fix_ui_notebooks.py`, etc.)
   ├─ utils and data
   └─ notebooks

## Execution Pipeline

1. Use notebooks to experiment with prompts and LangChain components.
2. Use helper scripts to standardize/repair notebooks (`standardize_all_notebooks.py`, `fix_ui_notebooks.py`).
3. Use shared utilities in `utils.py` for dataset loading and LLM calls.

## Setup Instructions

1. Install Python dependencies (for LLM scripts):
   ```bash
   pip install -r "Hands-On LangChain/requirements.txt"
   pip install nbformat python-dotenv openai panel langchain-openai
   ```
2. Create `.env` in root or project folder with:
   ```ini
   OPENAI_API_KEY=your_api_key
   OPENAI_API_BASE=https://api.openai.com/v1
   OPENAI_API_NAME=gpt-4o-mini
   ```
3. Run helper scripts from `Prompt Engineering for Instruction-Tuned LLM`:
   ```bash
   python fix_ui_notebooks.py
   python standardize_all_notebooks.py
   python restore_context.py
   python test_moderation.py
   ```

## Dependencies

- Python 3.8+
- nbformat
- openai
- python-dotenv
- panel
- langchain-openai

## Example Usage

- Open any .ipynb and run cells interactively.
- For scripted notebook cleanup:
  ```bash
  cd "Prompt Engineering for Instruction-Tuned LLM"
  python standardize_all_notebooks.py
  python fix_ui_notebooks.py
  ```

## Checklist: Documentation findings

- Added module-level docstrings in scripts.
- Added README files for each folder.
- Notebooks are not modified except via described scripts.
