#!/usr/bin/python

##EXAMPLE USAGE:
## $ python stats_extract.py
##      this will create a number of .json files
## $ ./xyPlot.py -g line -l --wi 11 --he 4 -t 'Weight' -f ../statsChart/weight_20170701.json 
## $ ./xyPlot.py -g line -l --wi 11 --he 4 -t 'Blood Pressure' -f ../statsChart/pressure_20170701.json 
## $ ./xyPlot.py -g line -l --wi 11 --he 4 -t 'Blood Sugar' -f ../statsChart/sugar_20170701.json 


import json
import os
import re
import datetime

test_date = '06-26-17'
test_weight = '(180.2)'
test_pressure = '118-62'
test_sugar = '17.17.     122'

def extract_data(this_file):
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
    bmi_dict = {}
    bmi2_dict = {}

    date_list = []
    weight_list = []
    pressure_h_list = []
    pressure_l_list = []
    sugar_morning_list = []
    sugar_evening_list = []

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
                #sugar_morning_dict[date] = val
                sugar_morning_list.append(int(val))
                morning_val = val
            if len(time) >=5:
                #sugar_evening_dict[date] = val
                sugar_evening_list.append(int(val))
                evening_val = val
            #if morning_val != 0 and evening_val != 0:
            #    sugar2_dict[date] = [morning_val, evening_val]

        #print('Date: {0}, Weight: {1}, Pressure: {2}, Sugar: {3}'.format(date, weight, pressure, '{0},{1}'.format(time,val)))

    today = datetime.date.today()
    fmt_today = '{:%Y%m%d}'.format(today)
    weight_path = 'weight_{0}.json'.format(fmt_today)
    weight2_path = 'weight2_{0}.json'.format(fmt_today)
    pressure_path = 'pressure_{0}.json'.format(fmt_today)
    pressure2_path = 'pressure2_{0}.json'.format(fmt_today)
    sugar_path = 'sugar_{0}.json'.format(fmt_today)
    sugar2_path = 'sugar2_{0}.json'.format(fmt_today)
    bmi_path = 'bmi_{0}.json'.format(fmt_today)
    bmi2_path = 'bmi2_{0}.json'.format(fmt_today)

    json_dict = {}
    weight_dict['weight'] = [range(0,len(weight_list)), weight_list]
    weight_dict['weight.sample'] = down_sample2(weight_dict, 'weight', 5)
    weight2_dict['weight'] = [date_list, weight_list]

    ph_norm_list, pl_norm_list = normalize_two_lists(pressure_h_list, pressure_l_list)
    pressure_dict['high'] = [range(0, len(pressure_h_list)), ph_norm_list]
    pressure_dict['low'] = [range(0, len(pressure_l_list)), pl_norm_list]
    pressure2_dict['high'] = [date_list, ph_norm_list]
    pressure2_dict['low'] = [date_list, pl_norm_list]


    sm_norm_list, se_norm_list = normalize_two_lists(sugar_morning_list, sugar_evening_list)
    sugar_dict['morning'] = [range(0, len(sm_norm_list)), sm_norm_list]
    sugar_dict['evening'] = [range(0, len(se_norm_list)), se_norm_list]
    sugar2_dict['morning'] = [date_list, sm_norm_list]
    sugar2_dict['evening'] = [date_list, se_norm_list]

    sugar_dict['morning.sample'] = down_sample2(sugar_dict, 'morning', 15)
    sugar_dict['evening.sample'] = down_sample2(sugar_dict, 'evening', 15)
 
    sugar_avg_list = two_list_avg(sm_norm_list, se_norm_list)
    sugar_dict['daily.avg'] = [range(0, len(sugar_avg_list)), sugar_avg_list]
    
    #sugar_rolling_avg_list = one_list_rolling_avg(sugar_avg_list)
    #sugar_dict['rolling.avg'] = [range(0, len(sugar_rolling_avg_list)), sugar_rolling_avg_list]

    sugar_sample_list = down_sample2(sugar_dict, 'daily.avg', 15)
    sugar_dict['daily.avg.sample'] = sugar_sample_list

    del sugar_dict['daily.avg']
    del sugar_dict['morning']
    del sugar_dict['evening']

    #pressure_h_avg_list = one_list_rolling_avg(pressure_h_list)
    #pressure_l_avg_list = one_list_rolling_avg(pressure_l_list)
    pressure_h_sample_list = down_sample2(pressure_dict, 'high', 5)
    pressure_l_sample_list = down_sample2(pressure_dict, 'low', 5)

    #pressure_dict['high rolling avg'] = [range(0, len(pressure_h_avg_list)), pressure_h_avg_list]
    #pressure_dict['low rolling avg'] = [range(0, len(pressure_l_avg_list)), pressure_l_avg_list]
    pressure_dict['high.sample'] = pressure_h_sample_list
    pressure_dict['low.sample'] = pressure_l_sample_list

    #weight_avg_list = one_list_rolling_avg(weight_list)
    #weight_dict['rolling avg'] = [range(0, len(weight_avg_list)), weight_avg_list]

    bmi_list = []
    height = (6*12) + 2
    for this_weight in weight_list:
        bmi_list.append(calc_bmi(height, this_weight))
    bmi_dict['bmi'] = [range(0, len(bmi_list)), bmi_list]
    bmi2_dict['bmi'] = [date_list, bmi_list]

    writeToJson(weight_dict, weight_path)
    writeToJson(pressure_dict, pressure_path)
    writeToJson(sugar_dict, sugar_path)
    writeToJson(bmi_dict, bmi_path)

    writeToJson(weight2_dict, weight2_path)
    writeToJson(pressure2_dict, pressure2_path)
    writeToJson(sugar2_dict, sugar2_path)
    writeToJson(bmi2_dict, bmi2_path)

    return weight_dict, pressure_dict, sugar_dict

