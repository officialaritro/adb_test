import logging, os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)

mongo_uri = 'mongodb://' + os.environ["MONGO_HOST"] + ':' + os.environ["MONGO_PORT"]
db = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)['test_db']

MAX_DESCRIPTION_LENGTH = 255


class TodoRepository:

    def __init__(self, collection):
        self.collection = collection

    def list(self):
        return [self._serialize(doc) for doc in self.collection.find().sort('_id')]

    def create(self, description):
        doc = {'description': description}
        doc['_id'] = self.collection.insert_one(doc).inserted_id
        return self._serialize(doc)

    @staticmethod
    def _serialize(doc):
        return {'id': str(doc['_id']), 'description': doc['description']}


class TodoListView(APIView):
    repository = TodoRepository(db['todos'])

    def get(self, request):
        return Response(self.repository.list(), status=status.HTTP_200_OK)

    def post(self, request):
        description = request.data.get('description') if isinstance(request.data, dict) else None
        if not isinstance(description, str) or not description.strip():
            return self._error('description is required', status.HTTP_400_BAD_REQUEST)
        description = description.strip()
        if len(description) > MAX_DESCRIPTION_LENGTH:
            return self._error(f'description must be at most {MAX_DESCRIPTION_LENGTH} characters', status.HTTP_400_BAD_REQUEST)
        return Response(self.repository.create(description), status=status.HTTP_201_CREATED)

    def handle_exception(self, exc):
        if isinstance(exc, PyMongoError):
            logger.exception('Database error')
            return self._error('Database is unavailable, please try again later', status.HTTP_503_SERVICE_UNAVAILABLE)
        return super().handle_exception(exc)

    @staticmethod
    def _error(message, status_code):
        return Response({'error': message}, status=status_code)
