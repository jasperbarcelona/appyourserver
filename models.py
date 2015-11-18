import flask, flask.views
from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy
import helpers.db_conn as db
from sqlalchemy import DateTime, Interval
import datetime

db = db.alchemy

class Client(db.Model):
    config_collection_name = 'client'

    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(30))
    category = db.Column(db.String(30))
    email = db.Column(db.String(60))
    username = db.Column(db.String(30))
    password = db.Column(db.String(70))
    contact_no = db.Column(db.String(15))
    country = db.Column(db.String(30))
    city = db.Column(db.String(30))

    def serialize(self):
        return {
            'id': self.id,
            'api_key': self.api_key,
            'name':self.name,
            'category':self.category,
            'email':self.email,
            'username':self.username,
            'password':self.password,
            'contact_no':self.contact_no,
            'country':self.country,
            'city':self.city
        }

class Svc(db.Model):
    config_collection_name = 'client'

    id = db.Column(db.Integer, primary_key=True)
    msisdn = db.Column(db.String(15), unique=True)
    svc = db.Column(db.String(5))
    def serialize(self):
        return {
            'id': self.id,
            'msisdn': self.msisdn,
            'svc':self.svc,
        }


class User(db.Model):
    config_collection_name = 'client'

    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(32), unique=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(60))
    msisdn = db.Column(db.String(15))
    country = db.Column(db.String(30))

    def serialize(self):
        return {
            'id': self.id,
            'api_key': self.api_key,
            'first_name':self.first_name,
            'last_name':self.last_name,
            'email':self.email,
            'msisdn':self.msisdn,
            'country':self.country
        }


class Service(db.Model):
    config_collection_name = 'service'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    name = db.Column(db.String(30))
    desc = db.Column(db.String)
    code = db.Column(db.String(10))
    avg_time = db.Column(Interval)
    current = db.Column(db.String(10))
    total_time = db.Column(Interval,default=datetime.timedelta(hours=0,minutes=0,seconds=0))

    def serialize(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'name':self.name,
            'desc':self.desc,
            'avg_time':self.avg_time,
            'current':self.current,
            'code':self.code,
            'total_time':self.total_time
        }


class Queued(db.Model, object):
    config_collection_name = 'queued'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, nullable=True)
    service_id = db.Column(db.Integer)
    queue_no = db.Column(db.String(10))
    msisdn = db.Column(db.String(15), nullable=True)
    client_name = db.Column(db.String(30))
    user_name = db.Column(db.String(60), nullable=True)
    service_name = db.Column(db.String(30))
    service_desc = db.Column(db.String)
    timestamp = db.Column(DateTime)

    def serialize(self):
        return {
            'id': self.id,
            'client_id':self.client_id,
            'user_id':self.user_id,
            'service_id':self.service_id,
            'queue_no': self.queue_no,
            'msisdn':self.msisdn,
            'client_name':self.client_name,
            'user_name':self.user_name,
            'service_name':self.service_name,
            'service_desc':self.service_desc,
            'timestamp':self.timestamp
        }


class Transaction(db.Model, object):
    config_collection_name = 'transaction'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, nullable=True)
    service_id = db.Column(db.Integer)
    queue_no = db.Column(db.String(10))
    msisdn = db.Column(db.String(15), nullable=True)
    client_name = db.Column(db.String(30))
    user_name = db.Column(db.String(60), nullable=True)
    service_name = db.Column(db.String(30))
    service_desc = db.Column(db.String)
    start_time = db.Column(DateTime)
    end_time = db.Column(DateTime,default=None)

    def serialize(self):
        return {
            'id': self.id,
            'client_id':self.client_id,
            'user_id':self.user_id,
            'service_id':self.service_id,
            'queue_no': self.queue_no,
            'msisdn':self.msisdn,
            'client_name':self.client_name,
            'user_name':self.user_name,
            'service_name':self.service_name,
            'service_desc':self.service_desc,
            'start_time':self.start_time,
            'end_time':self.end_time
        }