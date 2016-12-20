# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pandas as pd
import math as m
import numpy as np
import pprint
import time
from collections import Counter

from travelDB import travelDB

class similarDB(object):
    def __init__(self, travelDB, user_id, city, days):
        start_time = time.time()
        print("Starting initializing...")

        self.travel_db = travelDB()
        self.user_id = user_id
        self.city = city
        self.days = days


        self.geoinfo_df = self.travel_db.get_geoinfo_db_fetch(city)
        self.geoinfo_df.columns = ['place_id', 'name', 'lng', 'lat']
        self.geoinfo_df = self.geoinfo_df.set_index('place_id')

        self.user_df = self.travel_db.get_user_db_fetch(user_id)
        self.user_df.columns = ['index', 'user_id', 'place_id']
        self.user_df = self.user_df.set_index('index')

        self.types_df = self.travel_db.get_types_db_fetch(city)

        self.ratings_df = self.travel_db.get_ratings_db_fetch(city)
        self.ratings_df.columns = ['place_id', 'reviews']

        self.node_df = pd.DataFrame(columns=['place_id', 'node', 'distance'])
        self.node_geo_df = 0
        self.node_list = list()

        print('Initializing has been done! %s sec' % (time.time() - start_time))

    def get_user_pref(self):
        start_time = time.time()
        print('Calculating user preference...')
        user_type = self.travel_db.get_user_type(self.user_id)

        user_prefer = pd.DataFrame(dict(Counter(user_type)).items(), columns=['type', 'weight'])

        print('Calculating user preference has been done! %s sec' % (time.time() - start_time))

        return pd.DataFrame(np.hstack((np.array(user_prefer.type).reshape(len(user_prefer.type), 1),
                                       np.array(user_prefer.weight/max(user_prefer.weight)).reshape(len(user_prefer.weight), 1))),
                            columns=['type', 'weight']).sort_values(by='weight', ascending=False)

    def get_place_score(self):
        start_time = time.time()
        user_pref_df = self.get_user_pref().set_index('type')
        place_scores = dict()

        print('Calculating place scores...')

        for place in self.types_df.index.tolist():
            place_score = 0
            types = self.types_df.ix[place, 'types']

            for type in types:
                if type in user_pref_df.index.tolist():
                    place_score += user_pref_df.ix[type, 'weight']

#           place_scores[self.geoinfo_df.ix[place, 'name']] = place_score
            place_scores[place] = place_score

        place_score_df = pd.merge(pd.DataFrame(place_scores.items(), columns=['place_id', 'weight']),
                                  self.ratings_df, on='place_id', how='outer').sort_values(['weight', 'reviews'], ascending=[False, False])

        print('Calculating place scores has been done! %s sec' % (time.time() - start_time))
        return place_score_df

    def deg2rad(self, deg):
        return deg * m.pi / 180

    def rad2deg(self, rad):
        return rad * 180 / m.pi

    def cal_distance(self, place1, place2, df=0):
        lng1, lat1 = tuple((self.geoinfo_df.ix[place1, 'lng'], self.geoinfo_df.ix[place1, 'lat']))
        lng2, lat2 = tuple((self.geoinfo_df.ix[place2, 'lng'], self.geoinfo_df.ix[place2, 'lat']))

        theta = float(lng1) - float(lng2)
        dist = m.sin(self.deg2rad(lat1)) * m.sin(self.deg2rad(lat2)) + \
               m.cos(self.deg2rad(lat1)) * m.cos(self.deg2rad(lat2)) * m.cos(self.deg2rad(theta))

        dist = m.acos(dist)
        dist = self.rad2deg(dist)

        dist = dist * 60 * 1.1515
        dist = dist * 1.609344
        dist = dist * 1000.0

        return dist

    def cal_distance_by_degree(self, lng1, lat1, lng2, lat2):
        theta = float(lng1) - float(lng2)
        dist = m.sin(self.deg2rad(lat1)) * m.sin(self.deg2rad(lat2)) + \
               m.cos(self.deg2rad(lat1)) * m.cos(self.deg2rad(lat2)) * m.cos(self.deg2rad(theta))

        dist = m.acos(dist)
        dist = self.rad2deg(dist)

        dist = dist * 60 * 1.1515
        dist = dist * 1.609344
        dist = dist * 1000.0

        return dist

    def making_node(self):
        start_time = time.time()
        user_pref_df = self.get_place_score().set_index('place_id')

        self.node_df.place_id = user_pref_df.index

        radar = 1000

        print('Making node...')
        for n, place1 in self.node_df.iterrows():
            for i, place2 in self.node_df.iterrows():
                if n >= i:
                    if m.isnan(self.node_df.ix[i, 'node']): self.node_df.ix[i, 'node'] = n
                    continue

                if radar > self.cal_distance(place1.place_id, place2.place_id):
                    if m.isnan(self.node_df.ix[i, 'node']):
                        self.node_df.ix[i, 'node'] = n
                        self.node_df.ix[i, 'distance'] = self.cal_distance(place1.place_id, place2.place_id)
                    elif self.node_df.ix[i, 'distance'] > self.cal_distance(place1.place_id, place2.place_id):
                        self.node_df.ix[i, 'node'] = n
                        self.node_df.ix[i, 'distance'] = self.cal_distance(place1.place_id, place2.place_id)

        self.node_df = pd.merge(self.node_df, self.geoinfo_df.reset_index(), on='place_id', how='outer').fillna(0)
        self.node_df = self.node_df.sort_values(['node', 'distance'], ascending=[True, True])

        self.node_geo_df = self.node_df.groupby('node')['place_id'].apply(list).reset_index()
        self.node_geo_df['lat'] = 0
        self.node_geo_df['lng'] = 0

        for n, row in self.node_geo_df.iterrows():
            self.node_geo_df.ix[n, 'lng'], self.node_geo_df.ix[n, 'lat'] = self.cal_center(row.place_id)

        self.node_list = self.node_geo_df['node'].tolist()

        print('Making node has been done! %s sec' % (time.time() - start_time))

