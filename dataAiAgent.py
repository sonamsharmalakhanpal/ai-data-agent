import os
import re

from sqlalchemy import create_engine, text
from langchain_ollama import ChatOllama


# ============================================================
# DATABASE
# ============================================================

DATABASE_URL = "sqlite:///data.db"

engine = create_engine(
    DATABASE_URL,
    echo=False
)


# ============================================================
# OLLAMA / LOCAL OPEN-SOURCE LLM
# ============================================================

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

llm = ChatOllama(
    model=OLLAMA_MODEL,
    temperature=0
)


# ============================================================
# PROMPT
# ============================================================

SQL_PROMPT = """
You are an expert SQL data analyst.

Your job is to convert the user's question into a SQLite SQL query.

IMPORTANT RULES:

1. Generate ONLY a SQLite SQL query.
2. Do not generate explanations.
3. Do not generate markdown.
4. Do not use ```sql.
5. Do not invent tables.
6. Do not invent columns.
7. Use only the tables and columns provided in the database schema.
8. The query must be valid SQLite syntax.
9. For aggregation questions, use appropriate SQL functions such as SUM, COUNT, AVG, MIN or MAX.
10. For "total revenue", calculate the appropriate SUM of the revenue column.
11. Return only the SQL statement.

DATABASE SCHEMA:

{schema}

USER QUESTION:

{question}
"""


# ============================================================
# GET DATABASE SCHEMA
# ============================================================

def get_database_schema():
    """
    Read the SQLite database schema so the LLM knows
    which tables and columns actually exist.
    """

    schema = []

    with engine.connect() as connection:

        tables = connection.execute(
            text("""
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
        ).fetchall()

        for table in tables:

            table_name = table[0]

            columns = connection.execute(
                text(f'PRAGMA table_info("{table_name}")')
            ).fetchall()

            schema.append(f"Table: {table_name}")

            for column in columns:
                column_name = column[1]
                column_type = column[2]

                schema.append(
                    f"  - {column_name} ({column_type})"
                )

    return "\n".join(schema)


# ============================================================
# CLEAN LLM SQL RESPONSE
# ============================================================

def clean_sql(response):
    """
    Remove markdown/code fences if the model happens
    to return them.
    """

    sql = response.content.strip()

    sql = re.sub(
        r"```sql",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = sql.replace("```", "")

    return sql.strip()


# ============================================================
# VALIDATE SQL
# ============================================================

def validate_sql(sql):
    """
    Basic safety check.

    This POC should only allow SELECT queries.
    """

    sql_clean = sql.strip().lower()

    if not sql_clean.startswith("select"):
        raise ValueError(
            "Only SELECT queries are allowed."
        )

    forbidden = [
        "insert ",
        "update ",
        "delete ",
        "drop ",
        "alter ",
        "create ",
        "replace ",
        "truncate "
    ]

    for keyword in forbidden:

        if keyword in sql_clean:
            raise ValueError(
                f"Unsafe SQL detected: {keyword.strip()}"
            )

    return True


# ============================================================
# GENERATE SQL
# ============================================================

def generate_sql(user_question):

    schema = get_database_schema()

    prompt = SQL_PROMPT.format(
        schema=schema,
        question=user_question
    )

    response = llm.invoke(prompt)

    sql = clean_sql(response)

    validate_sql(sql)

    return sql


# ============================================================
# EXECUTE SQL
# ============================================================

def execute_sql(sql):

    with engine.connect() as connection:

        result = connection.execute(
            text(sql)
        )

        rows = result.fetchall()

        columns = result.keys()

    return {
        "columns": list(columns),
        "rows": [list(row) for row in rows]
    }


# ============================================================
# BUSINESS EXPLANATION
# ============================================================

def generate_explanation(
        user_question,
        sql,
        result
):

    prompt = f"""
You are a business data analyst.

User question:
{user_question}

SQL:
{sql}

Result:
{result}

Give a short, clear business explanation of the result.

Do not generate SQL.
Do not use markdown.
Keep the explanation concise.
"""

    response = llm.invoke(prompt)

    return response.content.strip()


# ============================================================
# AI DATA AGENT
# ============================================================

def ask_agent(user_question):

    try:

        # 1. Generate SQL
        sql = generate_sql(user_question)

        # 2. Execute SQL
        result = execute_sql(sql)

        # 3. Generate explanation
        explanation = generate_explanation(
            user_question,
            sql,
            result
        )

        return {
            "SQL Query": sql,
            "Result": result,
            "Explanation": explanation
        }

    except Exception as e:

        return {
            "SQL Query": None,
            "Result": None,
            "Explanation": f"Error: {str(e)}"
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    import sys

    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = (
            "What is total revenue from closed deals?"
        )

    response = ask_agent(user_query)

    print("\nSQL Query:")
    print(response["SQL Query"])

    print("\nResult:")
    print(response["Result"])

    print("\nExplanation:")
    print(response["Explanation"])