import unittest
from app import create_app, db
from app.models import User, BlogPost
from flask_jwt_extended import create_access_token
from config import TestConfig

class APITestCase(unittest.TestCase):
    # Set up the application with the test configuration
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()

        # Create a test user and log them in
        self.user = User(username='testuser@example.com')
        self.user.set_password('testpass')
        db.session.add(self.user)
        db.session.commit()

        # Generate an access token for the test user
        self.access_token = create_access_token(identity=self.user.id)
        print(f"Access Token for testuser: {self.access_token}")

        # Create a second test user
        self.other_user = User(username='otheruser@example.com')
        self.other_user.set_password('otherpass')
        db.session.add(self.other_user)
        db.session.commit()

        # Generate an access token for the second test user
        self.other_access_token = create_access_token(identity=self.other_user.id)
        print(f"Access Token for otheruser: {self.other_access_token}")

    def tearDown(self):
        # Clean up the database and the application context after each test
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_signup(self):
        print("Starting signup test")
        response = self.client.post('/signup', json={'email': 'newuser@example.com', 'password': 'newpass123'})
        print(f"Signup Response: {response.data}")
        self.assertEqual(response.status_code, 201)

    def test_login(self):
        print("Starting login test")
        response = self.client.post('/login', json={'email': 'testuser@example.com', 'password': 'testpass'})
        print(f"Login Response: {response.data}")
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.get_json())

    def test_create_post(self):
        print("Starting create post test")
        response = self.client.post('/posts', json={'title': 'Test Title', 'body': 'Test Body'}, headers={'Authorization': f'Bearer {self.access_token}'})
        print(f"Create post response: {response.data}")
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.get_json())

    def test_get_posts(self):
        print("Starting get posts test")
        post_response = self.client.post('/posts', json={'title': 'Test Title', 'body': 'Test Body'}, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(post_response.status_code, 201)
        response = self.client.get('/posts', headers={'Authorization': f'Bearer {self.access_token}'})
        print(f"Get posts response: {response.data}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['posts']), 1)
        self.assertEqual(data['posts'][0]['title'], 'Test Title')

    def test_get_post_by_id(self):
        print("Starting get post by id test")
        post_response = self.client.post('/posts', json={'title': 'Test Title', 'body': 'Test Body'}, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(post_response.status_code, 201)
        post_id = post_response.get_json()['id']
        response = self.client.get(f'/posts/{post_id}', headers={'Authorization': f'Bearer {self.access_token}'})
        print(f"Get post by id response: {response.data}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['title'], 'Test Title')
        self.assertEqual(data['body'], 'Test Body')

    def test_update_post(self):
        print("Starting update post test")
        post_response = self.client.post('/posts', json={'title': 'Test Title', 'body': 'Test Body'}, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(post_response.status_code, 201)
        post_id = post_response.get_json()['id']
        response = self.client.put(f'/posts/{post_id}', json={'title': 'Updated Title', 'body': 'Updated Body'}, headers={'Authorization': f'Bearer {self.access_token}'})
        print(f"Update post response: {response.data}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Post updated successfully')

    def test_delete_post(self):
        print("Starting delete post test")
        post_response = self.client.post('/posts', json={'title': 'Test Title', 'body': 'Test Body'}, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(post_response.status_code, 201)
        post_id = post_response.get_json()['id']
        response = self.client.delete(f'/posts/{post_id}', headers={'Authorization': f'Bearer {self.access_token}'})
        print(f"Delete post response: {response.data}")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], 'Post deleted successfully')

    def test_user_cannot_access_others_post(self):
        print("Starting user cannot access others post test")
        post_response = self.client.post('/posts', json={'title': 'Test Title', 'body': 'Test Body'}, headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(post_response.status_code, 201)
        post_id = post_response.get_json()['id']

        # Other user tries to access the post
        response = self.client.get(f'/posts/{post_id}', headers={'Authorization': f'Bearer {self.other_access_token}'})
        print(f"Other user get post response: {response.data}")
        self.assertEqual(response.status_code, 403)

        # Other user tries to update the post
        response = self.client.put(f'/posts/{post_id}', json={'title': 'Updated Title', 'body': 'Updated Body'}, headers={'Authorization': f'Bearer {self.other_access_token}'})
        print(f"Other user update post response: {response.data}")
        self.assertEqual(response.status_code, 403)

        # Other user tries to delete the post
        response = self.client.delete(f'/posts/{post_id}', headers={'Authorization': f'Bearer {self.other_access_token}'})
        print(f"Other user delete post response: {response.data}")
        self.assertEqual(response.status_code, 403)

    def test_rate_limiting(self):
        print("Starting rate limiting test")
        for i in range(12):  # Try a couple more to ensure we hit the limit
            response = self.client.post('/signup', json={'email': f'newuser{i}@example.com', 'password': 'newpass123'})
            print(f"Rate limit test response {i}: {response.data}")
            if response.status_code == 429:  # Rate limit hit
                break
            self.assertIn(response.status_code, [201, 429])  # Either created or rate limited
        self.assertEqual(response.status_code, 429)  # Ensure the last request was rate limited

if __name__ == '__main__':
    unittest.main()