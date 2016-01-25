# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 22:50:37 2016

@author: kenren
"""

#!/usr/bin/env python
"""
This code gets the number of unique users in MongoDB
"""

def get_db(db_name):
    from pymongo import MongoClient
    client = MongoClient('localhost:27017')
    db = client[db_name]
    return db

def make_pipeline():
    # complete the aggregation pipeline
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
    pprint.pprint(result)
    
