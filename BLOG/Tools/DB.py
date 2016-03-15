#!/usr/bin/python -O
#-*- coding:utf8 -*-

import os
import sys
import config
import torndb
import LOG

logger = LOG.Syslog.getLogger()

class DB():
    
    """ 封装与操作常用的操作数据库，初始化数据库，相关工具等。 """
    def __init__(self):
        try:
            self.dbc = torndb.Connection(
                           host=config.MySQLConnection.get('Host', '127.0.0.1') + ':' + str(config.MySQLConnection.get('Port', 3306)),
                           database=config.MySQLConnection.get('Database', None),
                           user=config.MySQLConnection.get('User', None),
                           password=config.MySQLConnection.get('Passwd', None),
                           connect_timeout=30,max_idle_time=60,
                           time_zone=config.MySQLConnection.get('Timezone','+8:00'),
                           charset=config.MySQLConnection.get('Charset', 'utf8'))
        except Exception, e:
            logger.error(e)
            sys.exit(126)

    def get(self, sql):
        return self.dbc.get(sql)

    def insert(self, sql):
        return self.dbc.execute(sql)

    def delete(self, sql):
        return self.dbc.execute(sql)

if __name__ == "__main__":
    pass
