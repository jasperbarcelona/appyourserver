from dateutil.parser import parse as parse_date
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.orderinglist import ordering_list
from flask import render_template, request, jsonify
from functools import update_wrapper
from flask import session, redirect
from datetime import timedelta
from datetime import datetime
from functools import wraps
import threading
from threading import Timer
from multiprocessing.pool import ThreadPool
import cStringIO
from werkzeug.datastructures import FileStorage
from multiprocessing.pool import ThreadPool
from werkzeug import secure_filename
from models import *
from time import sleep
import requests
import datetime
import time
import json
import uuid
import os
import db_conn as db
import json

db = db.alchemy

def login(email,password):
    user = User.query.filter_by(email=email,password=password).first()
    if user == None:
        return jsonify(success=False)
    return jsonify(
        success=True,
        api_key=user.api_key,
        first_name=user.first_name,
        last_name=user.last_name,
        contact_no=user.contact_no,
        country=user.country,
        city=user.city,
        preffered_alert_time=user.preffered_alert_time,
        preffered_alert_number=user.preffered_alert_number,
        user_key=user.user_key
        )


def get_queues(api_key):
    client = Client.query.filter_by(api_key=api_key).first()
    if client != None:
        queues = Queued.query.filter_by(client_id=client.id).all()
    else:
        user = User.query.filter_by(api_key=api_key).first()
        queues = Queued.query.filter_by(user_id=user.id).all()
    queued = [e.serialize() for e in queues]
    return jsonify(queue=queued)

def generate_number(service_id,client):
    last_queue = Queued.query.filter_by(client_id=client,service_id=service_id).order_by(Queued.timestamp.desc()).first()
    service = Service.query.filter_by(id=service_id).first()
    if last_queue == None:
        new_number = service.code + '1'
    else:
        if int(last_queue.queue_no[2:]) <= 100:
            new_number = service.code + str(int(last_queue.queue_no[2:])+1)
    return new_number

def add_queue(api_key,service_id,user_key,info):
    user = User.query.filter_by(user_key=user_key).first()
    client = Client.query.filter_by(api_key=api_key).first()
    service = Service.query.filter_by(id=service_id).first()

    if user == None:
        user_id=''
    else:
        user_id=user.id

    new_queue = Queued(
        queue_no=generate_number(service_id,client.id),
        client_id=client.id,
        client_name=client.name,
        user_id=user_id,
        service_id=service_id,
        service_name=service.name,
        service_desc=service.desc,
        info=info,
        timestamp=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
        )

    db.session.add(new_queue)
    db.session.commit()
    return jsonify(Success=True),201

def search_test():
    a = Client.query.filter_by(id='1').first()
    return a

def rebuild_database():
    db.drop_all()
    db.create_all()

    client = Client(
        api_key='435674859374657483948',
        name='BPI - Lucena',
        category='business',
        email='bpi.lucena@gmail.com',
        username='bpilucena',
        password='jasper',
        country='Philippines',
        city='Manila',
        contact_no='09159484200'
        )

    user = User(
        api_key='435674859374657483948',
        first_name='Jasper',
        last_name='Barcelona',
        email='barcelona.jasperoliver@gmail.com',
        password='jasper',
        contact_no='09159484200',
        country='Philippines',
        city='Manila',
        preffered_alert_time=10,
        preffered_alert_number=5,
        user_key='1234'
        )

    service = Service(
        client_id=1,
        name='Bank Deposit',
        desc='Deposit cash to bank account',
        code='BD',
        avg_time = datetime.datetime.now().time(),
        current = 'BD1'
        )

    info={}
    info['senderAccount'] = '123456789'
    info['receiverAccount'] = '987654321'

    queued = Queued(
        queue_no='BD1',
        client_id=1,
        user_id = 1,
        service_id = 1,
        info = info,
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S:%f')
        )

    db.session.add(client)
    db.session.add(user)
    db.session.add(service)
    db.session.add(queued)
    db.session.commit()

    return jsonify(Success=True), 200