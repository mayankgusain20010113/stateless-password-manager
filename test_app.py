import unittest
import json
import sys
import os
import sqlite3

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app, DB_NAME

class TestPasswordManager(unittest.TestCase):
    def setUp(self):
        """Set up test client and clean database before each test."""
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.base_url = '/api'
        
        # Clean database before each test
        self._cleanup_db()

    def tearDown(self):
        """Clean up after each test."""
        self._cleanup_db()

    def _cleanup_db(self):
        """Delete all data from the database."""
        if os.path.exists(DB_NAME):
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vault_entries")
            cursor.execute("DELETE FROM users")
            conn.commit()
            conn.close()

    def test_register_user(self):
        """Test user registration."""
        response = self.client.post(f'{self.base_url}/register',
            json={'username': 'test_user', 'password': 'secure_pass'},
            content_type='application/json')
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'User registered successfully')

    def test_login_success(self):
        """Test successful login."""
        # Register first
        self.client.post(f'{self.base_url}/register',
            json={'username': 'login_test', 'password': 'pass123'})
        
        response = self.client.post(f'{self.base_url}/login',
            json={'username': 'login_test', 'password': 'pass123'})
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Login successful')

    def test_wrong_password(self):
        """Test login failure with wrong password."""
        response = self.client.post(f'{self.base_url}/login',
            json={'username': 'nonexistent', 'password': 'wrong'})
        self.assertEqual(response.status_code, 401)

    def test_save_and_get_password(self):
        """Test saving and retrieving a password."""
        # Login
        self.client.post(f'{self.base_url}/register',
            json={'username': 'vault_test', 'password': 'master123'})
        login_resp = self.client.post(f'{self.base_url}/login',
            json={'username': 'vault_test', 'password': 'master123'})
        
        # Save
        save_resp = self.client.post(f'{self.base_url}/save',
            json={
                'service': 'TestSite',
                'password': 'secret123',
                'master_password': 'master123'
            })
        self.assertEqual(save_resp.status_code, 200)

        # Get
        get_resp = self.client.get(f'{self.base_url}/get?master_password=master123')
        self.assertEqual(get_resp.status_code, 200)
        data = json.loads(get_resp.data)
        self.assertEqual(len(data['entries']), 1)
        self.assertEqual(data['entries'][0]['service'], 'TestSite')
        self.assertEqual(data['entries'][0]['password'], 'secret123')

if __name__ == '__main__':
    unittest.main()