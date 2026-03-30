from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv


# API key
os.environ["OPENAI_API_KEY"] = "apikey"
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