import codecs
import json
import os

import yaml
from pymongo import MongoClient

from configs import settings
from patterns import Singleton


class Specifications(object, metaclass=Singleton):
    def __init__(self):
        self.extractor_file_path = os.path.normpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'configs/ebay/extractor/extractor.yaml')
        )
        try:
            with open(self.extractor_file_path, 'r') as stream:
                self.data = yaml.load(stream)
            self.field_keys = self.data.keys()
        except Exception as e:
            print(f'An Error loading specification file. Details: {e}')
            self.field_keys = tuple()
            self.data = dict()


class GoodMeta(type):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
        new_class._specifications = Specifications()
        client = MongoClient(
            host=settings.MONGO_DB_HOST,
            port=settings.MONGO_DB_PORT,
            connect=False
        )
        new_class._mongo_db = client.ebay_scraping
        return new_class


class Good(object, metaclass=GoodMeta):
    dfp_prefix = 'goods_data'  # dump file plural prefix
    df_prefix = 'good_%s_data'  # dump file prefix
    dumper = {
        'yaml': lambda data, file: yaml.dump(data, file, default_flow_style=False),
        'json': lambda data, file: json.dump(data, file)
    }

    def __init__(self, result_directory):
        self.result_directory = result_directory
        self._id = None
        self.title = None

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    def serialize(self):
        data = {k: getattr(self, k, None) for k in self._specifications.field_keys}
        data.update({'id': self.id, 'title': self.title})
        return data

    def to_mongo_db(self):
        collection = self._mongo_db.goods
        data = self.serialize()
        if self.id and collection.find_one({'id': self.id}):
            collection.update_one({'id': self.id}, {"$set": data})
        else:
            collection.insert_one(data)

    def save_to_file(self, file_format=None):
        if file_format and file_format in self.dumper:
            file_path = f'{self.result_directory}/{self.df_prefix}.{file_format}' % self.id
            with open(file_path, 'w') as outfile:
                self.dumper.get(file_format, self.dumper['json'])(self.serialize(), outfile)

    @classmethod
    def save_goods_batch_to_file(cls, goods, to_one_file=True, result_directory=None, file_format=None):
        if file_format and file_format in cls.dumper:
            if to_one_file:
                file_path = f'{result_directory or ""}/{cls.dfp_prefix}.{file_format}'
                data = [good.serialize() for good in goods]
                with open(file_path, 'w') as outfile:
                    cls.dumper.get(file_format, cls.dumper['json'])(data, outfile)
            else:
                for good in goods:
                    result_directory = result_directory or good.result_directory
                    file_path = f'{result_directory or ""}/{cls.df_prefix}.{file_format}' % good.id
                    with open(file_path, 'w') as outfile:
                        cls.dumper.get(file_format, cls.dumper['json'])(good.serialize(), outfile)


def mongo_collection_to_file(file_format='json'):
    client = MongoClient(
        host=settings.MONGO_DB_HOST,
        port=settings.MONGO_DB_PORT,
        connect=False
    )
    db = client.ebay_scraping
    collection = db.goods
    cursor = collection.find({})
    with codecs.open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  f"collection.{file_format}"), "w", encoding='utf-8') as file:
        if file_format == 'json':
            file.write('[')
            for document in cursor:
                document.pop('_id')
                file.write(json.dumps(document, indent=4, ensure_ascii=False))
                file.write(',')
            file.write(']')
        elif file_format == 'txt':
            for document in cursor:
                document.pop('_id')
                document.pop('id')
                title = document.get('title', 'Unknown')
                try:
                    document['title'] = (''.join(title.split('Details about')[1:])).lstrip().rstrip()
                except AttributeError:
                    document['title'] = title or 'Unknown'
                file.write(';'.join([x.replace('\n', '').strip() if x else 'Unknown' for x in document.values()]))
                file.write('\n')