#       return self.node_df.copy()
#       return self.node_df.ix[:, ['name', 'place_id', 'node', 'distance']].sort_values(['node', 'distance'], ascending=[True, True])
        return self.node_geo_df

    def making_schedule(self):
        start_time = time.time()

        self.making_node()
        total_schedule = dict()
        result_df = pd.DataFrame(columns=list(self.node_df.columns).extend('day'))

        for day in xrange(self.days):
            temp_df = pd.DataFrame(columns=list(self.node_df.columns).extend('day'))
            total_distance = 0

            result_list = [self.node_list[0]]
            self.node_list.pop(0)

            for node in result_list:
                temp_df = temp_df.append(self.node_df[self.node_df['node'] == node])
                total_distance += temp_df[temp_df['node'] == node]['distance'].sum()

                if len(temp_df) > 8: continue
                if total_distance < 10000:
                    next_node, distance = self.find_near_node(node)
                    result_list.append(next_node)
                    self.node_list.remove(next_node)
                    total_distance += distance

            temp_df['day'] = day
            total_schedule.update(temp_df.groupby('day')['name'].apply(list).to_dict())
            result_df = result_df.append(temp_df)

#       pprint.pprint(total_schedule, width=1)

#       result_df = result_df[['day', 'node', 'name', 'place_id', 'lat', 'lng']]

#       writer = pd.ExcelWriter('{}_{}.xlsx'.format(self.city, self.user_id))
#       result_df.to_excel(writer)
#       writer.save()

        print('Making Schedule has been done! %s sec' % (time.time() - start_time))
        return total_schedule

    def find_near_node(self, node):
        temp_node_df = self.node_geo_df.set_index('node').ix[self.node_list, :]
        temp_node_df['distance'] = 0
        lng1 = self.node_geo_df[self.node_geo_df['node'] == node]['lng']
        lat1 = self.node_geo_df[self.node_geo_df['node'] == node]['lat']

        for n, row in temp_node_df.iterrows():
            lng2 = row.lng
            lat2 = row.lat
            temp_node_df.ix[n, 'distance'] = self.cal_distance_by_degree(lng1, lat1, lng2, lat2)

        return temp_node_df['distance'].idxmin(), temp_node_df.ix[temp_node_df['distance'].idxmin()]['distance']

    def cal_center(self, place_list):
        lat = list()
        lng = list()

        for place in place_list:
            lat.append(self.geoinfo_df.ix[place, 'lat'])
            lng.append(self.geoinfo_df.ix[place, 'lng'])

        return tuple((min(lng) + (max(lng) - min(lng)) / 2, min(lat) + (max(lat) - min(lat)) / 2))
'''
city = 'moscow'
user_id = 1
days = 3
travel_db = travelDB()

similar_db = similarDB(travelDB, user_id, city, days)
pprint.pprint(similar_db.making_schedule(), width=1)
'''