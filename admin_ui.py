import streamlit as st
import json
import requests

def get_agents():
    try:
        r = requests.get("http://localhost:8000/agents")
        return r.json().get("agents", [])
    except:
        return []

def get_config():
    try:
        r = requests.get("http://localhost:8000/config")
        return r.json()
    except:
        return []

def save_config(data):
    requests.post("http://localhost:8000/update_config",
      json=data
    )

st.title("Admin Panel")

config = get_config()
agents = get_agents()
agent_options = ["No Agent"] + agents

selected_agent = st.selectbox("Active Agent", agent_options)
if config.get('active_agent'):
    st.caption(f"Active Agent: {config.get('active_agent')}")
else:
    st.caption(f"No agent selected.")

kb = st.text_input("Knowledge Base URL", config["kb_url"])

instructions = st.text_area(
    "Additional Instructions",
    config["instructions"]
)

if st.button("Save"):
    config["kb_url"] = kb
    config["instructions"] = instructions
    config["active_agent"] = (
        None if selected_agent == "No Agent" else selected_agent
    )
    r = save_config(config)

    r = requests.post(
        "http://localhost:8000/update_kb",
        json={"kb_url": kb}
    )

    docs = r.json()["docs"]
    st.success(f"Updated KB. KB has {docs} data points")

st.header("Create Agent")

agent_name = st.text_input("Agent Name")
instructions = st.text_area("Instructions")

if st.button("Create Agent"):

    if not agent_name:
        st.error("Agent must have a name")

    else:

        r = requests.post(
            "http://localhost:8000/create_agent",
            json={
                "name": agent_name,
                "instructions": instructions
            }
        )

        st.success(f"Successfully created agent: {agent_name}")

st.header("Reported Mistakes")

r = requests.get("http://localhost:8000/mistakes")

for m in r.json():
    st.write("Affected agent:", m["agent"])
    st.write("Question:", m["question"])
    st.write("Response:", m["wrong_response"])
    st.write("Updated Response:", m["corrected_response"])
    st.write("---")