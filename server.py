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
from time import sleep
import requests
import datetime
import time
import json
import uuid
import os

app = flask.Flask(__name__)
app.secret_key = '234234rfascasascqweqscasefsdvqwefe2323234dvsv'

class IngAdmin(sqla.ModelView):
    column_display_pk = True
admin = Admin(app)
admin.add_view(IngAdmin(helper.Client, helper.db.session))
admin.add_view(IngAdmin(helper.User, helper.db.session))
admin.add_view(IngAdmin(helper.Service, helper.db.session))
admin.add_view(IngAdmin(helper.Queued, helper.db.session))

@app.route('/api/queue/fetch/',methods=['GET'])
@validate.api_key
def get_queue():
    is_client = request.args.get('is_client')
    api_key = flask.request.args.get('api_key')
    return helper.get_queues(api_key)


@app.route('/api/user/login/',methods=['POST'])
def user_login():
    data = request.json
    email = data['email']
    password = data['password']
    return helper.login(email,password)


@app.route('/api/queue/new/',methods=['POST'])
@validate.api_key
@validate.service
# @validate.user_key
# @validate.info
def add_queue():
    data = request.json
    api_key = flask.request.args.get('api_key')
    service_id = data['service_id']
    user_key = data['user_key']
    info = data['info']

    return helper.add_queue(api_key,service_id,user_key,info)


@app.route('/test',methods=['GET','POST'])
def test():
    return helper.search_test().first_name


@app.route('/db/rebuild',methods=['GET','POST'])
def database_rebuild():
    return helper.rebuild_database()


if __name__ == '__main__':
    app.debug = True
    app.run(port=int(os.environ['PORT']), host='0.0.0.0')