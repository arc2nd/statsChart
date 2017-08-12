#!/usr/bin/python
##James Parks

import sys
import os

import datetime
import calendar
import pymongo

from PyQt4 import QtGui, QtCore
import widgets as wdg
######################
##MongoDB structure
######################
##SUGAR
##_id, date, time, value
##WEIGHT
##_id, date, value
##PRESSURE_L
##_id, date, value
##PRESSURE_H
##_id, date, value

######################
#USEFUL MONGO COMMANDS
######################

#$ sudo service mongodb start
#$ mongo
#> use DB_NAME ##switch to or create db
#> db.createCollection( 'records', {autoIndexId: true} )
#> db.records.insert( RECORD_DICT )
## auth magic happens
#$ python
#>>> client = pymongo.MongoClient()
#>>> db = client.DB_NAME ##name of my database
#>>> records = db.records ##name of my collection

#records.count()
#cur = records.find({})
#for doc in cur:
#    pprint(doc)

def stat_to_mongo(collection=None, value_dict=None):
    if not collection.find( value_dict ).count():
        rec_id = collection.insert_one( value_dict )
        return rec_id.inserted_id
    else:
        print('already found: {0} in DB\nDon\'t want to make a duplicate'.format(value_dict))


class statToMongo_UI(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(statToMongo_UI, self).__init__()

        self.statusBar().showMessage('ready')
        self.setWindowTitle('Stat to Mongo')
        self.setGeometry(300, 300, 250, 150)

        self.main_widget = statMainWidget()
        self.setCentralWidget(self.main_widget)

        self.show()


class statMainWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(statMainWidget, self).__init__()
        client = pymongo.MongoClient()
        db = client.healthStats
        self.weight = db.weight
        self.pressure_h = db.pressure_h
        self.pressure_l = db.pressure_l
        self.sugar = db.sugar

        self.date_dict = {}
        self.weight_dict = {}
        self.pressure_h_dict = {}
        self.pressure_l_dict = {}
        self.sugar_dict = {}

        self.ml = QtGui.QFormLayout()

        self.date_edit = wdg.dateWidget()
        self.weight_edit = wdg.weightWidget()
        self.pressure_edit = wdg.pressureWidget()
        self.sugar_edit = wdg.sugarWidget()

        button_layout = QtGui.QHBoxLayout()
        print_button = QtGui.QPushButton('Print')
        submit_button = QtGui.QPushButton('Submit')
        cancel_button = QtGui.QPushButton('Cancel')

        button_layout.addWidget(print_button)
        button_layout.addWidget(submit_button)
        button_layout.addWidget(cancel_button)

        self.ml.addRow('Date', self.date_edit)
        self.ml.addRow('Weight', self.weight_edit)
        self.ml.addRow('Pressure', self.pressure_edit)
        self.ml.addRow('Sugar', self.sugar_edit)
        self.ml.addItem(button_layout)

        self.connect(print_button, QtCore.SIGNAL('clicked()'), self.collect)
        self.connect(submit_button, QtCore.SIGNAL('clicked()'), self.submit)
        self.connect(cancel_button, QtCore.SIGNAL('clicked()'), sys.exit)

        self.setLayout(self.ml)

    def collect(self):
        from pprint import pprint
        
        date = self.date_edit.get_timestamp()
        weight = self.weight_edit.get_value()
        pressure_h, pressure_l = self.pressure_edit.get_value()
        sugar_time, sugar_val = self.sugar_edit.get_value()

        if date:
            self.date_dict = {'date': date}
            if weight:
                self.weight_dict = {'date': date, 'value': weight}
            if pressure_h and pressure_l:
                self.pressure_h_dict = {'date': date, 'value': pressure_h}
                self.pressure_l_dict = {'date': date, 'value': pressure_l}
            if sugar_time and sugar_val:
                self.sugar_dict = {'date': date, 'time': sugar_time, 'value': sugar_val}
        else:
            print('Can\'t find date. Can\'t submit')

        pprint(self.date_dict)
        pprint(self.weight_dict)
        pprint(self.pressure_h_dict)
        pprint(self.pressure_l_dict)
        pprint(self.sugar_dict)

    def submit(self):
        self.collect()

        stat_to_mongo(self.sugar, self.sugar_dict)
        stat_to_mongo(self.weight, self.weight_dict)
        stat_to_mongo(self.pressure_l, self.pressure_l_dict)
        stat_to_mongo(self.pressure_h, self.pressure_h_dict)
        print('submitted')


if __name__ == '__main__':
    #make an app
    app = QtGui.QApplication(sys.argv)
    #make the window 
    win = statToMongo_UI()
    sys.exit(app.exec_())








