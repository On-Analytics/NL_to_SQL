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
        # 1. Clean and normalize
        sql_upper = sql.strip().upper()
        
        # 2. Check for multiple statements
        if ';' in sql.strip()[:-1]:
            raise ValueError("Multiple SQL statements are not allowed.")

        # 3. Read-only enforcement
        for word in self.FORBIDDEN_KEYWORDS:
            if re.search(rf'\b{word}\b', sql_upper):
                raise ValueError(f"Unauthorized keyword detected: {word}")

        # 4. Ensure it starts with SELECT
        if not sql_upper.startswith('SELECT'):
            raise ValueError("Only SELECT queries are allowed.")

        # 5. Table whitelisting (basic regex check)
        if self.allowed_tables:
            # This is a simple heuristic; a full parser would be better for complex queries
            found_tables = self._extract_tables(sql)
            for table in found_tables:
                if table.lower() not in [t.lower() for t in self.allowed_tables]:
                    raise ValueError(f"Unauthorized table access: {table}")

        # 6. Row limiting
        if 'LIMIT' not in sql_upper:
            sql = sql.strip()
            if sql.endswith(';'):
                sql = sql[:-1]
            sql += " LIMIT 100;"
        
        return sql

    def _extract_tables(self, sql: str) -> Set[str]:
        """
        Extracts table names from a simple SELECT query.
        Matches 'FROM table' or 'JOIN table'.
        """
        matches = re.findall(rf'\b(?:FROM|JOIN)\s+([a-zA-Z0-9_".]+)', sql, re.IGNORECASE)
        return {m.strip('"') for m in matches}
