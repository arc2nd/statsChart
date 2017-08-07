#!/usr/bin/python
##James Parks

import sys
import os

import datetime
import calendar
import pymongo

from PyQt4 import QtGui, QtCore

######################
##MongoDB structure
######################
##SUGARS
##_id, date, time, value
##WEIGHTS
##_id, date, value
##PRESSURE_LS
##_id, date, value
##PRESSURE_HS
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

        self.date_edit = dateWidget()
        self.weight_edit = weightWidget()
        self.pressure_edit = pressureWidget()
        self.sugar_edit = sugarWidget()

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

        #pprint(self.date_dict)
        #pprint(self.weight_dict)
        #pprint(self.pressure_h_dict)
        #pprint(self.pressure_l_dict)
        #pprint(self.sugar_dict)

    def submit(self):
        self.collect()

        stat_to_mongo(self.sugar, self.sugar_dict)
        stat_to_mongo(self.weight, self.weight_dict)
        stat_to_mongo(self.pressure_l, self.pressure_l_dict)
        stat_to_mongo(self.pressure_h, self.pressure_h_dict)
        print('submitted')


class dateWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(dateWidget, self).__init__()
        self.layout = QtGui.QHBoxLayout()
        #self.dateEdit = QtGui.QLineEdit()
        self.dateEdit = QtGui.QDateEdit(datetime.date.today())
        self.dateEdit.calendarPopup()
        self.dateEdit.setDisplayFormat('yyyy.MM.dd')
        self.layout.addWidget(self.dateEdit)
        self.setLayout(self.layout)

    def get_value(self):
        #return str(self.dateEdit.text())
        return self.dateEdit.date()

    def get_timestamp(self, split_char=None):
        import datetime
        import calendar
        q_date = self.get_value()
        day = int(q_date.day())
        month = int(q_date.month())
        year = str(q_date.year())
        if len(year) == 2:
            year = int('20{0}'.format(year))
        else:
            year = int(year)
        dt = datetime.datetime(year, month, day)
        ts = calendar.timegm(dt.timetuple())
        return ts


class weightWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(weightWidget, self).__init__()
        self.layout = QtGui.QHBoxLayout()
        self.weightEdit = QtGui.QLineEdit()
        self.layout.addWidget(self.weightEdit)
        self.setLayout(self.layout)

    def get_value(self):
        return str(self.weightEdit.text())


class pressureWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(pressureWidget, self).__init__()
        self.layout = QtGui.QHBoxLayout()
        self.pressureHighEdit = QtGui.QLineEdit()
        self.pressureHighEdit.setPlaceholderText('high')
        self.pressureLowEdit = QtGui.QLineEdit()
        self.pressureLowEdit.setPlaceholderText('low')
        self.layout.addWidget(self.pressureHighEdit)
        self.layout.addWidget(self.pressureLowEdit)
        self.setLayout(self.layout)

    def get_value(self):
        return [str(self.pressureHighEdit.text()), str(self.pressureLowEdit.text())]


class sugarWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(sugarWidget, self).__init__()
        self.layout = QtGui.QHBoxLayout()
        self.sugarTimeEdit = QtGui.QTimeEdit(datetime.datetime.now().time())
        self.sugarTimeEdit.setDisplayFormat('HH:mm')
        self.sugarValueEdit = QtGui.QLineEdit()
        self.layout.addWidget(self.sugarTimeEdit)
        self.layout.addWidget(self.sugarValueEdit)
        self.setLayout(self.layout)

    def get_value(self):
        q_time = self.sugarTimeEdit.time()
        txtTime = '{0}.{1}'.format(q_time.hour(), q_time.minute())
        return [str(txtTime), str(self.sugarValueEdit.text())]


if __name__ == '__main__':
    #make an app
    app = QtGui.QApplication(sys.argv)
    #make the window 
    win = statToMongo_UI()
    sys.exit(app.exec_())








