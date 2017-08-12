#!/usr/bin/python
##James Parks

##in here I'll put procedures to query the mongoDB and build appropriate
##pgPlot compatible json files out of that data

#for doc in weights.find( {'date': {'$lt': 1498521600}}, {'_id':0} ):
#    pprint(doc)

import sys 
import os
from pprint import pprint

import datetime
import calendar
import pymongo

from PyQt4 import QtGui, QtCore, QtSvg, QtWebKit

import listProcessing as lp
import widgets as wdg
def get_range(collection=None, source_key=None, start_date=None, end_date=None):
    start_ts = date_to_ts(start_date)
    end_ts = date_to_ts(end_date)
    print('s: {0}\ne: {1}'.format(start_ts, end_ts))
    date_list = []
    value_list = []
    for doc in collection.find( {'date': {'$gte': start_ts, '$lte': end_ts}}, {'_id':0} ):
        date_list.append(ts_to_date(doc['date']))
        value_list.append(doc[source_key])
    return [date_list, value_list]

def build_json(collection=None, source_key=None, dest_key=None, start_date=None, end_date=None, sample_rate=1):
    date_list = []
    value_list = []
    ret_dict = {dest_key: get_range(collection, source_key=source_key, start_date=start_date, end_date=end_date)}
    if sample_rate > 1:
        ret_dict['{0}.sample'.format(dest_key)] = lp.down_sample2(ret_dict, dest_key, sample_rate)
    return ret_dict

class fromMongo_UI(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(fromMongo_UI, self).__init__()

        self.statusBar().showMessage('ready')
        self.setWindowTitle('from Mongo')
        self.setGeometry(300, 300, 500, 300)

        self.main_widget = fromMainWidget()
        self.setCentralWidget(self.main_widget)

        self.show()

class fromMainWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(fromMainWidget, self).__init__()
        client = pymongo.MongoClient()
        db = client.healthStats
        self.weight = db.weight
        self.pressure_h = db.pressure_h
        self.pressure_l = db.pressure_l
        self.sugar = db.sugar

        self.collections_list = [self.weight, self.pressure_h, self.pressure_l, self.sugar]

        self.date_dict = {}
        self.weight_dict = {}
        self.pressure_h_dict = {}
        self.pressure_l_dict = {}
        self.sugar_dict = {}

        self.ml = QtGui.QVBoxLayout()

        start_label = QtGui.QLabel('Start:')
        self.start_date_edit = wdg.dateWidget()
        end_label = QtGui.QLabel('End:')
        self.end_date_edit = wdg.dateWidget()

        button_layout = QtGui.QHBoxLayout()
        report_button = QtGui.QPushButton('Submit')

        button_layout.addWidget(start_label)
        button_layout.addWidget(self.start_date_edit)
        button_layout.addWidget(end_label)
        button_layout.addWidget(self.end_date_edit)
        button_layout.addWidget(report_button)
        #graph = QtGui.QLabel()
        #graph.setPixmap(QtGui.QPixmap('../sugar2.png'))
        graph = QtWebKit.QWebView()
        with open('../sugar2.svg', 'r') as fp:
            contents = fp.read()
        graph.setContent(contents)
        self.ml.addLayout(button_layout)
        self.ml.addWidget(graph)

        self.connect(report_button, QtCore.SIGNAL('clicked()'), self.submit)

        self.setLayout(self.ml)

    def submit(self):
        start_date = self.start_date_edit.get_date()
        end_date = self.end_date_edit.get_date()
        collection = self.weight
        this_json = build_json(collection=collection, 
                               source_key='value', 
                               dest_key='weight', 
                               start_date=start_date, 
                               end_date=end_date, 
                               sample_rate=1)
        pprint(this_json)
        plan = """
        #get the date range from the graph
        #turn the data into a json
        #use pgPlot to turn the data into an SVG
        #show the SVG in the graph_label as a pixmap
        """
        print(plan)


def date_to_ts(date=None, split_char='-'):
    year, month, day = date.split(split_char)
    day = int(day)
    month = int(month)
    if len(year) == 2:
        year = '20{0}'.format(year)
        year = int(year)
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


if __name__ == '__main__':
    #make an app
    app = QtGui.QApplication(sys.argv)
    #make the window 
    win = fromMongo_UI()
    sys.exit(app.exec_())
