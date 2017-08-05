#!/usr/bin/python
##James Parks

##in here I'll put procedures to query the mongoDB and build appropriate
##pgPlot compatible json files out of that data

def fromMongo(collection, start_date, end_date):
    date_list = []
    weight_list = []
    pressure_h_list = []
    pressure_l_list = []
    sugar_m_time_list = []
    sugar_m_list = []
    sugar_e_time_list = []
    sugar_e_list = []

    cur = collection.find({})
    for doc in cur:
        for key in doc.keys():
            #populate my lists
