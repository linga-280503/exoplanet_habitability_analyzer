from pymongo import MongoClient, ASCENDING
from typing import List, Dict

class DB:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]
        self.planets = self.db['planets']
        self.favs = self.db['favorites']
        self.notes = self.db['notes']
        self._ensure_indexes()

    def _ensure_indexes(self):
        self.planets.create_index([('name', ASCENDING)], unique=True)
        self.planets.create_index([('score', ASCENDING)])
        self.favs.create_index([('name', ASCENDING)], unique=True)

    def upsert_planets(self, docs: List[Dict]):
        for d in docs:
            self.planets.update_one({'name': d['name']}, {'$set': d}, upsert=True)

    def list_planets(self, query: Dict, limit:int=500):
        return list(self.planets.find(query).sort('score', -1).limit(limit))

    def get(self, name: str):
        return self.planets.find_one({'name': name})

    def favorite(self, name: str):
        self.favs.update_one({'name': name}, {'$set': {'name': name}}, upsert=True)

    def list_favorites(self):
        return [d['name'] for d in self.favs.find()]

    def add_note(self, name: str, text: str):
        self.notes.insert_one({'name': name, 'text': text})

    def list_notes(self, name: str):
        return [n['text'] for n in self.notes.find({'name': name}).sort('_id', -1)]
