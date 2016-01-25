# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 22:50:37 2016

@author: kenren
"""

#!/usr/bin/env python
"""
This code is doing the following:
1, find the top 10 users from San Jose map data in MongoDB
2, draw the map of San Jose using Stereographic Projection
3, for each of the top 10 users, extract the locations (latitude, longitude)
   this user added into the San Jose map data
4, draw the locations as a dot in the map.
"""
from pymongo import MongoClient
import pprint
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import numpy as np

    
def get_db(db_name):
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def make_pipeline():
    # complete the aggregation pipeline
    # get the top 10 user.
    pipeline = [ ]
    pipeline.append({'$group':{'_id': '$created.user', 'count' :{'$sum':1}}})
    pipeline.append({'$sort':{'count':-1}})
    pipeline.append({'$limit': 10})

    return pipeline

def aggregate(db, pipeline):
    return [doc for doc in db.sj.aggregate(pipeline)]


if __name__ == '__main__':
    db = get_db('project')
    pipeline = make_pipeline()
    result = aggregate(db, pipeline)
    #pprint.pprint(result)

    # create figure and axes instances
    fig = plt.figure(figsize=(16,16))
    ax = fig.add_axes([0.1,0.1,0.9,0.9])
    
    # llcrnrlat,llcrnrlon,urcrnrlat,urcrnrlon
    # are the lat/lon values of the lower left and upper right corners
    # of the map.
    # resolution = 'i' means use intermediate resolution coastlines.
    # lon_0, lat_0 are the central longitude and latitude of the projection.
    m = Basemap(llcrnrlon=-122.2332,llcrnrlat=37.0793,urcrnrlon=-121.4010,urcrnrlat=37.5141, \
                rsphere=6371200.,resolution='h',projection='stere',lon_0=-122,lat_0=37.25, anchor='C')
    
    # can get the identical map this way (by specifying width and
    # height instead of lat/lon corners)
    m.drawcoastlines()
    m.drawcounties(linewidth=1)
    m.fillcontinents(color='coral',lake_color='aqua')
    # draw parallels and meridians.
    m.drawmeridians(np.arange(-122,-120.,0.25), dashes=[3,3], color='b', labels=[0,0,0,1], ax=ax)
    m.drawparallels(np.arange(37.,38.,0.25), dashes=[3,3], color='b', labels=[1,0,0,0], ax=ax)
    m.drawmapboundary(fill_color='aqua')
    
    # Pick up one user from the top 10 users.
    user = result[4]['_id']
    print user

    # Extract all the locations this user added.
    user_data = db.sj.find({'created.user':user})
    pos_x  = []
    pos_y = []
    i = 0
    for each in user_data:
        if 'pos' in each:
            i = i+ 1
            pos_x.append(each['pos'][1])
            pos_y.append(each['pos'][0])
    print i
    # Draw all the location as dots on the map.            
    m.scatter(pos_x, pos_y, latlon=True, zorder=10, s=5, marker='o', color='b', alpha=1)        
    
    plt.title("San Jose, California")
    plt.show()
    
    
        
    
