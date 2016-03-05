# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Name:        qq_api
# Purpose:
#
# Author:      Administrator
#
# Created:     01/01/2016
# Copyright:   (c) Administrator 2016
# Licence:     <your licence>
#-------------------------------------------------------------------------------
from web import database as web_database
import pymongo
from api_tool import Config

_CONF = {
    'db': {
        'dbn': 'mysql',
        'host': '192.168.71.130',
        'user': 'admin',
        'pw': 'admin',
        'db': 'QQinfo',
        'port':3306,
        'charset': 'utf8'
    },
    'mongodb': {
        'host': '192.168.71.130',
        'port': 27017
    },
}

config = Config(_CONF)
config.MYSQL_DB = web_database(**config.db)
config.MONGO_CONN = pymongo.MongoClient(**config.mongodb)

def main():
    print config

    config1 = Config()
    print config1
    print id(config)
    print id(config1)

if __name__ == '__main__':
    main()
