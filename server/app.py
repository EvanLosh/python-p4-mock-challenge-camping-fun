#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''

@app.route('/campers', methods = ['GET', 'POST'])
def campers():
    if request.method == 'GET':
        camper_dicts = [camper.to_dict(rules = ('-signups',)) for camper in Camper.query.all()]
        response = make_response(
            camper_dicts,
            200
        )
    elif request.method == 'POST':
        form_data = request.get_json()
        if (8 <= form_data['age'] <= 18) and len(form_data['name']) > 0:
            new_camper = Camper(
                name = form_data['name'],
                age = form_data['age']
            )        
            db.session.add(new_camper)
            db.session.commit()
            response = make_response(
                new_camper.to_dict(),
                201
            )
        else:
            response = make_response(
                {'errors': 'invalid form data'},
                400
            )
    return response

@app.route('/activities', methods = ['GET', 'POST'])
def activities():
    if request.method == 'GET':
        activities_dicts = [a.to_dict(rules = ('-signups',)) for a in Activity.query.all()]
        response = make_response(
            activities_dicts,
            200
        )
    elif request.method == 'POST':
        form_data = request.get_json()
        # if (8 <= form_data['age'] <= 18) and len(form_data['name']) > 0:
        if isinstance(form_data['difficulty'], int) and isinstance(form_data['name'], str):
            new_activity = Activity(
                name = form_data['name'],
                difficulty = form_data['difficulty']
            )        
            db.session.add(new_activity)
            db.session.commit()
            response = make_response(
                new_activity.to_dict(),
                201
            )
        else:
            response = make_response(
                {'errors': 'invalid form data'},
                400
            )
    return response

@app.route('/signups', methods = ['POST'])
def signups():
    # if request.method == 'GET':
    #     signups_dicts = [a.to_dict(rules = ('-signups',)) for a in Signup.query.all()]
    #     response = make_response(
    #         signups_dicts,
    #         200
    #     )
    elif request.method == 'POST':
        form_data = request.get_json()
        invalid = False
        # if (8 <= form_data['age'] <= 18) and len(form_data['name']) > 0:
        # if isinstance(form_data['difficulty'], int) and isinstance(form_data['name'], str):
        if not (0<= form_data['time'] <= 23):
            invalid = True
        if not invalid:
            new_signup = Signup(
                time = form_data['time'],
                camper_id = form_data['camper_id'],
                activity_id = form_data['activity_id']
            )        
            db.session.add(new_signup)
            db.session.commit()
            response = make_response(
                new_signup.to_dict(),
                201
            )
        else:
            response = make_response(
                {'errors': ['validation errors']},
                400
            )
    return response
    
@app.route('/campers/<int:id>', methods = ['GET', 'PATCH'])
def camper_by_id(id):
    if id in [camper.to_dict()['id'] for camper in Camper.query.all()]:
        camper = Camper.query.filter_by(id=id).first()
        if request.method == 'GET':
            response = make_response(
                camper.to_dict(),
                200
            )
        elif request.method == 'PATCH':
            invalid = False
            form_data = request.get_json()
            # if (form_data['name'] and len(form_data['name']) > 0) and (form_data['age'] and 8 <= form_data['age'] <= 18):
            for attr in form_data:
                if attr == 'name':
                    if len(form_data['name']) > 0:
                        setattr(camper, attr, form_data[attr])
                    else:
                        invalid = True
                if attr == 'age':
                    if 8 <= form_data['age'] <= 18:
                        setattr(camper, attr, form_data[attr])
                    else: 
                        invalid = True
            if not invalid:
                db.session.commit()
                response = make_response(
                    camper.to_dict(),
                    202
                )
            else:
                response = make_response(
                    {'errors': ['validation errors']},
                    400
                )
    else:
        response = make_response(
            {'error': 'Camper not found'},
            404
        )
    return response

@app.route('/activities/<int:id>', methods = ['GET', 'DELETE'])
def activity_by_id(id):
    if id in [a.to_dict()['id'] for a in Activity.query.all()]:
        activity = Activity.query.filter_by(id=id).first()
        if request.method == 'GET':
            response = make_response(
                activity.to_dict(),
                200
            )
        if request.method == 'DELETE':
            db.session.delete(activity)
            db.session.commit()
            response = make_response(
                {},
                204
            )
        # elif request.method == 'PATCH':
        #     invalid = False
        #     form_data = request.get_json()
        #     for attr in form_data:
        #         if attr == 'name':
        #             if isinstance(form_data['name'], str):
        #                 setattr(activity, attr, form_data[attr])
        #             else:
        #                 invalid = True
        #         if attr == 'difficulty':
        #             if isinstance(form_data['difficulty'], int):
        #                 setattr(activity, attr, form_data[attr])
        #             else: 
        #                 invalid = True
        #     if not invalid:
        #         db.session.commit()
        #         response = make_response(
        #             activity.to_dict(),
        #             202
        #         )
        #     else:
        #         response = make_response(
        #             {'errors': ['validation errors']},
        #             400
        #         )
    else:
        response = make_response(
            {'error': 'Activity not found'},
            404
        )
    return response

if __name__ == '__main__':
    app.run(port=5555, debug=True)
