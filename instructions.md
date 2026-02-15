# LLM-Based Conversational Agent with Secure SQL Routing (PostgreSQL MCP)

## Overview

This project implements a conversational AI system that:

* Accepts natural language input from users.
* Uses structured tool-calling to determine routing.
* Dynamically retrieves PostgreSQL schema metadata.
* Generates schema-compliant SQL.
* Validates SQL for safety.
* Executes queries via a PostgreSQL MCP server.
* Returns formatted, conversational responses.
* Maintains multi-turn conversational state.

The system must behave like a standard chat assistant while securely integrating structured database access.

---

# Core Architecture

## 1️⃣ Chat Interface

* Multi-turn conversation support.
* Persistent conversational memory per session.
* Context-aware follow-ups (e.g., “Now group that by month.”).
* Tracks:

  * `last_sql_query`
  * `last_filters`
  * `last_result_summary`

---

# 2️⃣ Structured Tool-Calling (Routing Layer)

The LLM must return structured output instead of free-form classification.

### Example Output

### If database query:

```json
{
  "action": "query_database",
  "intent_description": "User wants total revenue by month for Colombia"
}
```

### If general question:

```json
{
  "action": "respond_normally",
  "response": "..."
}
```

The system routes based on `action`.

No heuristic-based routing outside structured output.

---

# 3️⃣ Dynamic Schema Retrieval (Option 2 Implementation)

## Objective

The LLM must generate SQL using real, validated schema metadata retrieved dynamically from PostgreSQL.

The agent does NOT memorize the schema.
Schema awareness is enforced at runtime.

---

## 3.1 Schema Loading on System Initialization

On application startup, retrieve schema metadata from PostgreSQL:

### Retrieve tables

```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public';
```

### Retrieve columns per table

```sql
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'public';
```

Store schema in backend memory:

```python
schema = {
  "transactions": {
    "columns": {
      "id": "uuid",
      "user_id": "uuid",
      "amount": "numeric",
      "created_at": "timestamp"
    }
  },
  "users": {
    "columns": {
      "id": "uuid",
      "country": "text",
      "created_at": "timestamp"
    }
  }
}
```

---

## 3.2 Relevant Table Selection

Before SQL generation:

1. Analyze user intent.
2. Select relevant tables based on:

   * Keyword matching
   * Simple heuristic mapping
   * (Optional) Embedding similarity
3. Inject only relevant table definitions into the SQL generation prompt.

### Example Prompt Injection

```
Available tables:

transactions
- id (uuid)
- user_id (uuid)
- amount (numeric)
- created_at (timestamp)

users
- id (uuid)
- country (text)
- created_at (timestamp)
```

Do NOT inject entire schema if unnecessary.

---

## 3.3 Schema Enforcement Rule

All generated SQL must:

* Use only tables from the retrieved schema.
* Use only valid column names.
* Respect correct data types.

The LLM is not trusted to infer schema independently.

---

# 4️⃣ SQL Generation Layer

If `action = query_database`:

1. Use the injected schema context.
2. Generate read-only SQL.
3. Produce syntactically valid PostgreSQL SQL.

The SQL should:

* Use explicit column names.
* Avoid `SELECT *` (optional but recommended).
* Include aggregation/grouping if required.
* Respect previous conversational state (if applicable).

---

# 5️⃣ SQL Safety Validator (Mandatory Layer)

All generated SQL must pass validation before execution.

---

## 5.1 Read-Only Enforcement

Reject any SQL containing:

* `INSERT`
* `UPDATE`
* `DELETE`
* `DROP`
* `ALTER`
* `TRUNCATE`
* `CREATE`

Only allow `SELECT`.

---

## 5.2 Table Whitelisting

Parse SQL and extract table names.

Ensure:

* All referenced tables exist in the loaded schema.
* No system tables are accessed.
* No cross-schema access unless explicitly allowed.

---

## 5.3 Column Validation

Parse SQL to extract column references.

Ensure:

* All referenced columns exist in corresponding tables.
* No hallucinated fields are used.

---

## 5.4 Row Limiting

If SQL does not include `LIMIT`, automatically append:

```sql
LIMIT 100
```

Prevent unbounded full-table scans.

---

## 5.5 Dangerous Pattern Detection

Reject queries containing:

* Nested unauthorized subqueries
* Access to restricted schemas
* Multiple statements separated by `;`
* Comment-based injection attempts

---

## 5.6 Query Logging

Log:

* User message
* Generated SQL
* Validation result
* Execution time
* Row count

---

# 6️⃣ PostgreSQL MCP Execution Layer

If SQL passes validation:

1. Execute query via MCP.
2. Retrieve structured result set.
3. Return result to summarization layer.

Execution must use read-only database credentials.

---

# 7️⃣ Result Formatting & Summarization

Do NOT return raw SQL rows unless explicitly requested.

The system must:

* Format results clearly.
* Provide summary insights.
* Highlight:

  * Totals
  * Averages
  * Trends
  * Anomalies (if applicable)

Example:

> Revenue increased 12% month-over-month. Colombia represents 32% of total revenue during the selected period.

---

# 8️⃣ Standard LLM Response Path

If `action = respond_normally`:

* Respond directly using Claude Code SDK.
* No schema injection.
* No SQL generation.
* No MCP execution.

---

# 9️⃣ Multi-Turn State Handling

The system must maintain session-level state:

```python
conversation_state = {
  "last_sql_query": "...",
  "last_filters": {...},
  "last_result_summary": "...",
}
```

For follow-ups:

User:

> Show revenue by month.

User:

> Now only for Colombia.

The system must:

* Modify previous query context.
* Apply additional filter.
* Regenerate SQL using prior state.

LangGraph is recommended for orchestrating this stateful flow.

---

# 10️⃣ Full Execution Flow

```
User Input
      ↓
Structured Tool-Calling (LLM)
      ↓
If respond_normally → Direct LLM Response
      ↓
If query_database:
      ↓
Dynamic Schema Selection
      ↓
SQL Generation
      ↓
SQL Safety Validator
      ↓
PostgreSQL MCP Execution
      ↓
Result Summarization
      ↓
Final Conversational Response
```

---

# Security Principles

* The LLM never has direct database access.
* SQL is always validated before execution.
* Schema is controlled by backend logic.
* Read-only database credentials are mandatory.
* All queries are logged.

---

# Expected System Behavior

The final system must:

* Feel like a natural conversational assistant.
* Automatically detect when data retrieval is required.
* Generate schema-compliant SQL.
* Enforce strict SQL safety validation.
* Support multi-turn analytical conversations.
* Provide human-readable insights from structured data.

host:localhost
username:postgres
password:daviddeveloper
port:5432
database:postgres

operating system username: postgres
operating system password: [PASSWORD]
operating system port: 5432
operating system database: postgres

pgbouncer: 6432