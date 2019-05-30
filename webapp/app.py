#!/usr/bin/env python

import sys
import traceback

import pymongo

from flask import Flask  # , render_template, Response, redirect, url_for, request, session, flash
from flask_restful import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app)

# set up the database stuff
from pymongo.monitoring import ServerHeartbeatListener
 
class HeartbeatFailedListener(ServerHeartbeatListener):
    def started(self, event):
        pass
 
    def succeeded(self, event):
        pass
 
    def failed(self, event):
        print('Heartbeat failed with exception: ', event.reply)
 
heartbeat_listener = HeartbeatFailedListener()
# conn = MongoClient('127.0.0.1', 27017, username='admin', password='admin',
#                    serverSelectionTimeoutMS=1000, event_listeners=[heartbeat_listener])




host = 'stats_mongo'  # '127.0.0.1'
# host = '192.168.0.3'
port = 27017

def build_conn(collection):
    try:
        client = pymongo.MongoClient('mongodb://{}:{}/'.format(host, port), 
                    serverSelectionTimeoutMS=1000, 
                    event_listeners=[heartbeat_listener])
        db = client.healthStats
        if client:
            print('connected to mongodb')
        if collection == 'weight':
            coll_store = db.weight
        if collection == 'pressure':
            coll_store = db.pressure
        if collection == 'sugar':
            coll_store = db.sugar
        return coll_store
    except:
        traceback.print_exc(sys.exc_info())
        print('not connected to mongodb')

def stat_to_mongo(collection=None, value_dict=None):
    coll_store = build_conn(collection)
    if not coll_store.find(value_dict).count():
        rec_id = coll_store.insert_one(value_dict)
        return rec_id.inserted_id
    else:
        print('already found: {0} in DB\nDon\'t want to make a duplicate'.format(value_dict))

def stat_from_mongo(collection, source_key='value'):
    coll_store = build_conn(collection)
    rec_list = []
    date_list = []
    value_list = []
    time_list = []
    for doc in coll_store.find():  # ( {'date': {'$gte': start_ts, '$lte': end_ts}}, {'_id':0} ):
        rec_list.append(doc)
    for doc in rec_list:
        date_list.append(doc['date'])
        value_list.append(doc[source_key])
        time_list.append(doc['time'])
    ret_dict = {'dates':date_list, 'times':time_list, 'values':value_list}
    return ret_dict



# set up the REST stuff
parser = reqparse.RequestParser()
parser.add_argument('value')
parser.add_argument('date')
parser.add_argument('time')
parser.add_argument('min')
parser.add_argument('max')
parser.add_argument('table')


class Sugar(Resource):
    def get(self):
        return 'Sugar.get'
    def post(self):
        args = parser.parse_args()
        date = args['date']
        time = args['time']
        value = args['value']
        data_dict = {'date': date, 'time':time, 'value':value}
        stat_to_mongo('sugar', data_dict)
        return 'Sugar.post'
    def put(self):
        return 'Sugar.put'
    def delete(self):
        return 'Sugar.delete'

class Weight(Resource):
    def get(self):
        return 'Weight.get'
    def post(self):
        args = parser.parse_args()
        date = args['date']
        value = args['value']
        data_dict = {'date':date, 'value':value}
        stat_to_mongo('weight', data_dict)
        return 'Weight.post'
    def put(self):
        return 'Weight.put'
    def delete(self):
        return 'Weight.delete'

class Pressure(Resource):
    def get(self):
        return 'Pressure.get'
    def post(self):
        args = parser.parse_args()
        date = args['date']
        min_val = args['min']
        max_val = args['max']
        data_dict = {'date': date, 'min':min_val, 'max':max_val}
        stat_to_mongo('pressure', data_dict)
        return 'Pressure.post'
    def put(self):
        return 'Pressure.put'
    def delete(self):
        return 'Pressure.delete'

class Query(Resource):
    def get(self):
        return 'Query.get'
    def post(self):
        args = parser.parse_args()
        date = args['date']
        time = args['time']
        table = args['table']
        ret_val = stat_from_mongo(table, 'value')
        return ret_val
    def put(self):
        return 'Query.put'
    def delete(self):
        return 'Query.delete'

##add resources to api
api.add_resource(Sugar, '/Sugar')
api.add_resource(Weight, '/Weight')
api.add_resource(Pressure, '/Pressure')
api.add_resource(Query, '/Query')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


