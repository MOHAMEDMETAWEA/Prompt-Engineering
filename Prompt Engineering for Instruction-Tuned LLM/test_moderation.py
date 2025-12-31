from openai import OpenAI
from dotenv import dotenv_values
import traceback

env_values = dotenv_values(".env")
openai_api_key = env_values["OPENAI_API_KEY"]
openai_api_base = env_values.get("OPENAI_API_BASE")

client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base
)

print(f"Testing moderation with base_url: {openai_api_base}")
try:
    response = client.moderations.create(input="I want to kill someone")
    print(f"Response type: {type(response)}")
    print(f"Response content: {response}")
except Exception as e:
    print(f"Error calling moderations: {e}")
    traceback.print_exc()
