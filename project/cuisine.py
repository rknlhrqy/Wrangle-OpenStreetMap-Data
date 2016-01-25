# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 22:50:37 2016

@author: kenren
"""

#!/usr/bin/env python
"""
This code gets the number of unique users in MongoDB
"""
#%pylab inline
import matplotlib.pyplot as plt
import seaborn as sns
import pprint

def draw_bar_plot_with_x_string(bar_y, bar_x, bar_x_string, x_label, y_label, sub_title):
    bar_width = 0.4
    plt.bar(bar_x, bar_y, bar_width, color='b', align='center')
    plt.xticks(bar_x, bar_x_string)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.suptitle(sub_title)

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def make_pipeline():
    # complete the aggregation pipeline
    pipeline = [ ]
    pipeline.append({'$match':{'cuisine':{'$exists':1}}})
    pipeline.append({'$group':{'_id': '$cuisine', 'count' :{'$sum':1}}})
    pipeline.append({'$sort':{'count':-1}})
    pipeline.append({'$limit': 25})
    return pipeline

def aggregate(db, pipeline):
    return [doc for doc in db.sj.aggregate(pipeline)]


if __name__ == '__main__':
    db = get_db('project')
    pipeline = make_pipeline()
    result = aggregate(db, pipeline)
    pprint.pprint(result)
    
    bar_y = []
    bar_x = []
    bar_x_string = []
    i = 0
    for each in result:
        bar_y.append(each['count'])
        i = i + 1
        bar_x.append(i)
        bar_x_string.append(each['_id'])
        
    xlabel = 'Different Cuisine'
    ylabel = 'Number of Business'
    suptitle = 'Number of Business for Different Cuisine'

#    draw_bar_plot_with_x_string(bar_y, bar_x, bar_x_string, xlabel, ylabel, suptitle)
    draw_bar_plot_with_x_string(bar_y, bar_x, bar_x, xlabel, ylabel, suptitle)
    
    for index, value in zip(bar_x, bar_x_string):
        print index, "=", value
