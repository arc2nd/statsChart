import os
import sys
import datetime
import calendar

from PyQt4 import QtGui, QtCore




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

    def get_date(self):
        #return str(self.dateEdit.text())
        q_date = self.dateEdit.date()
        day = int(q_date.day())
        month = int(q_date.month())
        year = str(q_date.year())
        if len(year) == 2:
            year = int('20{0}'.format(year))
        else:
            year = int(year)
        return '{0}-{1}-{2}'.format(year, month, day)

    def get_datetime(self):
        date = self.get_date()
        year, month, day = date.split('-')
        day = int(day)
        month = int(month)
        year = int(year)
        return datetime.datetime(year, month, day)

    def get_timestamp(self, split_char=None):
        dt = self.get_datetime()
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

