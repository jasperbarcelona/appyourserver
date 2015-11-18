#/usr/bin/python

import flask, flask.views
from flask import url_for, request, session, redirect, jsonify, Response, make_response, current_app
from flask import render_template, request
from flask import session, redirect
from jinja2 import environment, FileSystemLoader
from flask.ext import admin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import ModelView
from flask.ext.admin import Admin, BaseView, expose
from dateutil.parser import parse as parse_date
from functools import update_wrapper
from datetime import timedelta
from datetime import datetime
from functools import wraps
import threading
from werkzeug.datastructures import FileStorage
from werkzeug import secure_filename
import helpers.helper as helper
import validations.validators as validate
from flask_socketio import SocketIO, emit
from time import sleep
import requests
import datetime
import time
import json
import uuid
import os

app = flask.Flask(__name__)
app.secret_key = '234234rfascasascqweqscasefsdvqwefe2323234dvsv'
socketio = SocketIO(app)

class IngAdmin(sqla.ModelView):
    column_display_pk = True
admin = Admin(app)
admin.add_view(IngAdmin(helper.Client, helper.db.session))
admin.add_view(IngAdmin(helper.User, helper.db.session))
admin.add_view(IngAdmin(helper.Service, helper.db.session))
admin.add_view(IngAdmin(helper.Queued, helper.db.session))
admin.add_view(IngAdmin(helper.Svc, helper.db.session))
admin.add_view(IngAdmin(helper.Transaction, helper.db.session))

@app.route('/api/user/register/',methods=['GET','POST'])
@validate.fields
@validate.email
@validate.new_msisdn
def register():
    data = flask.request.form.to_dict()
    first_name = data['first_name']
    last_name = data['last_name']
    email = data['email']
    msisdn = data['msisdn']
    country = data['country']
    return helper.save_user(first_name,last_name,email,msisdn,country)

@app.route('/api/queue/fetch/',methods=['GET'])
@validate.user_api_key
def get_queue():
    api_key = flask.request.args.get('api_key')
    return helper.get_user_queues(api_key)


@app.route('/api/user/svc/generate/',methods=['POST'])
@validate.msisdn
def new_msisdn():
    msisdn = flask.request.form.get('msisdn')
    return helper.generate_svc(msisdn)


@app.route('/api/user/login/',methods=['POST'])
@validate.msisdn
@validate.svc
def user_login():
    data = flask.request.form.to_dict()
    msisdn = data['msisdn']
    svc = data['svc']
    return helper.login(msisdn,svc)


@app.route('/api/queue/new/',methods=['POST'])
@validate.client_api_key
@validate.service
@validate.msisdn
def add_queue():
    data = flask.request.form.to_dict()
    api_key = flask.request.args.get('api_key')
    service_id = data['service_id']
    msisdn = data['msisdn']

    return helper.add_queue(api_key,service_id,msisdn)


@app.route('/api/queue/next/',methods=['POST'])
@validate.client_api_key
@validate.service
def next_queue():
    data = flask.request.form.to_dict()
    api_key = flask.request.args.get('api_key')
    service_id = data['service_id']

    return helper.next_queue(api_key,service_id)


@app.route('/db/rebuild',methods=['GET','POST'])
def database_rebuild():
    return helper.rebuild_database()


@app.route('/favicon.ico',methods=['GET','POST'])
def favicon():
    return '',200


if __name__ == '__main__':
    app.debug = True
    app.run(port=int(os.environ['PORT']),host='0.0.0.0',threaded=True)