from dateutil.parser import parse as parse_date
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.orderinglist import ordering_list
from werkzeug.security import generate_password_hash, check_password_hash
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
import random
import string

db = db.alchemy

SMS_URL = 'https://post.chikka.com/smsapi/request'
CLIENT_ID = 'ef8cf56d44f93b6ee6165a0caa3fe0d1ebeee9b20546998931907edbb266eb72'
SECRET_KEY = 'c4c461cc5aa5f9f89b701bc016a73e9981713be1bf7bb057c875dbfacff86e1d'
SHORT_CODE = '29290420420'
RANDOM = string.lowercase+string.digits

def save_user(first_name,last_name,email,msisdn,country):
    new_user = User(
        api_key=uuid.uuid4().hex,
        first_name=first_name,
        last_name=last_name,
        email=email,
        msisdn=msisdn,
        country=country
        )
    db.session.add(new_user)
    db.session.commit()

    svc = ''.join(random.sample(RANDOM,6))
    new = Svc(
        msisdn=msisdn,
        svc=svc
        )
    db.session.add(new)
    db.session.commit()
    print 'still okay here'
    return jsonify(
        status='success',
        msisdn=msisdn,
        svc=svc
        ),201

def generate_svc(msisdn):
    existing = Svc.query.filter_by(msisdn=msisdn).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()

    svc = ''.join(random.sample(RANDOM,4))
    new = Svc(
        msisdn=msisdn,
        svc=svc
        )
    db.session.add(new)
    db.session.commit()

    # send_svc(svc,msisdn)
    return jsonify(
        status='success',
        msisdn=msisdn,
        svc=svc #TEMPORARY RETURN
        ),201

def send_svc(svc,msisdn):
    message_body={
        'message_type': 'SEND',
        'message': 'Your security verification number is %s'%svc,
        'client_id': CLIENT_ID,
        'mobile_number': msisdn,
        'secret_key': SECRET_KEY,
        'shortcode': SHORT_CODE,
        'message_id': uuid.uuid4().hex
    }

    sent = False
    while not sent:
        try:
            r = requests.post(SMS_URL,message_body)
            sent = True
            print r.status_code

        except requests.exceptions.ConnectionError as e:
            print "Sending Failed!"
            sleep(5)

def login(msisdn,svc):
    match = Svc.query.filter_by(msisdn=msisdn,svc=svc).first()
    if match == None:
        return jsonify(status='failed',error='Invalid security verification code'),401
    db.session.delete(match)
    db.session.commit()
    user = User.query.filter_by(msisdn=msisdn).first()
    return jsonify(
        status='success',
        api_key=user.api_key,
        first_name=user.first_name,
        last_name=user.last_name,
        msisdn=user.msisdn,
        country=user.country
        ),200

def get_user_queues(api_key):
    user = User.query.filter_by(api_key=api_key).first()
    queue = Queued.query.filter_by(user_id=user.id).first()
    if queue == None:
        return jsonify(
        status='success',
        queue_no=None,
        current=None,
        client_name=None,
        service_name=None,
        estimated_hours='0',
        estimated_minutes='0'
        ),200
    service = Service.query.filter_by(id=queue.service_id).first()

    all_queues = Queued.query.all()
    if service.current == None:
        ahead = 0
    else:
        ahead = all_queues.index(queue)+1
    eta = ahead * service.avg_time

    return jsonify(
        status='success',
        queue_no=queue.queue_no,
        current=service.current,
        client_name=queue.client_name,
        service_name=service.name,
        estimated_hours=str(eta).split(':')[0],
        estimated_minutes=str(eta).split(':')[1]
        ),200

def get_client_queues(api_key):
    client = Client.query.filter_by(api_key=api_key).first()
    queues = Queued.query.filter_by(client_id=client.id).all()
    queued = [e.serialize() for e in queues]
    return jsonify(status='success',queue=queued),200

def generate_number(service_id,client):
    last_queue = Queued.query.filter_by(client_id=client,service_id=service_id).order_by(Queued.timestamp.desc()).first()
    service = Service.query.filter_by(id=service_id).first()
    if last_queue == None:
        new_number = service.code + '1'
    else:
        if int(last_queue.queue_no[2:]) <= 100:
            new_number = service.code + str(int(last_queue.queue_no[2:])+1)
    return new_number

def end_last_transaction(service_id):
    last_transaction = Transaction.query.filter_by(service_id=service_id).order_by(Transaction.start_time.desc()).first()
    last_transaction.end_time = datetime.datetime.now()

    db.session.commit()
    compute_average_time(last_transaction)

