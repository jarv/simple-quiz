import os
import unittest
import tempfile
import simplejson
os.environ['FLASK_SETTINGS'] = 'cfg/test.py'
import simple_quiz
from simple_quiz.models import user_datastore, Deck
from flask import url_for
from mongoengine.queryset import DoesNotExist

TEST_DATA = {
    'title': 'test deck',
    'public': False,
    'cards': [
        {
            'question_text': 'This is a question',
            'answer_text': 'This is an answer',
            'question_img': 'none',
            'answer_img': 'none',
        }
    ]
}

def run_tests():
    unittest.main()

class StateTestCase(unittest.TestCase):

    def setUp(self):
        self.app = simple_quiz.app.test_client()
        # create test user and login
        user_datastore.create_user(email='test@example.com', password='test')
        self.test_user = user_datastore.find_user(email='test@example.com')
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.test_user.id
            sess['_fresh'] = True

    def tearDown(self):
        user_datastore.find_user(email='test@example.com').delete()
        # delete the testdeck if it exists
        try:
            d = Deck.objects.get(slug='testdeck')
            d.delete()
        except DoesNotExist:
            pass


    def test_login(self):
        """
        Tests a simple hello world view that requires login
        """

        r = self.app.get('/login_test')
        assert r.data == 'hello world'

    def test_deck_post(self):
        """
        Creates a new deck with dummy data,
        reads the deck back
        """

        data = simplejson.dumps(TEST_DATA)
        # create a new deck
        r = self.app.post('/update-deck/testdeck', data={'json_data': str(data)})
        resp = simplejson.loads(r.data)
        assert resp['status'] == 'created'
        # create a deck that already exists
        r = self.app.post('/update-deck/testdeck', data={'json_data': str(data)})
        resp = simplejson.loads(r.data)
        assert resp['status'] == 'updated'

    def test_deck_get(self):
        self.test_deck_post()

        # get a deck that doesn't exist
        r = self.app.get('/deck/error')
        resp = simplejson.loads(r.data)
        assert resp['status'] == 'error' and resp['msg'] == 'Deck does not exist'

        # get the deck
        r = self.app.get('/deck/testdeck')
        resp = simplejson.loads(r.data)
        assert resp['status'] == 'success'


if __name__ == '__main__':
    unittest.main()
