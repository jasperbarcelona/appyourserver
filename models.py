import flask, flask.views
from flask import Flask, request
from flask.ext.sqlalchemy import SQLAlchemy
import helpers.db_conn as db

db = db.alchemy

class Client(db.Model):
    config_collection_name = 'client'

    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(32), unique=True)
    name = db.Column(db.String(30))
    category = db.Column(db.String(30))
    email = db.Column(db.String(60))
    username = db.Column(db.String(30))
    password = db.Column(db.String(30))
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


class User(db.Model):
    config_collection_name = 'client'

    id = db.Column(db.Integer, primary_key=True)
    api_key = db.Column(db.String(32), unique=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    email = db.Column(db.String(60))
    password = db.Column(db.String(30))
    contact_no = db.Column(db.String(15))
    country = db.Column(db.String(30))
    city = db.Column(db.String(30))
    preffered_alert_time = db.Column(db.Integer)
    preffered_alert_number = db.Column(db.Integer)
    user_key = db.Column(db.String(4))

    def serialize(self):
        return {
            'id': self.id,
            'api_key': self.api_key,
            'first_name':self.first_name,
            'last_name':self.last_name,
            'email':self.email,
            'password':self.password,
            'contact_no':self.contact_no,
            'country':self.country,
            'city':self.city,
            'preffered_alert_time':self.preffered_alert_time,
            'preffered_alert_number':self.preffered_alert_number,
            'user_key':self.user_key
        }


class Service(db.Model):
    config_collection_name = 'service'

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer)
    name = db.Column(db.String(30))
    desc = db.Column(db.String)
    code = db.Column(db.String(10))
    avg_time = db.Column(db.Time)
    current = db.Column(db.String(10))

    def serialize(self):
        return {
            'id': self.id,
            'client_id': self.client_id,
            'name':self.name,
            'desc':self.desc,
            'avg_time':self.avg_time,
            'current':self.current,
            'code':self.code
        }


class Queued(db.Model, object):
    config_collection_name = 'queued'

    id = db.Column(db.Integer, primary_key=True)
    queue_no = db.Column(db.String(10))
    client_id = db.Column(db.Integer)
    client_name = db.Column(db.String(30))
    user_id = db.Column(db.Integer, nullable=True)
    service_id = db.Column(db.Integer)
    service_name = db.Column(db.String(30))
    service_desc = db.Column(db.String)
    info = db.Column(db.PickleType())
    timestamp = db.Column(db.String(50))

    def serialize(self):
        return {
            'id': self.id,
            'queue_no': self.queue_no,
            'client_id':self.client_id,
            'client_name':self.client_name,
            'user_id':self.user_id,
            'service_id':self.service_id,
            'service_name':self.service_name,
            'service_desc':self.service_desc,
            'info':self.info,
            'timestamp':self.timestamp
        }