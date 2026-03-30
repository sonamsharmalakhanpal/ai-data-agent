from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv


# API key
os.environ["OPENAI_API_KEY"] = "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"
# load_dotenv()
# os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


# DB connection (SQLite)
db = SQLDatabase.from_uri("sqlite:///data.db")

# LLM
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Agent
agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    verbose=True
)

# Run query
response = agent_executor.invoke({
    "input": "What is total revenue from closed deals?"
})

print(response["output"])