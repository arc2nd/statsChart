#!/usr/bin/python
##James Parks

##in here I'll put procedures to query the mongoDB and build appropriate
##pgPlot compatible json files out of that data

#for doc in weights.find( {'date': {'$lt': 1498521600}}, {'_id':0} ):
#    pprint(doc)

import datetime
import calendar

import listProcessing as lp

def get_range(collection=None, dest_key=None, start_date=None, end_date=None):
    start_ts = date_to_ts(start_date)
    end_ts = date_to_ts(end_date)
    print('s: {0}\ne: {1}'.format(start_ts, end_ts))
    date_list = []
    value_list = []
    for doc in collection.find( {'date': {'$gte': start_ts, '$lte': end_ts}}, {'_id':0} ):
        date_list.append(doc['date'])
        value_list.append(doc[dest_key])
    return [date_list, value_list]

def date_to_ts(date=None, split_char='-'):
    month, day, year = date.split(split_char)
    day = int(day)
    month = int(month)
    if len(year) == 2:
        year = int('20{0}'.format(year))
    elif len(year) == 4:
        year = int(year)
    else:
        print('invalid year')
        return

    dt = datetime.datetime(year, month, day)
    ts = calendar.timegm(dt.timetuple())
    return ts

def ts_to_date(ts=None, join_char='-'):
    dt = datetime.datetime.utcfromtimestamp(ts)
    date = dt.strftime('%-m{0}%d{0}%y'.format(join_char))
    return date
