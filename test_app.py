import unittest
import json
from app import app, users
import io
import pandas as pd

class TestUserAPI(unittest.TestCase):
    def setUp(self):
        """Set up test client and other test variables."""
        self.app = app
        self.client = self.app.test_client()
        # Clear users before each test
        users.clear()

    def test_create_user_success(self):
        """Test creating a new user successfully."""
        response = self.client.post('/users',
                                  data=json.dumps({'Name': 'John', 'Age': 30}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['Name'], 'John')
        self.assertEqual(data['Age'], 30)

    def test_create_user_empty_name(self):
        """Test creating a user with empty name."""
        response = self.client.post('/users',
                                  data=json.dumps({'Name': '', 'Age': 30}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Name cannot be empty', response.get_data(as_text=True))

    def test_create_user_invalid_age(self):
        """Test creating a user with invalid age."""
        response = self.client.post('/users',
                                  data=json.dumps({'Name': 'John', 'Age': 999}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Age must be between 1 and 120', response.get_data(as_text=True))

    def test_create_user_duplicate(self):
        """Test creating a duplicate user."""
        # Create first user
        self.client.post('/users',
                        data=json.dumps({'Name': 'John', 'Age': 30}),
                        content_type='application/json')
        # Try to create duplicate
        response = self.client.post('/users',
                                  data=json.dumps({'Name': 'John', 'Age': 40}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('User already exists', response.get_data(as_text=True))

    def test_get_users_empty(self):
        """Test getting users when none exist."""
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['data']), 0)
        self.assertEqual(data['count'], 0)

    def test_get_users(self):
        """Test getting users after adding some."""
        self.client.post('/users',
                        data=json.dumps({'Name': 'John', 'Age': 30}),
                        content_type='application/json')
        response = self.client.get('/users')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data['data']), 1)
        self.assertEqual(data['count'], 1)

    def test_delete_user_success(self):
        """Test deleting an existing user."""
        # Create a user first
        self.client.post('/users',
                        data=json.dumps({'Name': 'John', 'Age': 30}),
                        content_type='application/json')
        response = self.client.delete('/users/John')
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted successfully', response.get_data(as_text=True))

    def test_delete_user_not_found(self):
        """Test deleting a non-existent user."""
        response = self.client.delete('/users/NonExistentUser')
        self.assertEqual(response.status_code, 404)
        self.assertIn('User not found', response.get_data(as_text=True))

    def test_upload_users_success(self):
        """Test uploading users from CSV file."""
        # Create a test CSV file in memory
        csv_data = "Name,Age\nJohn,30\nJane,25"
        csv_file = io.BytesIO(csv_data.encode())
        
        response = self.client.post('/users/upload',
                                  data={'file': (csv_file, 'test.csv')},
                                  content_type='multipart/form-data')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(len(data['added_users']), 2)

    def test_upload_users_invalid_format(self):
        """Test uploading users with invalid CSV format."""
        # Create an invalid CSV file in memory
        csv_data = "InvalidColumn1,InvalidColumn2\nJohn,30"
        csv_file = io.BytesIO(csv_data.encode())
        
        response = self.client.post('/users/upload',
                                  data={'file': (csv_file, 'test.csv')},
                                  content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn('CSV must contain', response.get_data(as_text=True))

    def test_get_average_age_by_group(self):
        """Test getting average age by name group."""
        # Add test users
        test_users = [
            {'Name': 'Alice', 'Age': 20},
            {'Name': 'Amy', 'Age': 30},
            {'Name': 'Bob', 'Age': 25}
        ]
        for user in test_users:
            self.client.post('/users',
                           data=json.dumps(user),
                           content_type='application/json')

        response = self.client.get('/users/average-age')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['average_age']['A'], 25.0)  # (20 + 30) / 2
        self.assertEqual(data['average_age']['B'], 25.0)

    def test_get_average_age_empty(self):
        """Test getting average age when no users exist."""
        response = self.client.get('/users/average-age')
        self.assertEqual(response.status_code, 404)
        self.assertIn('No users found', response.get_data(as_text=True))

if __name__ == '__main__':
    unittest.main()