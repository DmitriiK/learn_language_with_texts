"""
Usage tracking module for LLM invocations.
Tracks metrics such as text length, input tokens, and output tokens.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any

from src import config as cfg


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
            initial_data = {
                "overall": {
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "total_text_length": 0,
                    "invocations_count": 0
                },
                "users": {}
            }
            with open(self.usage_data_path, 'w') as f:
                json.dump(initial_data, f, indent=2)

    def _read_usage_data(self) -> Dict:
        """Read the current usage data from the file."""
        try:
            with open(self.usage_data_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is corrupted or doesn't exist, initialize it
            self._ensure_usage_file_exists()
            with open(self.usage_data_path, 'r') as f:
                return json.load(f)

    def _write_usage_data(self, data: Dict) -> None:
        """Write usage data to the file."""
        with open(self.usage_data_path, 'w') as f:
            json.dump(data, f, indent=2)

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
        usage_data["overall"]["total_input_tokens"] += input_tokens
        usage_data["overall"]["total_output_tokens"] += output_tokens
        usage_data["overall"]["total_text_length"] += text_length
        usage_data["overall"]["invocations_count"] += 1
        
        # Update per-user statistics if user_name is provided
        if user_name:
            if user_name not in usage_data["users"]:
                usage_data["users"][user_name] = {
                    "total_input_tokens": 0,
                    "total_output_tokens": 0,
                    "total_text_length": 0,
                    "invocations_count": 0,
                    "history": []
                }
            
            user_data = usage_data["users"][user_name]
            user_data["total_input_tokens"] += input_tokens
            user_data["total_output_tokens"] += output_tokens
            user_data["total_text_length"] += text_length
            user_data["invocations_count"] += 1
            
            # Add entry to user history
            user_data["history"].append({
                "timestamp": datetime.now().isoformat(),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "text_length": text_length
            })
        
        self._write_usage_data(usage_data)

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
            return usage_data["users"].get(user_name, {"error": "User not found"})
        
        return usage_data


usage_tracker = UsageTracker()
