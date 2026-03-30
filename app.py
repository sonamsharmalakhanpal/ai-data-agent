import streamlit as st
from agent import ask_agent

st.title("AI Data Analyst Agent")

query = st.text_input("Ask your data question:")

if query:
    result = ask_agent(query)
    st.write(result)