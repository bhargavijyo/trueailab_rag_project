import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

emb = genai.embed_content(model="models/gemini-embedding-001", content="Hello", task_type="retrieval_document")
print(len(emb['embedding']))
