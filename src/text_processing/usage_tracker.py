"""
Usage tracking module for LLM invocations.
Tracks metrics such as text length, input tokens, and output tokens.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any, List

from pydantic import BaseModel, Field

from src import config as cfg


class UsageEntry(BaseModel):
    """Individual usage entry for LLM invocation."""
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    input_tokens: int
    output_tokens: int
    text_length: int


class UserUsageStats(BaseModel):
    """Usage statistics for a specific user."""
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_text_length: int = 0
    invocations_count: int = 0
    history: List[UsageEntry] = []


class OverallUsageStats(BaseModel):
    """Overall usage statistics across all users."""
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_text_length: int = 0
    invocations_count: int = 0


class UsageStats(BaseModel):
    """Complete usage statistics."""
    overall: OverallUsageStats = Field(default_factory=OverallUsageStats)
    users: Dict[str, UserUsageStats] = {}


class UsageTracker:
    """Tracks usage metrics for LLM invocations."""

    def __init__(self):
        self.usage_data_path = cfg.USAGE_DATA_PATH
        self._ensure_usage_file_exists()

    def _ensure_usage_file_exists(self) -> None:
        """Ensure the usage data file exists with a proper structure."""
        directory = os.path.dirname(self.usage_data_path)
        Path(directory).mkdir(parents=True, exist_ok=True)
        
        if not os.path.exists(self.usage_data_path):
            # Create initial usage stats with default values
            initial_data = UsageStats()
            with open(self.usage_data_path, 'w') as f:
                json.dump(initial_data.model_dump(), f, indent=2)

    def _read_usage_data(self) -> UsageStats:
        """Read the current usage data from the file."""
        try:
            with open(self.usage_data_path, 'r') as f:
                data = json.load(f)
                return UsageStats.model_validate(data)
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is corrupted or doesn't exist, initialize it
            self._ensure_usage_file_exists()
            return UsageStats()

    def _write_usage_data(self, data: UsageStats) -> None:
        """Write usage data to the file."""
        with open(self.usage_data_path, 'w') as f:
            json.dump(data.model_dump(), f, indent=2)

    def log_usage(
        self,
        text_length: int,
        input_tokens: int,
        output_tokens: int,
        user_name: Optional[str] = None
    ) -> None:
        """
        Log usage statistics for an LLM invocation.
        
        Args:
            text_length: Length of the text sent to LLM
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            user_name: Optional username to track per-user statistics
        """
        usage_data = self._read_usage_data()
        
        # Update overall statistics
        usage_data.overall.total_input_tokens += input_tokens
        usage_data.overall.total_output_tokens += output_tokens
        usage_data.overall.total_text_length += text_length
        usage_data.overall.invocations_count += 1
        
        # Update per-user statistics if user_name is provided
        if user_name:
            # Create user stats if they don't exist
            if user_name not in usage_data.users:
                usage_data.users[user_name] = UserUsageStats()
            
            user_data = usage_data.users[user_name]
            user_data.total_input_tokens += input_tokens
            user_data.total_output_tokens += output_tokens
            user_data.total_text_length += text_length
            user_data.invocations_count += 1
            
            # Create and add new usage entry to user history
            new_entry = UsageEntry(
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                text_length=text_length
            )
            user_data.history.append(new_entry)
        
        self._write_usage_data(usage_data)

    def get_overall_usage_stats(self) -> OverallUsageStats:
        """
        Get overall usage statistics (excluding per-user data).

        Returns:
            OverallUsageStats instance.
        """
        usage_data = self._read_usage_data()
        return usage_data.overall
    
    def get_usage_stats(self, user_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage statistics.
        
        Args:
            user_name: If provided, returns stats for this user only
            
        Returns:
            Dictionary with usage statistics
        """
        usage_data = self._read_usage_data()
        
        if user_name:
            if user_name in usage_data.users:
                # Return user-specific stats as a dictionary
                return usage_data.users[user_name].model_dump()
            else:
                return {"error": "User not found"}
        
        # Return all usage stats as a dictionary
        return usage_data.model_dump()


# Create a singleton instance
usage_tracker = UsageTracker()
