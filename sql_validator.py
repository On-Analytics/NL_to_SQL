import os
import re
from typing import List, Set

class SQLValidator:
    """
    Validates SQL queries for safety and schema compliance.
    """
    
    FORBIDDEN_KEYWORDS = {
        'INSERT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 
        'TRUNCATE', 'CREATE', 'GRANT', 'REVOKE'
    }

    def __init__(self, allowed_tables: Set[str] = None):
        self.allowed_tables = allowed_tables or set()

    def validate(self, sql: str) -> str:
        """
        Validates the SQL query. Returns the (possibly modified) SQL if safe,
        raises ValueError otherwise.
        """
        # 1. Clean and normalize (Strip markdown and extra whitespace)
        # Remove markdown code blocks if present
        sql = re.sub(r'```sql\s*', '', sql, flags=re.IGNORECASE)
        sql = re.sub(r'```\s*', '', sql)
        sql = sql.strip()
        
        sql_upper = sql.upper()
        
        # 2. Check for multiple statements
        # Only allow a semicolon at the very end
        if ';' in sql[:-1]:
            # Check if it's really a separate statement or just a semicolon in a string
            # For simplicity, we stick to the basic check but allow trailing semicolon
            if sql.count(';') > 1 or (sql.count(';') == 1 and not sql.endswith(';')):
                raise ValueError("Multiple SQL statements are not allowed.")

        # 3. Read-only enforcement
        for word in self.FORBIDDEN_KEYWORDS:
            # Avoid matching words that are sub-parts of common SQL functions
            # e.g., CURRENT_DATE should not match CREATE
            if re.search(rf'(?<![A-Z_])\b{word}\b(?![A-Z_])', sql_upper):
                raise ValueError(f"Unauthorized keyword detected: {word}")

        # 4. Ensure it starts with SELECT
        if not sql_upper.startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed (no markdown or extra text).")

        # 5. Table whitelisting (basic regex check)
        if self.allowed_tables:
            found_tables = self._extract_tables(sql)
            for table in found_tables:
                if table.lower() not in [t.lower() for t in self.allowed_tables]:
                    raise ValueError(f"Unauthorized table access: {table}")

        # 6. Row limiting
        if 'LIMIT' not in sql_upper:
            if sql.endswith(';'):
                sql = sql[:-1].strip()
            sql += " LIMIT 100;"
        elif not sql.endswith(';'):
            sql += ";"
        
        return sql

    def _extract_tables(self, sql: str) -> Set[str]:
        """
        Extracts table names from a simple SELECT query.
        Matches 'FROM table' or 'JOIN table'.
        """
        matches = re.findall(rf'\b(?:FROM|JOIN)\s+([a-zA-Z0-9_".]+)', sql, re.IGNORECASE)
        return {m.strip('"') for m in matches}
