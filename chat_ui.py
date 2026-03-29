import streamlit as st
import requests
import random

if "history" not in st.session_state:
    st.session_state.history = []

st.title("Customer Support")
user_input = st.text_input("Ask a question")

if st.button("Send"):

    r = requests.post(
        "http://localhost:8000/chat",
        json={
            "text": user_input
        }
    )

    answer = r.json()["response"]

    st.session_state.history.append((user_input, answer))


for i, (q, a) in enumerate(reversed(st.session_state.history)):
    st.write("User:", q)
    st.write("Atome:", a)

    if st.button("Report mistake", key=f"report_{i}"):

        requests.post(
            "http://localhost:8000/report",
            json={"question": q, "answer": a}
        )

        st.warning("Reported")