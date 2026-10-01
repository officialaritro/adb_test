from django.test import SimpleTestCase
from pymongo.errors import ServerSelectionTimeoutError
from unittest.mock import patch
from .views import TodoListView, TodoRepository, db


@patch.object(TodoListView, 'repository', TodoRepository(db['todos_test']))
class TodoListViewTests(SimpleTestCase):

    def tearDown(self):
        db['todos_test'].drop()

    def test_created_todos_are_listed_in_order(self):
        for description in ['Learn Docker', '  Learn React  ']:
            self.assertEqual(self.client.post('/todos', {'description': description}, content_type='application/json').status_code, 201)
        response = self.client.get('/todos/')
        self.assertEqual([todo['description'] for todo in response.json()], ['Learn Docker', 'Learn React'])

    def test_rejects_invalid_description(self):
        for payload in [{}, {'description': '   '}, {'description': 123}, {'description': 'x' * 256}, ['a']]:
            response = self.client.post('/todos', payload, content_type='application/json')
            self.assertEqual(response.status_code, 400, payload)
        self.assertEqual(self.client.get('/todos').json(), [])

    def test_database_failure_returns_503(self):
        with patch.object(TodoRepository, 'list', side_effect=ServerSelectionTimeoutError('down')):
            response = self.client.get('/todos')
        self.assertEqual(response.status_code, 503)
        self.assertIn('error', response.json())
