from pymongo import MongoClient

database = MongoClient('localhost', 27017)
songDB = database['mux-dl']['include']


class dedup:
    def __init__(self, tags) -> None:
        self.data = {'url': tags['url']}

    def exist(self):
        return songDB.find_one(self.data)

    def insert(self):
        songDB.insert_one(self.data)
