import sys
import os
import json
import asyncio
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Ensure the correct agents SDK is found
user_site = os.path.expanduser(r"~\AppData\Roaming\Python\Python314\site-packages")
if os.path.exists(user_site) and user_site not in sys.path:
    # Insert at the beginning to avoid conflicts with local files or other versions
    sys.path.insert(0, user_site)

from agents import Agent, Runner, function_tool
from agents.mcp import MCPServerStdio, MCPServerStdioParams
from sql_validator import SQLValidator
from schema_retriever import SchemaRetriever

# Load environment variables
load_dotenv()

# Initialize components
db_url = os.getenv("POSTGRES_URL")
schema_retriever = SchemaRetriever(db_url)
validator = SQLValidator()

# Define the PostgreSQL MCP Server (stdio transport)
postgres_mcp = MCPServerStdio(
    params=MCPServerStdioParams(
        command=os.getenv("POSTGRES_MCP_COMMAND", "npx"),
        args=json.loads(os.getenv("POSTGRES_MCP_ARGS", '[]'))
    )
)

@function_tool
async def validate_sql(sql: str) -> str:
    """
    Validates a generated SQL query for safety and read-only compliance.
    Returns the validated SQL string if safe, or an error message starting with 'Error:'.
    """
    try:
        safe_sql = validator.validate(sql)
        return safe_sql
    except Exception as e:
        return f"Error during validation: {e}"

@function_tool
def get_schema(search_query: str = "") -> str:
    """
    Retrieves available database tables and their columns.
    Provide a search term (like 'products' or 'orders') or leave empty to see all tables.
    """
    return schema_retriever.get_relevant_schema_prompt(search_query)

async def main():
    print("Connecting to PostgreSQL MCP server...")
    try:
        await postgres_mcp.connect()
        print("MCP server connected successfully.")
    except Exception as e:
        print(f"Error connecting to MCP server: {e}")
        return

    # Define the Agent inside main to include MCP tools correctly via mcp_servers
    sql_agent = Agent(
        name="SQLAnalyticsAgent",
        instructions=(
            "You are a professional SQL Data Analyst assistant.\n"
            "Your goal is to answer user questions by querying a PostgreSQL database.\n\n"
            "CRITICAL RULES:\n"
            "1. ALWAYS start by calling `get_schema` to understand the available tables and columns.\n"
            "2. Generate a valid PostgreSQL SELECT query based ON THE SCHEMA. Do not guess column names.\n"
            "3. BEFORE executing any query, you MUST call `validate_sql`. Pass the raw SQL string as the argument.\n"
            "4. IMPORTANT: If `validate_sql` returns a string that does NOT start with 'Error:', then use THAT returned string to call the MCP `query` tool.\n"
            "5. If `validate_sql` returns an 'Error:', explain the issue to the user and refine your query.\n"
            "6. Always include a LIMIT 100 in your queries if not already present.\n"
            "7. After getting the data from the `query` tool, provide a concise summary or table to the user."
        ),
        tools=[
            get_schema, 
            validate_sql
        ],
        mcp_servers=[postgres_mcp]
    )

    runner = Runner()
    
    print("\nSQL Analytics Agent is ready. Type 'exit' to quit.")
    while True:
        try:
            user_input = await asyncio.to_thread(input, "You: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            
            if not user_input.strip():
                continue
                
            result = await runner.run(sql_agent, user_input)
            print(f"Assistant: {result.final_output}")
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
