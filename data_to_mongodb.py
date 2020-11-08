import pymongo
from pymongo.collection import Collection

class ConnectMongodb(object):
    def __init__(self):
        self.clent = pymongo.MongoClient(host='127.0.0.1',port=27017)
        self.db_name = self.clent['dou_guo_food']  #databases name

    def insert_item(self,item):
        db_collection = Collection(self.db_name,'douguo_table')
        db_collection.insert(item)


mongo_info = ConnectMongodb()