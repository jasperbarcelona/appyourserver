from flask import Flask, jsonify, request
from functools import wraps
from flask.ext.sqlalchemy import SQLAlchemy
from models import *
import helpers.db_conn as db
import json

def content_type(f):
    @wraps(f)
    def dfn(*args, **kwargs):
        # Content-Type is invalid
        content_type = request.headers.get('Content-Type')

        if content_type != 'application/json':
            return jsonify({
                'Error':'Invalid content type'
                })
        return f(*args, **kwargs)
    return dfn

def api_key(f):
    @wraps(f)
    def dfn(*args, **kwargs):
        api_key = request.args.get('api_key')

        if api_key == None or api_key == '':
            return jsonify({
                'Error':'Missing Argument: api_key'
                }), 500
        print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
        print Client.query.filter_by(api_key=api_key).first()
        if Client.query.filter_by(api_key=api_key).first() == None and User.query.filter_by(api_key=api_key).first() == None:
            return jsonify({
                'Error':'Invalid API Key'
                })
        return f(*args, **kwargs)
    return dfn

def service(f):
    @wraps(f)
    def dfn(*args, **kwargs):
        data = request.json
        api_key = flask.request.args.get('api_key')
        service_id = data['service_id']

        client = Client.query.filter_by(api_key=api_key).first()

        if service_id == None or service_id == '':
            return jsonify({
                'Error':'Missing Argument: service_id'
                }), 500

        if Service.query.filter_by(client_id=client.id, id=service_id).first() == None:
            return jsonify({
                'Error':'The service you requested does not or no longer exist'
                }), 500

        return f(*args, **kwargs)
    return dfn

def user_key(f):
    @wraps(f)
    def dfn(*args, **kwargs):
        data = request.json
        user_key = data['user_key']

        if user_key == None or user_key == '':
            return jsonify({
                'Error':'Missing Argument: user_key'
                }), 500

        user = User.query.filter_by(user_key=user_key).first()

        if user == None or user == '':
            return jsonify({
                'Error':'could not find a match for %s' %user_key
                }), 500

        return f(*args, **kwargs)
    return dfn