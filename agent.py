import sys
import os
import json
import asyncio
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
    Returns the validated SQL string or an error message.
    """
    try:
        # Check for non-read-only keywords
        forbidden = ["INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE", "ALTER", "CREATE"]
        if any(word in sql.upper() for word in forbidden):
            return "Error: Only SELECT queries are allowed."
        
        safe_sql = validator.validate(sql)
        return safe_sql
    except Exception as e:
        return f"Validation Error: {e}"

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
            "You are a helpful data analytics assistant for a database.\n"
            "STEP 1: Always use `get_schema` first to see which tables and columns are available.\n"
            "STEP 2: Based on the schema, generate a read-only PostgreSQL query. Always include a LIMIT 100.\n"
            "STEP 3: ALWAYS call `validate_sql` with your generated query before executing it.\n"
            "STEP 4: If `validate_sql` confirms the query is safe, use the `query` tool from the MCP server to execute it.\n"
            "STEP 5: Present the data to the user in a clear summary. If no results found, let them know."
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
