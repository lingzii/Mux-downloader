from pymongo import MongoClient
from json import loads, dumps


def debug():
    with open('metadata.json') as f:
        return loads(f.read())['debugMode']


def printWar(head, content):
    print(f"\033[93m[{head}] {content}\033[96m")


def save(file, data):
    with open(file, 'w', encoding="utf-8") as f:
        i = dumps(data, ensure_ascii=False, indent=2)
        f.write(i.encode("utf8").decode())


class DB:
    def __init__(self, col):
        self.col = col

    def insert(self, url):
        self.col.insert_one({"url": url})

    def delete(self, url):
        self.col.delete_one({"url": url})

    def check(self, url):
        return self.col.find_one({"url": url}) != None


database = MongoClient('localhost', 27017)['mux-dl']
songDB = DB(database['include'])
artistDB = DB(database['artist'])
errorlog = DB(database['errorlog'])
