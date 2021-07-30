from PIL.Image import NONE
from pymongo import MongoClient

database = MongoClient('localhost', 27017)
songDB = database['mux-dl']['include']


class dedup:
    def __init__(self, tags, config) -> None:
        self.data = {'url': tags['url']}
        self.debug = config['debug']

    def exist(self) -> bool:
        if self.debug:
            return songDB.find_one(self.data)
        else:
            return False

    def insert(self) -> None:
        if self.debug:
            songDB.insert_one(self.data)
