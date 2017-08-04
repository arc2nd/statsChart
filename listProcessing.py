#!/usr/bin/python
##James Parks
import json
import os
import re
import datetime

#rec_time = recorded time
#ref_time = reference time (how far away from ref time is rec time.
def time_delta(rec_time, ref_time):
    FMT = '%H.%M'
    rec_t = datetime.datetime.strptime(rec_time, FMT)
    ref_t = datetime.datetime.strptime(ref_time, FMT)
    if rec_time < ref_time:
        tdelta = ref_t - rec_t
        return -(tdelta.seconds / 60.0)
    else: #ref_time < rec_time:
        tdelta =rec_t - ref_t
        return tdelta.seconds / 60.0

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
    print(key)
    print('len x_values: {0}'.format(len(this_dict[key][0])))
    print('len y_values: {0}'.format(len(this_dict[key][-1])))
    if len(this_dict[key][0]) != len(this_dict[key][-1]):
        calc_start = len(this_dict[key][0]) - len(this_dict[key][-1])
        this_dict[key][0] = this_dict[key][0][calc_start:]
        print(this_dict[key][0])
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
            #print('\navg: {0}'.format(accumulator / float(incr)))
            x_samples.append(this_dict[key][0][i])
            y_samples.append(accumulator / float(incr))
            #print('new sample: x:{0} y:{1}\n\n'.format(i, accumulator / float(incr)))
            accumulator = 0
            last_value = False
        else:
            #print('accumulate: {0}'.format(this_y))
            accumulator += this_y
            last_value = True
        i += 1
        #print('orig data: x:{0} y:{1}'.format(i, this_y))
    if last_value:
        x_samples.append(this_dict[key][0][-1])
        y_samples.append(this_dict[key][-1][-1])

    #print('len of x_samples: {0}'.format(len(x_samples)))
    #print('len of y_samples: {0}'.format(len(y_samples)))
    return [x_samples, y_samples]

