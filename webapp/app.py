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
        if collection == 'Weight':
            coll_store = db.weight
        elif collection == 'Pressure':
            coll_store = db.pressure
        else:
            coll_store = db.sugar
        return coll_store
    except:
        traceback.print_exc(sys.exc_info()[-1])
        print('not connected to mongodb')

def stat_to_mongo(collection=None, value_dict=None):
    coll_store = build_conn(collection)
    if not coll_store.find(value_dict).count():
        rec_id = coll_store.insert_one(value_dict)
        return rec_id.inserted_id
    else:
        print('already found: {0} in DB\nDon\'t want to make a duplicate'.format(value_dict))

def stat_from_mongo(collection):
    print(collection)
    coll_store = build_conn(collection)
    rec_list = []
    ret_list = []
    ret_dict = {'value': 'None'}
    for doc in coll_store.find():  # ( {'date': {'$gte': start_ts, '$lte': end_ts}}, {'_id':0} ):
        rec_list.append(doc)
    for doc in rec_list:
        doc.pop('_id')
        ret_list.append(doc)
    return ret_list



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
        ret_val = stat_from_mongo('Sugar')
        return ret_val
        # return 'Sugar.get'
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
        ret_val = stat_from_mongo('Weight')
        return ret_val
        # return 'Weight.get'
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
        ret_val = stat_from_mongo('Pressure')
        return ret_val
        # return 'Pressure.get'
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
        ret_val = stat_from_mongo('Sugar')
        return ret_val 
        # return 'Query.get'
    def post(self):
        args = parser.parse_args()
        table = args['table']
        ret_val = stat_from_mongo(table)
        return ret_val 
    def put(self):
        return 'Query.put'
    def delete(self):
        return 'Query.delete'

class QueryTable(Resource):
    def get(self, table_id):
        ret_val = stat_from_mongo(table_id)
        return ret_val

##add resources to api
api.add_resource(Sugar, '/Sugar')
api.add_resource(Weight, '/Weight')
api.add_resource(Pressure, '/Pressure')
api.add_resource(Query, '/Query')
api.add_resource(QueryTable, '/Query/<string:table_id>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


