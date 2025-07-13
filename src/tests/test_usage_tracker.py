"""
Test usage tracker functionality.
"""
import os
import json
from unittest import TestCase, mock
import tempfile

from src.auth.usage_tracker import (
    UsageTracker, 
    UsageStats,
    UserUsageStats,
    OverallUsageStats,
    UsageEntry
)


class TestUsageTracker(TestCase):
    """Test the UsageTracker class"""
    
    def setUp(self):
        # Create a temporary file for testing
        self.test_file = tempfile.NamedTemporaryFile(delete=False)
        self.test_file.close()
        
        # Mock the config
        self.patcher = mock.patch('src.config.USAGE_DATA_PATH', self.test_file.name)
        self.patcher.start()
        
        # Create a new tracker that will use our test file
        self.tracker = UsageTracker()
    
    def tearDown(self):
        # Stop the mock and remove the test file
        self.patcher.stop()
        os.unlink(self.test_file.name)
    
    def test_initialize_usage_file(self):
        """Test that the usage file is initialized correctly"""
        # First, ensure the file doesn't exist to test initialization logic
        try:
            os.remove(self.test_file.name)
        except FileNotFoundError:
            pass
            
        # Create a new instance to trigger initialization
        self.tracker = UsageTracker()
        
        # The file should be created with the initial structure
        self.assertTrue(os.path.exists(self.test_file.name))
        with open(self.test_file.name, 'r') as f:
            file_content = f.read()
            self.assertTrue(file_content.strip())
            data = json.loads(file_content)
            # Validate using Pydantic
            usage_stats = UsageStats.model_validate(data)
        
        self.assertEqual(usage_stats.overall.total_input_tokens, 0)
        self.assertEqual(usage_stats.overall.total_output_tokens, 0)
        self.assertEqual(usage_stats.overall.total_text_length, 0)
        self.assertEqual(usage_stats.overall.invocations_count, 0)
        self.assertEqual(len(usage_stats.users), 0)
    
    def test_log_usage(self):
        """Test that usage is logged correctly"""
        # Log some usage
        self.tracker.log_usage(
            text_length=100,
            input_tokens=20,
            output_tokens=30,
            user_name='test_user'
        )
        
        # Check that the overall statistics were updated
        with open(self.test_file.name, 'r') as f:
            data = json.load(f)
            usage_stats = UsageStats.model_validate(data)
        
        self.assertEqual(usage_stats.overall.total_input_tokens, 20)
        self.assertEqual(usage_stats.overall.total_output_tokens, 30)
        self.assertEqual(usage_stats.overall.total_text_length, 100)
        self.assertEqual(usage_stats.overall.invocations_count, 1)
        
        # Check that the user statistics were updated
        self.assertIn('test_user', usage_stats.users)
        user_data = usage_stats.users['test_user']
        self.assertEqual(user_data.total_input_tokens, 20)
        self.assertEqual(user_data.total_output_tokens, 30)
        self.assertEqual(user_data.total_text_length, 100)
        self.assertEqual(user_data.invocations_count, 1)
        self.assertEqual(len(user_data.history), 1)
        
        # Check the history entry
        entry = user_data.history[0]
        self.assertEqual(entry.input_tokens, 20)
        self.assertEqual(entry.output_tokens, 30)
        self.assertEqual(entry.text_length, 100)
        self.assertTrue(entry.timestamp)  # Ensure timestamp exists
    
    def test_log_usage_no_user(self):
        """Test that usage is logged correctly when no user is specified"""
        # Log some usage without a user
        self.tracker.log_usage(
            text_length=100,
            input_tokens=20,
            output_tokens=30
        )
        
        # Check that only the overall statistics were updated
        with open(self.test_file.name, 'r') as f:
            data = json.load(f)
            usage_stats = UsageStats.model_validate(data)
        
        self.assertEqual(usage_stats.overall.total_input_tokens, 20)
        self.assertEqual(usage_stats.overall.total_output_tokens, 30)
        self.assertEqual(usage_stats.overall.total_text_length, 100)
        self.assertEqual(usage_stats.overall.invocations_count, 1)
        
        # There should be no users
        self.assertEqual(len(usage_stats.users), 0)
    
    def test_get_usage_stats(self):
        """Test retrieving usage statistics"""
        # Log usage for two different users
        self.tracker.log_usage(
            text_length=100,
            input_tokens=20,
            output_tokens=30,
            user_name='user1'
        )
        
        self.tracker.log_usage(
            text_length=200,
            input_tokens=40,
            output_tokens=60,
            user_name='user2'
        )
        
        # Get overall stats
        stats = self.tracker.get_usage_stats()
        
        self.assertEqual(stats['overall']['total_input_tokens'], 60)  # 20 + 40
        self.assertEqual(stats['overall']['total_output_tokens'], 90)  # 30 + 60
        
        # Get user-specific stats
        user1_stats = self.tracker.get_usage_stats(user_name='user1')
        
        self.assertEqual(user1_stats['total_input_tokens'], 20)
        self.assertEqual(user1_stats['total_output_tokens'], 30)
        
        # Test non-existent user
        non_existent_user_stats = self.tracker.get_usage_stats(user_name='non_existent')
        self.assertEqual(non_existent_user_stats['error'], "User not found")
