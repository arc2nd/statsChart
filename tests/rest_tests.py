#!/usr/bin/env python

import requests
import datetime

url = 'http://192.168.0.3:8580'

def sugar_test(date, time, value):
    end_point = '{}/Sugar'.format(url)
    data_dict = {'date':date, 'time':time, 'value':value}
    resp = requests.post(end_point, data_dict)
    print(resp.text)
    print('sugar: {}'.format(resp.status_code))

def weight_test(date, value):
    end_point = '{}/Weight'.format(url)
    data_dict = {'date':date, 'value':value}
    resp = requests.post(end_point, data_dict)
    print(resp.text)
    print('weight: {}'.format(resp.status_code))

def pressure_test(date, high, low):
    end_point = '{}/Pressure'.format(url)
    data_dict = {'date':date, 'min':low, 'max':high}
    resp = requests.post(end_point, data_dict)
    print(resp.text)
    print('pressure: {}'.format(resp.status_code))

def query_test(table):
    end_point = '{}/Query'.format(url)
    data_dict = {'table': table}
    resp = requests.post(end_point, data_dict)
    print(resp.text)
    print('query: {}'.format(resp.status_code))

if __name__ == '__main__':
    today = datetime.datetime.now()
    str_today = '{}{}{}'.format(today.year, str(today.month).zfill(2), str(today.day).zfill(2))
    str_now = '{}.{}'.format(str(today.hour).zfill(2), str(today.minute).zfill(2))

    value = 192.6
    weight_test(str_today, value)
    
    value = 92
    sugar_test(str_today, str_now, value)

    p_h = 117
    p_l = 85
    pressure_test(str_today, p_h, p_l)

    query_test('Weight')
