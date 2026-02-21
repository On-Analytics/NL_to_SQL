import os
import asyncio
import json
from dotenv import load_dotenv
from sql_validator import SQLValidator

async def test_date_functions():
    load_dotenv()
    validator = SQLValidator()
    
    # Test: CURRENT_DATE (This was likely failing because it contains 'CREATE' if boundaries are loose)
    # Wait, CURRENT_DATE doesn't contain CREATE. 
    # But maybe the LLM used "created_at" in a way that boundary detection missed?
    # Actually, "created_at" contains "CREATE".
    
    test_sql_1 = "SELECT COUNT(*) FROM orders WHERE created_at >= CURRENT_DATE - INTERVAL '1 month'"
    try:
        validated_1 = validator.validate(test_sql_1)
        print(f"Test 1 (created_at): SUCCESS -> {validated_1}")
    except Exception as e:
        print(f"Test 1 (created_at): FAILED -> {e}")

    # Test: Another potential culprit
    test_sql_2 = "SELECT * FROM users WHERE created_at > NOW()"
    try:
        validated_2 = validator.validate(test_sql_2)
        print(f"Test 2 (NOW): SUCCESS -> {validated_2}")
    except Exception as e:
        print(f"Test 2 (NOW): FAILED -> {e}")

if __name__ == "__main__":
    asyncio.run(test_date_functions())
