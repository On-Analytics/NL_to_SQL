# NLP SQL Agent: System Instructions & Architecture

This document serves as the primary technical reference for the **NLP SQL Agent**, detailing its architecture, operational guidelines, and system instructions for AI maintenance and interaction.

---

## 1. System Objective
The NLP SQL Agent is a conversational AI interface designed to bridge the gap between human language and structured databases. It allows users to query a PostgreSQL database using natural language, providing:
- **Schema-Agnostic Querying**: Dynamic discovery of any database structure.
- **Natural Language Translation**: Accurate conversion of intent into complex SELECT statements.
- **Safety First Architecture**: Strict read-only enforcement and query validation.

---

## 2. Architecture Overview
The system follows a modular architecture centered around the **OpenAI Agents SDK** and **Model Context Protocol (MCP)**.

### Core Components Hierarchy:
1.  **Orchestrator (`agent.py`)**: Uses the Agents SDK to manage multi-turn conversations, tool calling, and workflow execution.
2.  **Schema Retriever (`schema_retriever.py`)**: Queries `information_schema` at runtime to feed the LLM with up-to-date table and column metadata.
3.  **SQL Validator (`sql_validator.py`)**: A safety firewall that parses generated SQL using regex to ensure only `SELECT` statements are executed and enforces a `LIMIT 100`.
4.  **MCP PostgreSQL Server**: A standard bridge that executes the validated SQL against the physical database via stdio transport.

---

## 3. Operational Workflow (SOP)
The Agent follows a mandatory 5-step process for every query:

| Step | Component | Action |
| :--- | :--- | :--- |
| **1. Grounding** | `get_schema` | Retrieve table names and column types relevant to the user's query. |
| **2. Generation** | LLM | Draft a PostgreSQL query. *Note: Avoid passing markdown backticks to tools.* |
| **3. Validation** | `validate_sql` | Strips markdown, checks for forbidden keywords, and ensures `LIMIT 100`. |
| **4. Execution** | MCP `query` | Executes the validated SQL string returned by `validate_sql`. |
| **5. Synthesis** | LLM | Summarize the raw data into a human-readable response. |

---

## 4. Advanced Component Details

### SchemaRetriever
- **Mechanism**: Connects directly to the DB via `psycopg2`.
- **Discovery**: Queries `information_schema.tables` and `information_schema.columns` for the `public` schema.
- **Optimization**: Features a basic cache to avoid redundant schema lookups during a session.

### SQLValidator
- **Safety Rules**: Checks against a blacklist of DML/DDL keywords (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`).
- **Markdown Handling**: Automatically strips ` ```sql ` and ` ``` ` tags before processing.
- **Structure Check**: Ensures queries start with `SELECT` and contain no multiple statements (semicolon check).
- **Auto-Injection**: Automatically appends `LIMIT 100` if not explicitly provided by the LLM.

### Agent Configuration
- **Name**: `SQLAnalyticsAgent`
- **Context Handling**: Maintains thread history to support follow-up questions.
- **Tools**: `get_schema`, `validate_sql`, and the MCP-provided `query` tool.

---

## 5. System Instructions for AI Agents
If you are an AI assistant tasked with modifying or interacting with this repository, adhere to the following rules:

1.  **Strict Tool Sequence**: Never call the MCP `query` tool without first passing the SQL through the `validate_sql` tool. Use the exact output from `validate_sql` (if it doesn't return an error) for the `query` tool argument.
2.  **Schema First**: Prioritize the `get_schema` tool before generation. Never hallucinate column names.
3.  **No Markdown in Tools**: When calling `validate_sql` or `query`, pass the raw SQL string, not a markdown code block. (The system now handles stripping, but raw is preferred).
4.  **Error Explanation**: If `validate_sql` returns a string starting with "Error:", analyze the error message and explain it to the user.
5.  **Environment Variables**: Always load configuration (DB URLs, API Keys) via `.env`. No hardcoding of credentials.

---

## 6. How to Extend
- **Adding Domain Context**: You can wrap `get_schema` to provide hardcoded table descriptions if the database schema is cryptic.
- **Complex Validation**: For enterprise use, replace the regex-based `SQLValidator._extract_tables` with a dedicated SQL parser like `sqlglot`.
- **New Tools**: Add tools to `agent.py` for data visualization or exporting results to CSV.