def calc_bmi(height, weight):
    return (float(weight) * 703.0) / (float(height)**2)

def numpy_polyfit(xes, yes, pts):
    import numpy as np
    x = np.array(xes)
    y = np.array(yes)
    scale = len(x) / 30
    p = np.polyfit(x, y, pts)
    ox = range(1, len(x)-scale, scale)
    oy = list(p)

    #print('ox: {0}'.format(len(ox)))
    #print('oy: {0}'.format(len(oy)))
    return ox, oy

def two_list_avg(first_list, second_list):
    avg_list = []
    f = len(first_list)
    s = len(second_list)
    if f > s:
        diff = f - s
        #print('f > s: {0}'.format(diff))
        for x in range(1, diff):
            p = s + x
            #print p
            second_list.append(first_list[p])
            #print('appending {0} to position {1}'.format(first_list[p-1], p))
    elif f < s:
        diff = s - f
        #print('s > f: {0}'.format(diff))
        for x in range(1, diff+1):
            p = f + x
            #print p
            first_list.append(second_list[p - 1])
            #print('appending {0} to position {1}'.format(second_list[p-1], p))

    f = len(first_list)
    s = len(second_list)
    if f == s:
        for x in range(0, len(first_list)):
            myAvg = (float(first_list[x]) + float(second_list[x])) / float(2)
            #print('avg: {0}'.format(myAvg))
            avg_list.append(myAvg)

    return avg_list

def normalize_two_lists(first_list, second_list):
    f = len(first_list)
    s = len(second_list)
    if f > s:
        #print('first list is longer')
        diff = f - s
        #print('diff = {0}'.format(diff))
        for x in range(0, diff):
            #print('x: {0}'.format(x))
            p = s + x
            #print('p: {0}'.format(p))
            #print('appending: {0}'.format(first_list[p]))
            second_list.append(first_list[p])
    elif f < s:
        #print('second list is longer')
        diff = s - f
        #print('diff = {0}'.format(diff))
        for x in range(0, diff):
            print('x: {0}'.format(x))
            p = f + x
            #print('p: {0}'.format(p))
            #print('appending: {0}'.format(second_list[p]))
            first_list.append(second_list[p])
    f = len(first_list)
    s = len(second_list)
    if f == s:
        print('successful normalization')
    return first_list, second_list

