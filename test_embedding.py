import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found.")

client = genai.Client(api_key=api_key)

text = "Employees are entitled to annual leave."

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=text,
    config=types.EmbedContentConfig(
        task_type="RETRIEVAL_DOCUMENT"
    )
)

embedding = result.embeddings[0].values

print("Embedding generated successfully!")
print("Embedding dimensions:", len(embedding))
print("First 10 values:")
print(embedding[:10])