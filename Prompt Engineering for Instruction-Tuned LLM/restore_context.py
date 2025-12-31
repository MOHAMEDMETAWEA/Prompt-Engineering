import nbformat

def restore_context_building_chatbot(path):
    print(f"Restoring context in {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    pizzabot_context = """context = [ {'role':'system', 'content':\"\"\"
You are OrderBot, an automated service to collect orders for a pizza restaurant. \\
You first greet the customer, then collects the order, \\
and then asks if it's a pickup or delivery. \\
You wait to collect the entire order, then summarize it and check for a final \\
time if the customer wants to add anything else. \\
If it's a delivery, you ask for an address. \\
Finally you collect the payment.\\
Make sure to clarify all options, extras and sizes to uniquely \\
identify the item from the menu.\\
You respond in a short, very conversational friendly style. \\
The menu includes \\
pepperoni pizza  12.95, 10.00, 7.00 \\
cheese pizza   10.95, 9.25, 6.50 \\
eggplant pizza   11.95, 9.75, 6.75 \\
fries 4.50, 3.50 \\
greek salad 7.25 \\
Toppings: \\
extra cheese 2.00, \\
mushrooms 1.50 \\
sausage 3.00 \\
canadian bacon 3.50 \\
AI sauce 1.50 \\
peppers 1.00 \\
Drinks: \\
coke 3.00, 2.00, 1.00 \\
sprite 3.00, 2.00, 1.00 \\
bottled water 5.00 \\
\"\"\"} ]  # accumulate messages
panels = [] # collect display"""

    # Find and fix the collect_messages function cell to include context initialization
    updated = False
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == 'code' and 'def collect_messages(_):' in cell.source:
            # Check if this cell already has context defined
            if 'context =' not in cell.source:
                # Add context and panels before the function
                cell.source = pizzabot_context + "\n\n" + cell.source
                updated = True
                print(f"  Added context before collect_messages function")
                break
    
    if updated:
        with open(path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)

def restore_context_customer_service(path):
    print(f"Restoring context in {path}...")
    with open(path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)
    
    # The context is already in the UI dashboard cell for this notebook (lines 1660-1662)
    # Just verify it exists
    for cell in nb.cells:
        if cell.cell_type == 'code' and 'context = [' in cell.source and "Service Assistant" in cell.source:
            print(f"  Context already exists")
            return
    
    print(f"  Context not found - notebook may need manual review")

if __name__ == "__main__":
    restore_context_building_chatbot("building-chatbot-with-prompt-engineering.ipynb")
    restore_context_customer_service("end-to-end-customer-service-system-with-prompt.ipynb")
