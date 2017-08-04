#!/usr/bin/python

##EXAMPLE USAGE:
## $ python stats_extract.py
##      this will create a number of .json files
## $ ./xyPlot.py -g line -l --wi 11 --he 4 -t 'Weight' -f ../statsChart/weight_20170701.json 
## $ ./xyPlot.py -g line -l --wi 11 --he 4 -t 'Blood Pressure' -f ../statsChart/pressure_20170701.json 
## $ ./xyPlot.py -g line -l --wi 11 --he 4 -t 'Blood Sugar' -f ../statsChart/sugar_20170701.json 


import os
import re
import datetime

import listProcessing as lp

test_date = '06-26-17'
test_weight = '(180.2)'
test_pressure = '118-62'
test_sugar = '17.17.     122'

def extract_data(this_file, sample_rate=7):
    if this_file != '' and os.path.exists(this_file):
        with open(this_file, 'r') as fp:
            file_contents = fp.read()
    else:
        file_contents = r'6-26-17     (180.2)     118-62\n     17.17     122'

    date = None
    weight = None
    pressure = None
    time = None
    val = None

    date_pattern = '(?P<date>\d+-\d+-\d+)'
    weight_pattern = '(?P<weight>\(\d+.\d+\))'
    #blood_pressure_pattern = '(\d{1,2})(\d{2,3}-\d+)(?!\d+)'
    blood_pressure_pattern = '(?P<pressure>(\d{1,2})(\d{2,3}-\d+)(?!\d+))'
    #blood_sugar_pattern = r'(\d{1,2}\.\d{2}).(\s+)(\d{2,3})'
    blood_sugar_pattern = r'(?P<time>\d{1,2}\.\d{2}).(\s+)(?P<val>\d{2,3})'

    date_RE = re.compile(date_pattern)
    weight_RE = re.compile(weight_pattern)
    blood_pressure_RE = re.compile(blood_pressure_pattern)
    blood_sugar_RE = re.compile(blood_sugar_pattern)

    weight_dict = {}
    weight2_dict = {}
    pressure_dict = {}
    pressure2_dict = {}
    sugar_dict = {}
    sugar2_dict = {}
    sugarTime_dict = {}
    bmi_dict = {}
    bmi2_dict = {}

    date_list = []
    weight_list = []
    pressure_h_list = []
    pressure_l_list = []
    sugar_morning_list = []
    sugar_mTime_list = []
    sugar_evening_list = []
    sugar_eTime_list=[]

    ##This is the part where we run out text file through the
    ##Regular Expressions and extract all of the data into lists
    for this_line in file_contents.splitlines():
        splits = list(set(this_line.split(' ')))
        
        date_match = date_RE.search(this_line)
        weight_match = weight_RE.search(this_line)
        blood_pressure_match = blood_pressure_RE.search(this_line)
        blood_sugar_match = blood_sugar_RE.search(this_line)

        if date_match:
            date = date_match.groupdict()['date']
            date_list.append(str(date))
            print('Date: {0}'.format(str(date)))
            morning_val = 0
            evening_val = 0
        if weight_match:
            weight = weight_match.groupdict()['weight']
            if weight.startswith('('):
                weight = weight[1:]
            if weight.endswith(')'):
                weight = weight[:-1]
            print('\tWeight: {0}'.format(weight))
            #weight_dict[date] = weight
            weight_list.append(float(weight))
            #weight2_dict[date] = weight
        if blood_pressure_match:
            pressure = blood_pressure_match.groupdict()['pressure']
            if pressure.endswith('\\n'):
                pressure = pressure[:-2]
            print('\tPressure: {0}'.format(pressure))
            #pressure_dict[date] = pressure
            pressure_h, pressure_l = pressure.split('-')
            pressure_h_list.append(float(pressure_h))
            pressure_l_list.append(float(pressure_l))
            #pressure2_dict[date] = [pressure_h, pressure_l]
        if blood_sugar_match:
            time = blood_sugar_match.groupdict()['time']
            val = blood_sugar_match.groupdict()['val']
            print('\tSugar: {0},{1}'.format(time,val))
            if len(time) < 5:
                sugar_mTime_list.append(time)
                #sugar_morning_dict[date] = val
                sugar_morning_list.append(int(val))
                morning_val = val
            if len(time) >=5:
                sugar_eTime_list.append(time)
                #sugar_evening_dict[date] = val
                sugar_evening_list.append(int(val))
                evening_val = val
            #if morning_val != 0 and evening_val != 0:
            #    sugar2_dict[date] = [morning_val, evening_val]

        #print('Date: {0}, Weight: {1}, Pressure: {2}, Sugar: {3}'.format(date, weight, pressure, '{0},{1}'.format(time,val)))

    ##Set up some variables
    today = datetime.date.today()
    fmt_today = '{:%Y%m%d}'.format(today)
    weight_path = 'weight_{0}.json'.format(fmt_today)
    weight2_path = 'weight2_{0}.json'.format(fmt_today)
    pressure_path = 'pressure_{0}.json'.format(fmt_today)
    pressure2_path = 'pressure2_{0}.json'.format(fmt_today)
    sugar_path = 'sugar_{0}.json'.format(fmt_today)
    sugar2_path = 'sugar2_{0}.json'.format(fmt_today)
    sugarTime_path = 'sugarT_{0}.json'.format(fmt_today)
    bmi_path = 'bmi_{0}.json'.format(fmt_today)
    bmi2_path = 'bmi2_{0}.json'.format(fmt_today)

    ##Put data into the weight dict (don't need to normalize as it's only one list)
    weight_dict['weight'] = [range(0,len(weight_list)), weight_list]
    weight_dict['weight.sample'] = lp.down_sample2(weight_dict, 'weight', sample_rate)
    weight2_dict['weight'] = [date_list, weight_list]
    weight2_dict['wieght.sample'] = lp.down_sample2(weight2_dict, 'weight', sample_rate)

    ##Put data into the pressure dict
    ##      make sure the lists are of equal length
    ph_norm_list, pl_norm_list = lp.normalize_two_lists(pressure_h_list, pressure_l_list)

    ##      put data and sampled data into pressure dict
    pressure_dict['high'] = [range(0, len(pressure_h_list)), ph_norm_list]
    pressure_dict['low'] = [range(0, len(pressure_l_list)), pl_norm_list]
    pressure_h_sample_list = lp.down_sample2(pressure_dict, 'high', sample_rate)
    pressure_l_sample_list = lp.down_sample2(pressure_dict, 'low', sample_rate)
    pressure_dict['high.sample'] = pressure_h_sample_list
    pressure_dict['low.sample'] = pressure_l_sample_list

    ##      put data and sampled data into pressure2 dict
    pressure2_dict['high'] = [date_list, ph_norm_list]
    pressure2_dict['low'] = [date_list, pl_norm_list]
    pressure2_dict['high.sample'] = lp.down_sample2(pressure2_dict, 'high', sample_rate)
    pressure2_dict['low.sample'] = lp.down_sample2(pressure2_dict, 'low', sample_rate)

    ##Put data into the sugar and sugar2 dicts
    ##      make sure the lists are of equal length
    sm_norm_list, se_norm_list = lp.normalize_two_lists(sugar_morning_list, sugar_evening_list)

    ##      add morning and evening to sugar dict and sugar2 dict
    sugar_dict['morning'] = [range(0, len(sm_norm_list)), sm_norm_list] ##0 to end of list
    sugar_dict['evening'] = [range(0, len(se_norm_list)), se_norm_list] ##0 to end of list
    sugar2_dict['morning'] = [date_list, sm_norm_list]
    sugar2_dict['evening'] = [date_list, se_norm_list]

    ##      average the morning and evening sugar together and then sample it
    sugar_avg_list = lp.two_list_avg(sm_norm_list, se_norm_list)
    sugar_dict['daily.avg'] = [range(0, len(sugar_avg_list)), sugar_avg_list]
    sugar_sample_list = lp.down_sample2(sugar_dict, 'daily.avg', sample_rate)
    sugar_dict['daily.avg.sample'] = sugar_sample_list

    ##      do some down_sampling of morning and evening in sugar2 dict
    sugar2_dict['morn.sample'] = lp.down_sample2(sugar2_dict, 'morning', sample_rate)
    sugar2_dict['even.sample'] = lp.down_sample2(sugar2_dict, 'evening', sample_rate)

    ##      find the deltas between when readings were taken
    morning_deltas_list = []
    evening_deltas_list = []
    for this_time in sugar_mTime_list:
        morning_deltas_list.append(lp.time_delta(this_time, '6.30')) ##reference time is six thirty in the morning
    for this_time in sugar_eTime_list:
        evening_deltas_list.append(lp.time_delta(this_time, '18.30')) ##reference time is six thirty in the evening
    sugarTime_dict['m_time'] = [date_list, morning_deltas_list]
    sugarTime_dict['e_time'] = [date_list, evening_deltas_list]

    ##      sample the delta between readings
    sugarTime_dict['m_time.sample'] = lp.down_sample2(sugarTime_dict, 'm_time', sample_rate)
    sugarTime_dict['e_time.sample'] = lp.down_sample2(sugarTime_dict, 'e_time', sample_rate)

    #sugar_dict['morning.sample'] = lp.down_sample2(sugar_dict, 'morning', 15)
    #sugar_dict['evening.sample'] = lp.down_sample2(sugar_dict, 'evening', 15)

    ##      clean up the dicts for things we're not going to graph
    del sugar_dict['daily.avg']
    #del sugar_dict['morning']
    #del sugar_dict['evening']
    del sugar2_dict['morning']
    del sugar2_dict['evening']


    bmi_list = []
    height = (6*12) + 2
    for this_weight in weight_list:
        bmi_list.append(lp.calc_bmi(height, this_weight))
    bmi_dict['bmi'] = [range(0, len(bmi_list)), bmi_list]
    bmi2_dict['bmi'] = [date_list, bmi_list]

    writeToJson(weight_dict, weight_path)
    writeToJson(pressure_dict, pressure_path)
    writeToJson(sugar_dict, sugar_path)
    writeToJson(bmi_dict, bmi_path)

    writeToJson(weight2_dict, weight2_path)
    writeToJson(pressure2_dict, pressure2_path)
    writeToJson(sugar2_dict, sugar2_path)
    writeToJson(sugarTime_dict, sugarTime_path)
    writeToJson(bmi2_dict, bmi2_path)

    return weight_dict, pressure_dict, sugar_dict


def writeToJson(thisDict, filepath):
    import json
    import os
    with open(filepath, 'w+') as fp:
        json.dump(thisDict, fp, indent=4, sort_keys=True)
    return os.path.exists(filepath)

if __name__ == '__main__':
    #extract_data('/home/james/scripts/statsChart/stats_test_data.txt')
    data_file = '/home/james/scripts/statsChart/data/blood_sugar_all.txt'
    if os.path.exists(data_file):
        extract_data(data_file, sample_rate=7)
    else:
        print('no data file found')



