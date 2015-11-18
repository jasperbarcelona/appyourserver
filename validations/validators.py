from flask import Flask, jsonify, request
from functools import wraps
from flask.ext.sqlalchemy import SQLAlchemy
from validate_email import validate_email
from models import *
import helpers.db_conn as db
import json

def msisdn(f):
    @wraps(f)
    def dfn(*args, **kwargs):
        msisdn = flask.request.form.get('msisdn')

        if msisdn == None or msisdn == '':
            return jsonify(
                status='failed',
                error='Missing Argument: MSISDN'
                ), 404

        if User.query.filter_by(msisdn=msisdn).first() == None:
            return jsonify(
                status='failed',
                error='No user found for %s. Please register first.' %msisdn
                ), 401

        return f(*args, **kwargs)
    return dfn

def new_msisdn(f):
    @wraps(f)
    def dfn(*args, **kwargs):
        msisdn = flask.request.form.get('msisdn')

        if msisdn == None or msisdn == '':
            return jsonify(
                status='failed',
                error='Missing Argument: MSISDN'
                ),404

        if User.query.filter_by(msisdn=msisdn).first() != None:
            return jsonify(
                status='failed',
                error='The phone number %s, is already registered.' %msisdn
                ),409

        return f(*args, **kwargs)
    return dfn

def fields(f):
    @wraps(f)
    def dfn(*args, **kwargs):
        missing_fields = []
        data = flask.request.form.to_dict()

        for field in data:
            if data[field] == '':
                missing_fields.append(field)

        if len(missing_fields) != 0:
            return jsonify(
                status='failed',
                error='Missing field/s: ' + ", ".join(missing_fields)
                ),400

        return f(*args, **kwargs)
    return dfn

def email(f):
    @wraps(f)
    def dfn(*args, **kwargs):
        email_address = flask.request.form.get('email')
        if not validate_email(email_address):
            return jsonify(
                status='failed',
                error='Invalid email'
                ),400

        return f(*args, **kwargs)
    return dfn

def svc(f):
    @wraps(f)
    def dfn(*args, **kwargs):
        svc = flask.request.form.get('svc')

        if svc == None or svc == '':
            return jsonify(
                status='failed',
                error='Missing Argument: SVC'
                ), 404

        return f(*args, **kwargs)
    return dfn

def client_api_key(f):
    @wraps(f)
    def dfn(*args, **kwargs):
        api_key = request.args.get('api_key')

        if api_key == None or api_key == '':
            return jsonify(
                status='failed',
                error='Missing Argument: api_key'
                ), 404
        if Client.query.filter_by(api_key=api_key).first() == None:
            return jsonify(
                status='failed',
                error='Invalid API Key'
                ),401
        return f(*args, **kwargs)
    return dfn

def user_api_key(f):
    @wraps(f)
    def dfn(*args, **kwargs):
        api_key = request.args.get('api_key')

        if api_key == None or api_key == '':
            return jsonify(
                status='failed',
                error='Missing Argument: api_key'
                ), 404
        if User.query.filter_by(api_key=api_key).first() == None:
            return jsonify(
                status='failed',
                error='Invalid API Key'
                ),401
        return f(*args, **kwargs)
    return dfn

def service(f):
    @wraps(f)
    def dfn(*args, **kwargs):
        data = flask.request.form.to_dict()
        api_key = flask.request.args.get('api_key')
        service_id = data['service_id']

        client = Client.query.filter_by(api_key=api_key).first()

        if service_id == None or service_id == '':
            return jsonify(
                status='failed',
                error='Missing Argument: service_id'
                ), 404

        if Service.query.filter_by(client_id=client.id, id=service_id).first() == None:
            return jsonify(
                status='failed',
                error='The service you requested does not or no longer exist'
                ), 404

        return f(*args, **kwargs)
    return dfn

# def user_key(f):
#     @wraps(f)
#     def dfn(*args, **kwargs):
#         data = flask.request.form.to_dict()
#         user_key = data['user_key']

#         if user_key == None or user_key == '':
#             return jsonify(
#                 Error='Missing Argument: user_key'
#                 ), 500

#         user = User.query.filter_by(user_key=user_key).first()

#         if user == None or user == '':
#             return jsonify(
#                 Error='could not find a match for %s' %user_key
#                 ), 500

#         return f(*args, **kwargs)
#     return dfn