def compute_average_time(transaction):
    transaction_time = transaction.end_time - transaction.start_time

    transaction_count = Transaction.query.filter_by(service_id=transaction.service_id).count()

    print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    print transaction_time

    service = Service.query.filter_by(id=transaction.service_id).first()
    service.total_time += transaction_time
    service.avg_time = service.total_time / transaction_count
    db.session.commit()

def log_transaction(queue):
    transaction = Transaction(
        queue_no=queue.queue_no,
        client_id=queue.client_id,
        client_name=queue.client_name,
        user_id=queue.user_id,
        user_name=queue.user_name,
        msisdn=queue.msisdn,
        service_id=queue.service_id,
        service_name=queue.service_name,
        service_desc=queue.service_desc,
        start_time=datetime.datetime.now()
        )
    db.session.add(transaction)
    db.session.commit()

def next_queue(api_key,service_id):
    service = Service.query.filter_by(id=service_id).first()
    queue = Queued.query.filter_by(service_id=service_id).order_by(Queued.timestamp).first()

    if service.current == None:
        if queue == None:
            service.current = None
            return jsonify(
                status='success',
                service_name=service.name,
                current=None,
                remaining=0
                ),200
        service.current = queue.queue_no
        log_transaction(queue)
        db.session.delete(queue)
        db.session.commit()
    else:
        if queue == None:
            service.current = None
            db.session.commit()
            end_last_transaction(service_id)
            return jsonify(
                status='success',
                service_name=service.name,
                current=None,
                remaining=0
                ),200

        service.current = queue.queue_no
        end_last_transaction(service_id)
        log_transaction(queue)
        db.session.delete(queue)    
        db.session.commit()
    queue_count = Queued.query.filter_by(service_id=service_id).count()
    return jsonify(
        status='success',
        service_name=service.name,
        current=queue.queue_no,
        remaining=queue_count,
        ),200


def add_queue(api_key,service_id,msisdn):
    user = User.query.filter_by(msisdn=msisdn).first()
    client = Client.query.filter_by(api_key=api_key).first()
    service = Service.query.filter_by(id=service_id).first()

    if user == None:
        user_id=None
    else:
        user_id=user.id

    new_queue = Queued(
        queue_no=generate_number(service_id,client.id),
        client_id=client.id,
        client_name=client.name,
        user_id=user_id,
        user_name=user.first_name+' '+user.last_name,
        msisdn=msisdn,
        service_id=service_id,
        service_name=service.name,
        service_desc=service.desc,
        timestamp=datetime.datetime.now()
        )

    db.session.add(new_queue)
    db.session.commit()
    return jsonify(status='success'),201

def search_test():
    a = Client.query.filter_by(id='1').first()
    return a

def rebuild_database():
    db.drop_all()
    db.create_all()

    client = Client(
        api_key='435674859374657483949',
        name='BPI - Lucena',
        category='business',
        email='bpi.lucena@gmail.com',
        username='bpilucena',
        password=generate_password_hash('jasper'),
        country='Philippines',
        city='Manila',
        contact_no='09159484200'
        )

    user = User(
        api_key='435674859374657483948',
        first_name='Jasper',
        last_name='Barcelona',
        email='barcelona.jasperoliver@gmail.com',
        msisdn='09159484200',
        country='Philippines',
        )

    user1 = User(
        api_key='435674859374657483950',
        first_name='Joseph ',
        last_name='Sallao',
        email='sallao.joseph@gmail.com',
        msisdn='09183339068',
        country='Philippines',
        )

    user2 = User(
        api_key='435674859374657483951',
        first_name='Tobie',
        last_name='Delos Reyes',
        email='delosreyes.tobie@gmail.com',
        msisdn='09183339069',
        country='Philippines',
        )

    user3 = User(
        api_key='435674859374657483952',
        first_name='Janno  ',
        last_name='Armamento',
        email='armamento.janno@gmail.com',
        msisdn='09183339060',
        country='Philippines',
        )

    service = Service(
        client_id=1,
        name='Bank Deposit',
        desc='Deposit cash to bank account',
        code='BD',
        avg_time = datetime.timedelta(hours=00,minutes=00,seconds=00),
        current = None
        )

    service1 = Service(
        client_id=1,
        name='Withdrawal',
        desc='Withdraw cash from bank account',
        code='BW',
        avg_time = datetime.timedelta(hours=00,minutes=00,seconds=00),
        current = None
        )

    db.session.add(client)
    db.session.add(user)
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(service)
    db.session.add(service1)
    db.session.commit()

    return jsonify(status='success'), 200