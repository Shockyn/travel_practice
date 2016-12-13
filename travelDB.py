# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pandas as pd

from sqlalchemy import and_
from models import GeoInfos, Ratings, Types, Users
from connection import Session, connection

class travelDB(object):
    def __init__(self):
        pass

    def save_place(self, place_id, city, name, address, lng, lat):
        session = Session()

        if not self.get_place(place_id):
            geo = GeoInfos(place_id = place_id, name = name, city = city, address = address, lng = lng, lat = lat)
            session.add(geo)
            session.commit()
            print '<GEOINFO>', place_id, name, 'saved successfully!'

        session.close()

    def save_types(self, place_id, types):
        session = Session()

        if not self.get_types(place_id, types):
            type = Types(place_id = place_id, types = types)
            session.add(type)
            session.commit()
            print '<TYPE>', place_id, types, 'saved successfully!'

        session.close()

    def save_users(self, user_id, place_id):
        session = Session()

        if not self.get_users(user_id, place_id):
            user = Users(user_id = user_id, place_id = place_id)
            session.add(user)
            session.commit()
            print '<USER>', user_id, place_id, 'saved successfully.'

        session.close()

    def save_ratings(self, place_id, gg_reviews, gg_ratings, ta_reviews, ta_ratings):
        session = Session()

        if not self.get_ratings(place_id):
            rate = Ratings(place_id = place_id, gg_reviews = gg_reviews, gg_ratings = gg_ratings,
                           ta_reviews = ta_reviews, ta_ratings = ta_ratings)
            session.add(rate)
            session.commit()
            print '<RATING>', place_id, 'saved successfully!'

        session.close()

    def get_place(self, place_id):
        try:
            session = Session()
            row = session.query(GeoInfos).filter(GeoInfos.place_id == place_id).first()
            if row: print '<GEOINFO>', row, 'exists.'
            return row
        except Exception as e:
            print e
        finally:
            session.close()

    def get_place_name(self, place_id):
        try:
            session = Session()
            row = session.query(GeoInfos).filter(GeoInfos.place_id == place_id).first()
#           if row: print '<GEOINFO>', row, 'exists.'
            return row.name
        except Exception as e:
            print e
        finally:
            session.close()

    def get_types(self, place_id, type=''):
        try:
            session = Session()

            if not type:
                types = list()
                rows = session.query(Types).filter(Types.place_id == place_id).all()
                for row in rows: types.append(row.types)
#               if rows: print '<TYPE>', place_id, types
                types = list(set(types))
                return types
            else:
                row = session.query(Types).filter(and_(Types.place_id == place_id, Types.types == type)).first()
                if row: print '<TYPE>', row, 'exists.'
                return row
        except Exception as e:
            print e
        finally:
            session.close()

    def get_users(self, user_id, place_id=''):
        try:
            session = Session()

            if not place_id:
                places = list()
                rows = session.query(Users).filter(Users.user_id == user_id).all()
                for row in rows: places.append(row.place_id)
#               if rows: print '<USER>', user_id, places
                places = list(set(places))
                return places
            else:
                row = session.query(Users).filter(and_(Users.user_id == user_id, Users.place_id == place_id)).first()
                if row: print '<USER>', row, 'exists.'
                return row
        except Exception as e:
            print e
        finally:
            session.close()

    def get_ratings(self, place_id):
        try:
            session = Session()
            row = session.query(Ratings).filter(Ratings.place_id == place_id).first()
            if row: print '<RATING>', row, 'exists.'
            return row
        except Exception as e:
            print e
        finally:
            session.close()

    def get_geoinfo_db_fetch(self, city):
        result = connection.execute("SELECT * FROM travel.geoinfos WHERE travel.geoinfos.city = '{}'".format(city))
        df = pd.DataFrame(result.fetchall())
        df.columns = result.keys()

        return df.ix[:, ['PLACE_ID', 'NAME', 'LNG', 'LAT']]

    def get_user_db_fetch(self, user_id):
        result = connection.execute("SELECT * FROM travel.users WHERE travel.users.user_id = '{}'".format(user_id))
        df = pd.DataFrame(result.fetchall())
        df.columns = result.keys()

        return df

    def get_types_db_fetch(self, city):
        result = connection.execute("SELECT travel.geoinfos.place_id, name, types FROM travel.geoinfos " + \
                                    "INNER JOIN travel.types " + \
                                    "ON travel.geoinfos.place_id = travel.types.place_id " + \
                                    "WHERE travel.geoinfos.city = '{}'".format(city))
        df = pd.DataFrame(result.fetchall())
        df.columns = result.keys()

        df = df.groupby("place_id")['types'].apply(list)

        return pd.Series.to_frame(df)

    def get_ratings_db_fetch(self, city):
        result = connection.execute("SELECT travel.geoinfos.place_id, ta_reviews FROM travel.geoinfos " + \
                                    "INNER JOIN travel.ratings " + \
                                    "ON travel.geoinfos.place_id = travel.ratings.place_id " + \
                                    "WHERE travel.geoinfos.city = '{}'".format(city))
        df = pd.DataFrame(result.fetchall())
        df.columns = result.keys()

        return df
'''
city = 'moscow'
file_path = 'data/{}.xlsx'

travel_db = travelDB()

size = len(pd.read_excel(file_path.format(city)))
user_size = len(pd.read_excel(file_path.format('users')))

places_df = pd.read_excel(file_path.format(city)).ix[:, ['name', 'id', 'address', 'lng', 'lat']]
places_df = places_df.where((pd.notnull(places_df)), None)
ratings_df = pd.read_excel(file_path.format(city)).ix[:, ['id', 'gg_reviews', 'gg_ratings', 'ta_reviews', 'ta_ratings']]
ratings_df = ratings_df.where((pd.notnull(ratings_df)), 0)
types_df = pd.read_excel(file_path.format(city)).ix[:, ['id', 'types']]
users_df = pd.read_excel(file_path.format('users'))


for n in xrange(size):

    travel_db.save_place(places_df.ix[n, 'id'], city, places_df.ix[n, 'name'], places_df.ix[n, 'address'],
                         places_df.ix[n, 'lng'], places_df.ix[n, 'lat'])

    travel_db.save_ratings(ratings_df.ix[n, 'id'], ratings_df.ix[n, 'gg_reviews'], ratings_df.ix[n, 'gg_ratings'],
                           ratings_df.ix[n, 'ta_reviews'], ratings_df.ix[n, 'ta_ratings'])

    for type in types_df.ix[n, 'types'].replace(' ', '').split(','):
        travel_db.save_types(types_df.ix[n, 'id'], type)


for n in xrange(user_size):
    for place_id in users_df.ix[n, 'place_id'].replace(' ', '').split(','):
        travel_db.save_users(users_df.ix[n, 'user_id'], place_id)
'''