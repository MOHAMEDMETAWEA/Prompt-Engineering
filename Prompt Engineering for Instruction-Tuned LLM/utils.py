"""Utilities for LLM-powered customer service demos and notebooks.

Purpose:
- Provide helper functions to call chat completions, parse model outputs,
- Load and manage example product and category datasets,
- Offer convenience wrappers for extracting products/categories from free text.

Main components:
- OpenAI client initialization with optional OpenRouter moderation shim,
- Data loaders/creators for products and categories JSON files,
- Parsing utilities to robustly interpret LLM outputs,
- Convenience functions to format results for display.

Dependencies:
- openai: Chat completions API client
- python-dotenv: Load API keys and endpoints from .env
- json, os, collections: Standard library utilities
"""
import json
import os
from openai import OpenAI
from dotenv import dotenv_values
from collections import defaultdict

# ==============================
# 🔑 Load environment variables
# ==============================
env_values = dotenv_values(".env")
openai_api_key = env_values.get("OPENAI_API_KEY")
openai_api_base = env_values.get("OPENAI_API_BASE")
openai_api_name = env_values.get("OPENAI_API_NAME", "openai/gpt-4o-mini")

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

products_file = 'products.json'
categories_file = 'categories.json'

def get_completion_from_messages(messages, 
                                 model=openai_api_name, 
                                 temperature=0, max_tokens=500):
    """Call chat completions with a messages list.

    Parameters:
    - messages: list[dict] with role/content pairs for the chat
    - model: model identifier/name from .env (default: openai_api_name)
    - temperature: sampling temperature controlling creativity
    - max_tokens: maximum tokens in completion

    Returns:
    - str: assistant message content from the first choice
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
    )
    return response.choices[0].message.content

def create_categories():
    """Create default customer service categories and persist to JSON.

    Returns:
    - dict: mapping category -> list of subtopics
    """
    categories_dict = {
      'Billing': [
                'Unsubscribe or upgrade',
                'Add a payment method',
                'Explanation for charge',
                'Dispute a charge'],
      'Technical Support':[
                'General troubleshooting',
                'Device compatibility',
                'Software updates'],
      'Account Management':[
                'Password reset',
                'Update personal information',
                'Close account',
                'Account security'],
      'General Inquiry':[
                'Product information',
                'Pricing',
                'Feedback',
                'Speak to a human']
    }
    with open(categories_file, 'w') as file:
        json.dump(categories_dict, file)
    return categories_dict

def get_categories():
    """Load categories from JSON or create defaults when missing.

    Returns:
    - dict: categories structure
    """
    if not os.path.exists(categories_file):
        return create_categories()
    with open(categories_file, 'r') as file:
            categories = json.load(file)
    return categories

def get_product_list():
    """Return a flat list of product names."""
    products = get_products()
    return list(products.keys())

def get_products_and_category():
    """Aggregate product names by category.

    Returns:
    - dict[str, list[str]]: category -> list of product names
    """
    products = get_products()
    products_by_category = defaultdict(list)
    for product_name, product_info in products.items():
        category = product_info.get('category')
        if category:
            products_by_category[category].append(product_info.get('name'))
    return dict(products_by_category)

def get_products():
    """Load products from JSON or create defaults when missing.

    Returns:
    - dict[str, dict]: product name -> product info
    """
    if not os.path.exists(products_file):
        return create_products()
    with open(products_file, 'r') as file:
        products = json.load(file)
    return products

def find_category_and_product(user_input, products_and_category):
    """Ask the LLM to extract categories and products from text.

    Parameters:
    - user_input: str free-text customer query
    - products_and_category: dict allowed products grouped by category

    Returns:
    - str: model output (JSON-like) describing categories/products
    """
    delimiter = "####"
    system_message = f"""
    You will be provided with customer service queries. The customer service query will be delimited with {delimiter} characters.
    Output a python list of json objects, where each object has the following format:
        'category': <one of Computers and Laptops, Smartphones and Accessories, Televisions and Home Theater Systems, Gaming Consoles and Accessories, Audio Equipment, Cameras and Camcorders>,
    OR
        'products': <a list of products that must be found in the allowed products below>
    The allowed products are provided in JSON format: {products_and_category}
    """
    messages = [
        {'role':'system', 'content': system_message},
        {'role':'user', 'content': f"{delimiter}{user_input}{delimiter}"},
    ]
    return get_completion_from_messages(messages)

def find_category_and_product_only(user_input, products_and_category):
    """Variant that requests only the extracted list from the LLM.

    Parameters:
    - user_input: str free-text customer query
    - products_and_category: dict allowed products grouped by category

    Returns:
    - str: minimal list of objects (as text) from the model
    """
    delimiter = "####"
    system_message = f"""
    You will be provided with customer service queries. The query will be delimited with {delimiter}.
    Output a python list of objects with category or products.
    Allowed products: {products_and_category}
    Only output the list of objects, nothing else.
    """
    messages = [
        {'role':'system', 'content': system_message},
        {'role':'user', 'content': f"{delimiter}{user_input}{delimiter}"},
    ]
    return get_completion_from_messages(messages)

def get_products_from_query(user_msg):
    """Convenience wrapper returning extracted products/categories for a query."""
    products_and_category = get_products_and_category()
    return find_category_and_product(user_msg, products_and_category)

def get_product_by_name(name):
    """Lookup a product dict by its display name."""
    products = get_products()
    return products.get(name, None)

def get_products_by_category(category):
    """Return all product dicts belonging to a given category."""
    products = get_products()
    return [product for product in products.values() if product["category"] == category]

def get_mentioned_product_info(data_list):
    """Expand extracted items to full product dicts.

    Parameters:
    - data_list: list of dicts with keys 'products' or 'category'

    Returns:
    - list[dict]: product objects relevant to the query
    """
    product_info_l = []
    if data_list is None: return product_info_l
    for data in data_list:
        try:
            if "products" in data:
                for product_name in data["products"]:
                    product = get_product_by_name(product_name)
                    if product: product_info_l.append(product)
            elif "category" in data:
                category_products = get_products_by_category(data["category"])
                product_info_l.extend(category_products)
        except Exception as e: print(f"Error: {e}")
    return product_info_l

def read_string_to_list(input_string):
    """Parse a model-produced string into a Python list.

    Attempts to robustly clean common LLM formatting artifacts
    like fenced code blocks and single quotes before json.loads.

    Parameters:
    - input_string: str representation of a list of dicts

    Returns:
    - list | None: parsed list or None on failure
    """
    if not input_string: return None
    try:
        # Simple cleanup for common LLM output issues
        s = input_string.strip()
        if s.startswith("```python"): s = s[9:]
        if s.startswith("```json"): s = s[7:]
        if s.endswith("```"): s = s[:-3]
        s = s.strip().replace("'", "\"")
        return json.loads(s)
    except:
        return None

def generate_output_string(data_list):
    """Format product information as pretty-printed JSON lines.

    Parameters:
    - data_list: list of dicts with 'products' or 'category'

    Returns:
    - str: newline-separated JSON snippets for display
    """
    output_string = ""
    if data_list is None: return output_string
    for data in data_list:
        try:
            if "products" in data:
                for product_name in data["products"]:
                    product = get_product_by_name(product_name)
                    if product: output_string += json.dumps(product, indent=4) + "\n"
            elif "category" in data:
                for product in get_products_by_category(data["category"]):
                    output_string += json.dumps(product, indent=4) + "\n"
        except: pass
    return output_string

def create_products():
    """Create a minimal set of demo products and persist to JSON.

    Returns:
    - dict[str, dict]: product name -> product info
    """
    products = {
        "TechPro Ultrabook": {"name": "TechPro Ultrabook", "category": "Computers and Laptops", "brand": "TechPro", "price": 799.99, "description": "A sleek and lightweight ultrabook."},
        "BlueWave Gaming Laptop": {"name": "BlueWave Gaming Laptop", "category": "Computers and Laptops", "brand": "BlueWave", "price": 1199.99, "description": "High-performance gaming laptop."},
        "SmartX ProPhone": {"name": "SmartX ProPhone", "category": "Smartphones and Accessories", "brand": "SmartX", "price": 899.99, "description": "Powerful smartphone."},
        "CineView 4K TV": {"name": "CineView 4K TV", "category": "Televisions and Home Theater Systems", "brand": "CineView", "price": 599.99, "description": "Stunning 4K TV."},
        "FotoSnap DSLR Camera": {"name": "FotoSnap DSLR Camera", "category": "Cameras and Camcorders", "brand": "FotoSnap", "price": 599.99, "description": "Versatile DSLR camera."}
    }
    with open(products_file, 'w') as file:
        json.dump(products, file)
    return products

if __name__ == "__main__":
    # Example script usage: populate demo datasets if missing.
    # TODO: Consider adding CLI flags to skip/force recreation.
    create_products()
    create_categories()
