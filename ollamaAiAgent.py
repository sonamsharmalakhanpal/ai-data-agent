
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

STRICTLY follow these steps and output format:
1. Convert the user question into a correct SQL query.
2. Execute the SQL query.
3. Return ONLY the following, in this exact format (no extra text, no markdown, no code blocks):

SQL Query:
<query>

Result:
<actual result>

Explanation:
<short, crisp business explanation>

Rules:
- Only use available tables
- Do not hallucinate columns
- Do NOT add any extra commentary, markdown, or formatting
- Output must start with 'SQL Query:' and follow the format exactly
- If you do not know the answer, say so clearly in the Explanation
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