def one_list_rolling_avg(this_list):
    avg_list = []
    l = len(this_list)
    rolling = 0
    y = 1 
    total = 0
    for x in range(0,l):
        total = total + float(this_list[x])
        this_avg = float(total) / float(y)
        #this_avg = float(this_list[x]) + float(rolling) / float(2)
        y+=1
        #rolling = this_avg
        avg_list.append(this_avg)
    return avg_list

def two_list_rolling_avg(first_list, second_list):
    avg_list = []
    f = len(first_list)
    s = len(second_list)
    #print('f: {0}'.format(f))
    #print('s: {0}'.format(s))
    if f > s:
        diff = f - s
        #print('d: {0}'.format(diff))
        for x in range(1, diff+1):
            p = s + x
            #print('p: {0}'.format(p))
            second_list.append(first_list[p-1])
    elif f < s:
        diff = s - f
        #print('d: {0}'.format(diff))
        for x in range(1, diff+1):
            p = f + x
            #print('p: {0}'.format(p))
            first_list.append(second_list[p-1])
    f = len(first_list)
    s = len(second_list)
    #print('f: {0}'.format(f))
    #print('s: {0}'.format(s))
    if f == s:
        rolling = 0
        for x in range(0, f):
            thisAvg = (float(first_list[x]) + float(second_list[x]) + float(rolling)) / float(3)
            #print('avg: {0}'.format(thisAvg))
            avg_list.append(thisAvg)
    return avg_list

def writeToJson(thisDict, filepath):
    import json
    import os
    with open(filepath, 'w+') as fp:
        json.dump(thisDict, fp, indent=4, sort_keys=True)
    return os.path.exists(filepath)

def down_sample(this_dict, key, target_samples):
    import math
    #print('len x_values: {0}'.format(len(this_dict[key][0])))
    divisions = math.ceil((len(this_dict[key][1])) / float(target_samples))
    if int(divisions) == 0:
        divisions = 1.0
    #print('divisions: {0}'.format(divisions))
    x_samples = range(this_dict[key][0][0], this_dict[key][0][-1], int(divisions))
    x_samples.append(this_dict[key][0][-1])
    #print('len x_samples: {0}'.format(len(x_samples)))
    y_samples = []
    i = 0
    for this_val in range(1,len(this_dict[key][1])):
        if (i % int(divisions)) == 0:
            y_samples.append(this_dict[key][1][this_val])
        i+=1
    y_samples.append(this_dict[key][1][-1])
    #print('len y_samples: {0}'.format(len(y_samples)))
    sample_dict = {(key + ".sample"): [x_samples, y_samples]}
    return [x_samples, y_samples]
    #return sample_dict

def down_sample2(this_dict, key, incr):
    import math
    print('len x_values: {0}'.format(len(this_dict[key][0])))
    print('len y_values: {0}'.format(len(this_dict[key][-1])))
    i = 0
    accumulator = 0.0
    x_samples = []
    y_samples = []
    first_value = True
    last_value = False
    for this_y in this_dict[key][-1]:
        if first_value:
            x_samples.append(this_dict[key][0][0])
            y_samples.append(this_dict[key][1][0])
            first_value = False
        elif i % incr == 0:
            #print('accumulate: {0}'.format(this_y))
            accumulator += this_y
            print('\navg: {0}'.format(accumulator / float(incr)))
            x_samples.append(i)
            y_samples.append(accumulator / float(incr))
            print('new sample: x:{0} y:{1}\n\n'.format(i, accumulator / float(incr)))
            accumulator = 0
            last_value = False
        else:
            #print('accumulate: {0}'.format(this_y))
            accumulator += this_y
            last_value = True
        i += 1
        print('orig data: x:{0} y:{1}'.format(i, this_y))
    if last_value:
        x_samples.append(this_dict[key][0][-1])
        y_samples.append(this_dict[key][-1][-1])

    print('len of x_samples: {0}'.format(len(x_samples)))
    print('len of y_samples: {0}'.format(len(y_samples)))
    return [x_samples, y_samples]

if __name__ == '__main__':
    #extract_data('/home/james/scripts/statsChart/stats_test_data.txt')
    data_file = '/home/james/scripts/statsChart/data/blood_sugar_all.txt'
    if os.path.exists(data_file):
        extract_data(data_file)
    else:
        print('no data file found')



