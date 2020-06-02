import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from .app import *
from .models import *

# PRIVATE USER GENERATED FOR TESTING PURPOSES ONLY
# HAS ALL PERMISSIONS:
# "get:tutors", "get:subjects", "delete:tutor",
# "post:tutor", "post:subject", "patch:tutor", "delete:tutor"
ADMIN_TOKEN = os.environ.get('ADMIN_TOKEN')

class TextTutorTestCase(unittest.TestCase):
    """This class represents the text tutor test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "text_tutor_test"
        self.database_path = "postgres://{}/{}".format(
            'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.headers_admin = {
            'Content-Type': 'application/json',
            'Authorization': ADMIN_TOKEN}


        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            self.db.create_all()

    def tearDown(self):
        pass

    def test_paginate_tutors(self):
        """Tests tutor pagination success"""
        response = self.client().get('/tutors')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_request_beyond_valid_page(self):
        """ Tests error if user tries to access nonexistent page """
        response = self.client().get('/tutors?page=1000')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')

    def test_get_tutors(self):
        """ Tests success of loading tutors"""
        response = self.client().get('/api/tutors')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_get_subjects(self):
        """Tests success of loading tutors"""
        response = self.client().get('/api/subjects',
                headers=self.headers_admin)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_create_tutors(self):
        """Tests tutor creation"""
        test_tutor = {
            'id': 654321,
            'name': 'Test',
            'phone': '123456789',
            'email': 'test@email.com'
            # 'classes': 'classes' TODO
        }
        response = self.client().post('/api/tutors',
                data=json.dumps(test_tutor),
                headers=self.headers_admin)
        data = json.loads(response.data)

        # check status code, success message & compare length before & after
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['id'], 654321)

    def test_create_subjects(self):
        """Tests tutor creation"""
        test_subject = {
            'id': 765432,
            'name': 'English',
            'grade': '14',
        }

        response = self.client().post('/api/subjects',
                data=json.dumps(test_subject),
                headers=self.headers_admin)
        data = json.loads(response.data)

        # check status code, success message & compare length before & after
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['grade'], 14)

    def test_edit_tutor(self):
        """Tests PATCH tutor """
        patched_tutor = {
            'email': 'patch@email.com'
        }

        response = self.client().patch(
                '/api/tutors/654321',
                json=patched_tutor,
                headers=self.headers_admin)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['tutor']['email'], 'patch@email.com')

    def test_delete_tutor(self):
        """ Tests question delete success """
        delete_tutor = Tutor(
            name="Lizzo",
            phone='1231234123',
            email="lizzo@email.com",
            classes=" "
        )
        delete_tutor.insert()
        t_id = delete_tutor.id

        response = self.client().delete('/api/tutors/{}'.format(t_id),
                headers=self.headers_admin)
        data = json.loads(response.data)

        # check status code, success message & compare length before & after
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], t_id)

    def test_delete_subject(self):
        """Tests question delete success """
        delete_subject = Subject(
            name="Art",
            grade='8'
        )

        delete_subject.insert()
        s_id = subject.id


        response = self.client().delete('/api/subject/{}'.format(s_id),
                headers=self.headers_admin)
        data = json.loads(response.data)

        # check status code, success message & compare length before & after
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], s_id)

    def test_422_create_tutor(self):
        """test failure of question creation error 400"""
        tutors_before = Tutor.query.all()

        response = self.client().post('/api/tutors', json={},
                headers=self.headers_admin)
        data = json.loads(response.data)
        tutors_after = Tutor.query.all()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(len(tutors_before) == len(tutors_after))

    def test_422_create_subject(self):
        """test failure of question creation error 400"""
        subjects_before = Subject.query.all()

        response = self.client().post('/api/subjects', json={},
                headers=self.headers_admin)
        data = json.loads(response.data)
        subjects_after = Subject.query.all()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertTrue(len(subjects_before) == len(subjects_after))

    def test_422_edit_tutor(self):
        """test failure of patch tutor error 422"""
        patched_tutor = {
            'email': 12345
        }

        response = self.client().patch(
                '/api/tutors/654321',
                json=patched_tutor,
                headers=self.headers_admin)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertFalse(data['success'])

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
