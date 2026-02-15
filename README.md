# NLP SQL Agent

A conversational AI system designed to query PostgreSQL databases using natural language. This project leverages the OpenAI Agents SDK and Model Context Protocol (MCP) to provide a secure, schema-aware, and multi-turn data analytics experience.

## Features

- **Natural Language to SQL**: Translates user questions into syntactically correct PostgreSQL queries.
- **Dynamic Schema Retrieval (Schema-Agnostic)**: Automatically discovers database schema at runtime. This allows the agent to adapt to **any** table structure, columns, or data types within the PostgreSQL `public` schema without manual configuration.
- **SQL Safety Validator**: A mandatory layer that enforces read-only access and prevents dangerous operations (e.g., `DROP`, `DELETE`).
- **MCP Integration**: Executes queries via a PostgreSQL MCP server for standardized database interaction.
- **Multi-Turn Conversations**: Maintains context across multiple exchanges, allowing for follow-up questions and iterative data exploration.
- **Human-Readable Insights**: Summarizes raw data into clear, conversational responses.

## Project Structure

- `agent.py`: The main entry point for the conversational agent.
- `init_db.py`: Script to initialize and seed the PostgreSQL database.
- `setup_db.sql`: SQL script defining the database schema and initial data.
- `schema_retriever.py`: Handles dynamic retrieval of table and column metadata.
- `sql_validator.py`: Implements safety checks on generated SQL.
- `instructions.md`: Detailed system instructions and architecture overview.

## Setup

### Prerequisites

- Python 3.10 or higher
- PostgreSQL database
- Node.js (required for the PostgreSQL MCP server)
- `npx` (comes with Node.js)

### Installation

1. Clone the repository.
2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: Ensure `agents-sdk` and `psycopg2` are installed.)*
3. Create a `.env` file in the root directory and configure the following variables:
   ```env
   POSTGRES_URL=postgresql://username:password@localhost:5432/database_name
   POSTGRES_MCP_COMMAND=npx
   POSTGRES_MCP_ARGS=["-y", "@modelcontextprotocol/server-postgres", "--db-url", "postgresql://username:password@localhost:5432/database_name"]
   ```

### Database Initialization

Initialize the database schema and seed it with sample data:
```bash
python init_db.py
```

## Usage

Run the agent to start a conversational session:
```bash
python agent.py
```

Once running, you can ask questions like:
- "What are the total sales for each product category?"
- "Show me the top 5 customers by revenue."
- "Now group those sales by month." (Multi-turn context)

## Security

Security is a core principle of the NLP SQL Agent:
- **Read-Only Enforcement**: Only `SELECT` statements are permitted.
- **Validation Layer**: All generated SQL is parsed and validated against a whitelist of tables and columns before execution.
- **No Direct Access**: The LLM interacts with the database through controlled tools and validation layers.
- **Row Limiting**: Queries are automatically appended with `LIMIT 100` to prevent excessive data retrieval.
