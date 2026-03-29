import os
import re
import json
import backend.utils.constants as const
from llm.llm import query_llm

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

def get_path(filename):
    return os.path.join(DATA_DIR, filename)

def load_file(filename):
    try:
        with open(get_path(filename)) as f:
            return json.load(f)
    except:
        return json.dumps({})

def load_config():
    return load_file(const.CONFIG_FILE)

def load_mistake():
    return load_file(const.MISTAKES_FILE)

def load_agent():
    return load_file(const.AGENT_FILE)

def save_file(filename, data):
    try:
        with open(get_path(filename), "w") as f:
            json.dump(data, f, indent=2)
    except:
        pass

def save_mistake(data):
    mistakes = load_mistake()
    mistakes.append(data)
    return save_file(const.MISTAKES_FILE, mistakes)

def check_mistakes(query, agent_name=None):
    mistakes = load_file("mistakes.json")

    # reverse order to prioritize latest fixes
    for m in reversed(mistakes):
        if agent_name and m.get("agent") != agent_name:
            continue
        if query in m["question"] or m["question"] in query:
            return m.get("corrected_response")

    return None

def extract_id(text):
    match = re.search(r"\d+", text)
    return match.group() if match else None

def get_agent(name):
    agents = load_agent()
    for a in agents:
        if a["name"] == name:
            return a
    return None

def agent_exists(name):
    return get_agent(name) is not None

def generate_agent_config(name, instructions):
    prompt = f"""
You are configuring a chatbot agent.

Agent name: {name}

Instructions:
{instructions}

Decide:
- tools needed: application_status, transaction_status, kb
- behavior rules

Return JSON:
{{
  "name": "{name}",
  "instructions": "...",
  "tools": [...],
  "self_improve": true
}}
"""

    res = query_llm(prompt)

    try:
        config = json.loads(res)
    except:
        config = {
            "name": name,
            "instructions": instructions,
            "tools": ["kb"],
            "self_improve": True
        }

    return config
