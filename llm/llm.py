import os
from dotenv import load_dotenv
from groq import Groq
from llm.vector_store import search

load_dotenv()

client = Groq(api_key=os.getenv("API_KEY"))

MODEL = "llama-3.1-8b-instant"

def query_llm(prompt):

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful customer support assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    return response.choices[0].message.content.strip()

def classify_intent(query):

    prompt = f"""
Classify intent:

1 knowledge
2 application_status
3 failed_transaction
4 other

Query: {query}

Return only number.
"""

    return query_llm(prompt).strip()

def answer_kb(query):
    print(query)

    docs = search(query)
    print(docs[0][:500] if docs else "NO DOCS")

    context = "\n".join(docs)

    prompt = f"""
Answer using context.

Context:
{context}

Question:
{query}
"""

    return query_llm(prompt)