import os
import json
import psycopg2
from typing import Dict, Any, List

class SchemaRetriever:
    """
    Retrieves and caches PostgreSQL schema metadata.
    """
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.schema_cache: Dict[str, Any] = {}

    def fetch_schema(self) -> Dict[str, Any]:
        """
        Fetches tables and columns from information_schema.
        """
        try:
            conn = psycopg2.connect(self.db_url)
            cur = conn.cursor()
            
            # Fetch tables
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = [r[0] for r in cur.fetchall()]
            
            schema = {}
            for table in tables:
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = %s AND table_schema = 'public'
                """, (table,))
                columns = {r[0]: r[1] for r in cur.fetchall()}
                schema[table] = {"columns": columns}
            
            self.schema_cache = schema
            cur.close()
            conn.close()
            return schema
        except Exception as e:
            print(f"Error fetching schema: {e}")
            return {}

    def get_relevant_schema_prompt(self, search_query: str = "") -> str:
        """
        Formats the schema of relevant tables for the LLM prompt based on a search query.
        If search_query is empty, all tables are returned.
        """
        if not self.schema_cache:
            self.fetch_schema()
            
        # Determine which tables to include
        tables_to_include = []
        if not search_query:
            tables_to_include = list(self.schema_cache.keys())
        else:
            query = search_query.lower()
            tables_to_include = [t for t in self.schema_cache.keys() if query in t.lower()]

        if not tables_to_include:
            return "No relevant tables found in the database."

        prompt_parts = ["Available tables and columns:"]
        for table in tables_to_include:
            prompt_parts.append(f"\nTable: {table}")
            cols = self.schema_cache[table]["columns"]
            for col, dtype in cols.items():
                prompt_parts.append(f"  - {col} ({dtype})")
        
        return "\n".join(prompt_parts)
