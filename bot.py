import json
from fastapi import FastAPI

import backend.utils.constants as const
from backend.utils.utils import *
from backend.utils.mock_functions import get_application_status, get_transaction_status
from backend.web_scraper import scrape_kb
from llm.vector_store import build_index, search
from llm.llm import query_llm, answer_kb

app = FastAPI()
user_sessions = {}

@app.on_event("startup")
def load_kb():
    url = None
    config = load_config()
    try:
        url = config["kb_url"]
    except KeyError:
        print(f"kb_url key does not exist. Full config json as follows:\n{config}")

    print(f"Loading KB from: {url}")

    docs = scrape_kb(url)
    build_index(docs)

    print(f"Loaded {len(docs)} documents into KB")

@app.post("/chat")
def chat(msg: dict):
    query = msg["text"]
    user_id = "default_user"
    config = load_config()
    agent = None
    try:
        agent_name = config["active_agent"]
        agent = get_agent(agent_name) if agent_name else None
    except KeyError:
        print(f"active agent key does not exist. Full config json as follows:\n{config}")

    print("Query:", query)

    # Priotizing learning for previously wrong responses
    fix = check_mistakes(query, agent_name)
    if fix:
        return {"response": fix}

    if not agent:
        # Additional instructions (card application status)
        if user_sessions.get(user_id) == "awaiting_application_id":
            user_sessions.pop(user_id)
            uid = extract_id(query)

            if not uid:
                return {"response": "Invalid user ID. Please provide a numeric ID."}

            return {"response": get_application_status(uid)}

        # Additional instructions (transaction status)
        if user_sessions.get(user_id) == "awaiting_txn_id":
            user_sessions.pop(user_id)
            txn_id = query.strip()
            
            return {"response": get_transaction_status(txn_id)}

        # Additional instructions (card application status)
        if "application" in query and "status" in query:
            user_sessions[user_id] = "awaiting_application_id"
            return {"response": "Please provide your user ID."}

        # Additional instructions (transaction status)
        if "transaction" in query and ("fail" in query or "decline" in query):
            user_sessions[user_id] = "awaiting_txn_id"
            return {"response": "Please provide your transaction ID."}

        kb_answer = answer_kb(query)
        if "not sure" in kb_answer.lower() or len(kb_answer.strip()) < 20:
            return {"response": "I'm not sure. Please contact support."}

        return {"response": kb_answer}

    docs = search(query, namespace=agent_name)
    context = "\n".join(docs)
    instructions = None
    if agent:
        instructions = agent.get("instructions")

    prompt = f"""
{instructions}

Context:
{context}

Question:
{query}
"""

    return {"response": query_llm(prompt)}

@app.post("/report")
def report(data: dict):

    question = data["question"]
    wrong_answer = data["answer"]
    config = load_config()
    agent_name = config.get("active_agent") if config else None

    print("Mistake reported:", question)

    prompt = f"""
The chatbot gave a wrong answer. Fix the response.

Question: {question}
Wrong Answer: {wrong_answer}

Provide a corrected, helpful, and concise answer.
Only return the improved answer.
"""

    corrected_answer = query_llm(prompt)

    save_mistake({
        "agent": agent_name,
        "question": question,
        "wrong_response": wrong_answer,
        "corrected_response": corrected_answer
    })

    return {"status": "saved", "corrected_response": corrected_answer}

@app.get("/mistakes")
def mistakes():
    return load_mistake()

@app.post("/update_kb")
def update_kb(data: dict):

    url = data["kb_url"]
    print("Updating KB from:", url)
    docs = scrape_kb(url)
    print(f"Scraped {len(docs)} docs")
    build_index(docs)

    return {"status": "kb_updated", "docs": len(docs)}

@app.get("/config")
def config():
    config = load_config()
    return config

@app.post("/update_config")
def update_config(data: dict):
    save_file(const.CONFIG_FILE, data)

@app.get("/agents")
def list_agents():
    agents = load_agent()
    return {"agents": [a["name"] for a in agents]}

@app.post("/create_agent")
def create_agent(data: dict):

    name = data["name"]
    instructions = data["instructions"]

    if agent_exists(name):
        return {"error": "Agent name already exists"}

    agent = generate_agent_config(name, instructions)
    build_index(instructions, namespace=name)

    agents = load_agent()
    agents.append(agent)
    save_file(const.AGENT_FILE, agents)

    return {"status": "created", "agent": name}