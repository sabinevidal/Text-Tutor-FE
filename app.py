import os
import json
from flask import (Flask, request,
                   redirect, abort, jsonify,
                   render_template, flash, session,
                   url_for, make_response)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.dialects.postgresql import JSON

from models import *
from auth.auth import AuthError, requires_auth
# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#
TUTORS_PER_PAGE = 10


def paginate_tutors(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * TUTORS_PER_PAGE
    end = start + TUTORS_PER_PAGE

    tutors = [tutor.format() for tutor in tutors]
    current_tutors = tutors[start:end]

    return current_tutors


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    CORS(app, resources={'/': {'origins': '*'}}, supports_credentials=True)

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    '''
    @TODO uncomment the following line to initialize the datbase
    !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
    !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
    '''
    # db_drop_and_create_all()

# ----------------------------------
# ROUTES
# ----------------------------------
    @app.route('/')
    def index():
        return jsonify({
            'success' : True
        })

# ----------- TUTORS ----------

    @app.route('/api/tutors')
    def get_tutors():
        '''
        Handles GET requests for tutors.
        '''
        tutors = Tutor.query.all()

        if len(tutors) == 0:
            abort(404)

        tutor_list = list(map(Tutor.format, tutors))

        response = {
            'success': True,
            'tutors': tutor_list
        }
        return jsonify(response)

    @app.route('/api/tutors/<int:id>')
    @requires_auth('get:tutor')
    def show_tutor(jwt, id):
        '''
        Handles GET requests for tutor by id.
        '''
        tutor = Tutor.query.filter_by(id=id).one_or_none()

        if tutor is None:
            abort(404)

        return jsonify({
            'success': True,
            'tutor': tutor.format()
        })

    # CREATE
    @app.route('/api/tutors', methods=['POST'])
    @requires_auth('post:tutor')
    def add_tutor(jwt):
        '''
        Handles POST requests for creating a tutor.
        '''
        body = request.get_json()

        name = body.get('name')
        phone = body.get('phone')
        email = body.get('email')
        classes = body.get('classes')

        try:
            tutor = Tutor(
                name=name, phone=phone,
                email=email
            )

            for subject in classes:
                tutor_subjects = add_class(subject)
                tutor.classes.append(tutor_subjects)
            tutor.insert()

        except Exception as e:
            print('ERROR: ', str(e))
            abort(422)

        response = {
            'success': True,
            'tutor': tutor.format()
        }

        return jsonify(response)

    def add_class(subject):
        new_class = Subject(name=subject['name'], grade=subject['grade'])
        return new_class

    @app.route('/api/tutors/<int:id>', methods=['PATCH'])
    @requires_auth('patch:tutor')
    def edit_tutor(*args, **kwargs):
        id = kwargs['id']

        tutor = Tutor.query.filter_by(id=id).one_or_none()

        if tutor is None:
            abort(404)

        body = request.get_json()

        name = body.get('name')
        phone = body.get('phone')
        email = body.get('email')
        classes = body.get('classes')

        if 'name' in body:
            tutor.name = body['name']
        if 'phone' in body:
            tutor.phone = body['phone']
        if 'email' in body:
            tutor.email = body['email']
        if 'classes' in body:
            for subject in classes:
                tutor_subjects = add_class(subject)
                print("tutorsubs: ", tutor_subjects)
                tutor.classes.append(tutor_subjects)

        try:
            tutor.update()
        except Exception as e:
            print('EXCEPTION: ', str(e))
            abort(422)

        response = {
            'success': True,
            'tutors': tutor.format()
        }

        return jsonify(response)

    # DELETE
    @app.route('/api/tutors/<int:id>', methods=['DELETE'])
    @requires_auth('delete:tutor')
    def delete_tutor(*args, **kwargs):
        '''
        Handles API DELETE requests for tutors.
        '''
        id = kwargs['id']

        tutor = Tutor.query.filter_by(id=id).one_or_none()

        if tutor is None:
            abort(404)

        try:
            tutor.delete()
        except Exception as e:
            print('EXCEPTION: ', str(e))
            abort(422)

        return jsonify({
            'success': True,
            'tutor': tutor.name,
            'deleted_id': id
        })

    # ----------- SUBJECTS ----------
    # CREATE

    @app.route('/api/subjects', methods=['POST'])
    @requires_auth('post:subject')
    def add_subject(jwt):
        body = request.get_json()
        print('body: ', body)

        name = body.get('name')
        grade = body.get('grade')

        try:
            subject = Subject(
                name=name, grade=grade
            )
            subject.insert()

        except Exception as e:
            print('ERROR: ', str(e))
            abort(422)

        response = {
            'success': True,
            'subject': subject.format()
        }

        return jsonify(response)

    # GET
    @app.route('/api/subjects')
    def get_subjects():
        subjects = Subject.query.order_by(Subject.grade).all()

        if len(subjects) == 0:
            abort(404)

        subjects = format_subjects(subjects)

        response = {
            'success': True,
            'subjects': subjects
        }
        return jsonify(response)

    @app.route('/api/subjects/<int:id>')
    @requires_auth('get:subject')
    def show_subject(jwt, id):
        '''
        Handles GET requests for getting subjects by id
        '''
        subject = Subject.query.filter_by(id=id).one_or_none()

        if subject is None:
            abort(404)

        response = {
            'success': True,
            'subject': subject.format()
        }
        return jsonify(response)

    # DELETE
    @app.route('/api/subjects/<int:id>', methods=['DELETE'])
    @requires_auth('delete:subject')
    def delete_subject(*args, **kwargs):
        '''
        Handles API DELETE requests for subjects.
        '''
        id = kwargs['id']

        subject = Subject.query.filter_by(id=id).one_or_none()

        if subject is None:
            abort(404)

        try:
            subject.delete()
        except Exception as e:
            print('EXCEPTION: ', str(e))
            abort(422)

        return jsonify({
            'success': True,
            'subject': subject.name,
            'deleted_id': id
        })

# -----------------------------------------------------------
# Error Handlers
# -----------------------------------------------------------

    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "internal server error"
        }), 422

    @app.errorhandler(AuthError)
    def handle_auth_error(ex):
        '''
        Error handling for AuthError
        '''
        message = ex.error['description']
        response = jsonify(ex.error)
        response.status_code = ex.status_code
        print('AUTH ERROR: ', response.get_data(as_text=True))
        flash(f'{message} Please login.')
        return redirect('/')

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
