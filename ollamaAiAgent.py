
import sys
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_ollama import ChatOllama


# DB
db = SQLDatabase.from_uri("sqlite:///data.db")

# LLM
llm = ChatOllama(model="phi")

# Custom Prompt
CUSTOM_PREFIX = """
You are an expert data analyst.

Follow these steps STRICTLY:
1. Convert the user question into a correct SQL query.
2. Execute the SQL query.
3. Return response in this format:

SQL Query:
<query>

Result:
<actual result>

Explanation:
<short, crisp business explanation>

Rules:
- Only use available tables
- Do not hallucinate columns
- Keep explanation short and clear
"""

# Agent
agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True,
    prefix=CUSTOM_PREFIX,
    handle_parsing_errors=True
)

def ask_agent(query):
    try:
        response = agent_executor.invoke({
            "input": query
        })
        return response["output"]
    except Exception as e:
        print("Agent error:", e)
        return None


# Test
if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "What is total revenue from closed deals?"
    print(ask_agent(query))