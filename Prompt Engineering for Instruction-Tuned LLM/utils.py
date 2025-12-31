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
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature, 
        max_tokens=max_tokens, 
    )
    return response.choices[0].message.content

def create_categories():
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
    if not os.path.exists(categories_file):
        return create_categories()
    with open(categories_file, 'r') as file:
            categories = json.load(file)
    return categories

def get_product_list():
    products = get_products()
    return list(products.keys())

def get_products_and_category():
    products = get_products()
    products_by_category = defaultdict(list)
    for product_name, product_info in products.items():
        category = product_info.get('category')
        if category:
            products_by_category[category].append(product_info.get('name'))
    return dict(products_by_category)

def get_products():
    if not os.path.exists(products_file):
        return create_products()
    with open(products_file, 'r') as file:
        products = json.load(file)
    return products

def find_category_and_product(user_input, products_and_category):
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
    products_and_category = get_products_and_category()
    return find_category_and_product(user_msg, products_and_category)

def get_product_by_name(name):
    products = get_products()
    return products.get(name, None)

def get_products_by_category(category):
    products = get_products()
    return [product for product in products.values() if product["category"] == category]

def get_mentioned_product_info(data_list):
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
    create_products()
    create_categories()
