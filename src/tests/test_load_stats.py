"""
Script to test loading existing usage stats with Pydantic models
"""
import json
from src.auth.usage_tracker import UsageStats

# Path to the usage stats file
USAGE_STATS_PATH = "data/audit/usage_stats.json"

# Load the usage stats file
with open(USAGE_STATS_PATH, 'r') as f:
    data = json.load(f)

# Try to parse it with our Pydantic model
try:
    usage_stats = UsageStats.model_validate(data)
    print("Successfully loaded usage stats with Pydantic!")
    print(f"Overall invocation count: {usage_stats.overall.invocations_count}")
    print(f"Total users: {len(usage_stats.users)}")
    for user_name, user_stats in usage_stats.users.items():
        print(f"User {user_name}: {user_stats.invocations_count} invocations")
except Exception as e:
    print(f"Error loading usage stats: {e}")
