#!/usr/bin/python
##James Parks

import sys
import os

import datetime
import calendar
import pymongo

from PyQt4 import QtGui, QtCore

######################
#USEFUL MONGO COMMANDS
######################

#$ sudo service mongodb start
#$ mongo
#> use DB_NAME ##switch to or create db
#> db.createCollection( 'records', {autoIndexId: true} )
#> db.records.insert( RECORD_DICT )
## auth magic happens
#client = pymongo.MongoClient()
#db = client.healthStats ##name of my database
#records = db.records ##name of my collection

#records.count()
#cur = records.find({})
#for doc in cur:
#    pprint(doc)

def statToMongo(collection, date, weight=0, pressure_h=0, pressure_l=0, sugar_m_time=0.00, sugar_m=0, sugar_e_time=0.00, sugar_e=0):
    month, day, year = date.split('-')
    day = int(day)
    month = int(month)
    if len(year) == 2:
        year = int('20{0}'.format(year))
    else:
        year = int(year)
    dt = datetime.datetime(year, month, day)
    ts = calendar.timegm(dt.timetuple())
    recordDict = {  'date': ts,
                    'weight': float(weight),
                    'pressure_h': int(pressure_h),
                    'pressure_l': int(pressure_l),
                    'sugar_m_time': float(sugar_m_time),
                    'sugar_m': int(sugar_m),
                    'sugar_e_time': float(sugar_e_time),
                    'sugar_e': int(sugar_e)
                 }
    rec_id, status = collection.insert_one(recordDict)
    return rec_id, status


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
        self.ml = QtGui.QFormLayout()

        self.date_edit = QtGui.QLineEdit()
        self.weight_edit = QtGui.QLineEdit()
        self.pressure_edit = QtGui.QLineEdit()
        self.sugar_edit = QtGui.QLineEdit()

        button_layout = QtGui.QHBoxLayout()
        submit_button = QtGui.QPushButton('Submit')
        cancel_button = QtGui.QPushButton('Cancel')

        button_layout.addWidget(submit_button)
        button_layout.addWidget(cancel_button)

        self.ml.addRow('Date', date_edit)
        self.ml.addRow('Weight', weight_edit)
        self.ml.addRow('Pressure', pressure_edit)
        self.ml.addRow('Sugar', sugar_edit)
        self.ml.addItem(button_layout)

        self.connect(submit_button, QtCore.SIGNAL('clicked()'), self.submit)
        self.connect(cancel_button, QtCore.SIGNAL('clicked()'), sys.exit)

        self.setLayout(self.ml)

    def submit(self):
        plan = """        #gather info from fields
        #check to see which fields are filled out
        #   date: mandatory
        #   others: optional
        #if date already exists
        #   should I update?
        #   if sugar already exists
        #       is this the evening sugar?
        #do the update
        """
        print(plan)

if __name__ == '__main__':
    #make an app
    app = QtGui.QApplication(sys.argv)
    #make the window 
    win = statToMongo_UI()
    sys.exit(app.exec_())








