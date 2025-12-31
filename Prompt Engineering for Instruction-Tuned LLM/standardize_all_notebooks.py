import nbformat
import os

def fix_notebook(path):
    print(f"Processing {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # Standard components - includes function definitions in the import block
    import_block = """import os
import utils
import panel as pn
from openai import OpenAI
from dotenv import dotenv_values
from langchain_openai import ChatOpenAI

# ==============================
# 🔑 Load environment variables
# ==============================
env_values = dotenv_values(".env")

openai_api_key = env_values.get("OPENAI_API_KEY")
openai_api_base = env_values.get("OPENAI_API_BASE")
openai_api_name = env_values.get("OPENAI_API_NAME")

# Initialize Clients
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base
)

# Mock moderation for OpenRouter compatibility
if openai_api_base and "openrouter.ai" in openai_api_base:
    class MockResult(dict):
        def __getattr__(self, name): return self.get(name)
    class MockModeration(dict):
        def __init__(self):
            res = MockResult(flagged=False, categories={}, category_scores={})
            super().__init__(results=[res])
        @property
        def results(self): return self["results"]
    client.moderations.create = lambda *args, **kwargs: MockModeration()

chat = ChatOpenAI(
    model_name=openai_api_name, 
    openai_api_key=openai_api_key, 
    openai_api_base=openai_api_base,
    temperature=0.7
)
pn.extension()

# ==============================
# 🔧 Helper Functions
# ==============================
def get_completion(prompt, model=openai_api_name, temperature=0, max_tokens=500):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

def get_completion_from_messages(messages, model=openai_api_name, temperature=0, max_tokens=500):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content"""

    for cell in nb.cells:
        if cell.cell_type == 'code':
            content = cell.source
            # Check if this cell contains imports
            is_import_cell = ('from openai import OpenAI' in content or 
                             'import openai' in content or 
                             'ChatOpenAI(' in content or 
                             'dotenv_values' in content or
                             'UserSecretsClient' in content or
                             ('import panel' in content and 'pn.extension' in content))
            
            if is_import_cell:
                cell.source = import_block
            
            # Remove standalone function definition cells since they're now in import block
            if ('def get_completion(' in content or 'def get_completion_from_messages(' in content):
                # Check if this is ONLY function definitions
                lines = content.strip().split('\n')
                is_only_func_def = all(
                    line.strip() == '' or 
                    line.strip().startswith('def ') or 
                    line.strip().startswith('messages =') or
                    line.strip().startswith('response =') or
                    line.strip().startswith('return ') or
                    line.startswith('    ') or
                    line.startswith('#')
                    for line in lines
                )
                if is_only_func_def and 'def get_completion' in content:
                    cell.source = "# Function definitions moved to setup cell above"

    with open(path, 'w', encoding='utf-8') as f:
        nbformat.write(nb, f)

if __name__ == "__main__":
    notebooks = [f for f in os.listdir('.') if f.endswith('.ipynb')]
    for nb in notebooks:
        fix_notebook(nb)
