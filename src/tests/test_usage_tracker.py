"""
Test usage tracker functionality.
"""
import os
import json
from unittest import TestCase, mock
import tempfile

from src.text_processing.usage_tracker import UsageTracker


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
        # The file should be created with the initial structure
        with open(self.test_file.name, 'r') as f:
            data = json.load(f)
        
        self.assertIn('overall', data)
        self.assertIn('users', data)
        self.assertEqual(data['overall']['total_input_tokens'], 0)
        self.assertEqual(data['overall']['total_output_tokens'], 0)
        self.assertEqual(data['overall']['total_text_length'], 0)
        self.assertEqual(data['overall']['invocations_count'], 0)
    
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
        
        self.assertEqual(data['overall']['total_input_tokens'], 20)
        self.assertEqual(data['overall']['total_output_tokens'], 30)
        self.assertEqual(data['overall']['total_text_length'], 100)
        self.assertEqual(data['overall']['invocations_count'], 1)
        
        # Check that the user statistics were updated
        self.assertIn('test_user', data['users'])
        self.assertEqual(data['users']['test_user']['total_input_tokens'], 20)
        self.assertEqual(data['users']['test_user']['total_output_tokens'], 30)
        self.assertEqual(data['users']['test_user']['total_text_length'], 100)
        self.assertEqual(data['users']['test_user']['invocations_count'], 1)
        self.assertEqual(len(data['users']['test_user']['history']), 1)
    
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
        
        self.assertEqual(data['overall']['total_input_tokens'], 20)
        self.assertEqual(data['overall']['total_output_tokens'], 30)
        self.assertEqual(data['overall']['total_text_length'], 100)
        self.assertEqual(data['overall']['invocations_count'], 1)
        
        # There should be no users
        self.assertEqual(len(data['users']), 0)
    
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
