#-*- coding:utf8 -*-

import os
import sys
import torndb
import LOG
from Config import MYSQL

logger = LOG.Syslog.getLogger()
MySQLConnection = MYSQL.get('MySQLConnection')
class DB():
    
    """ 封装与操作常用的操作数据库，初始化数据库，相关工具等。 """
    def __init__(self):
        try:
            self.dbc = torndb.Connection(
                           host=MySQLConnection.get('Host') + ':' + str(MySQLConnection.get('Port', 3306)),
                           database=MySQLConnection.get('Database', None),
                           user=MySQLConnection.get('User', None),
                           password=MySQLConnection.get('Passwd', None),
                           connect_timeout=30,max_idle_time=60,
                           time_zone=MySQLConnection.get('Timezone','+8:00'),
                           charset=MySQLConnection.get('Charset', 'utf8'))
        except Exception, e:
            logger.error(e)
            sys.exit(126)

    def get(self, sql):
        try:
            data=self.dbc.get(sql)
        except Exception,e:
            logger.error(e)
            data=self.dbc.query(sql)
        return data

    def insert(self, sql):
        return self.dbc.execute(sql)

    def delete(self, sql):
        return self.dbc.execute(sql)

    def update(self, sql):
        return self.dbc.execute(sql)

if __name__ == "__main__":
    """
    s=''
    d={'cname':u'陶成伟','motto':'motto','email':'','extra':None}
    L=len(d)
    for k,v in d.iteritems():
        L-=1
        if not v:
            continue
        if L == 0:
            s+="%s='%s'" %(k,v)
        else:
            s+="%s='%s'," %(k,v)
    for k,v in d.iteritems():
        L-=1
        if L == 0:
            if v:
                s+="%s='%s'" %(k,v)
            break
        else:
            if v:
                s+="%s='%s'," %(k,v)
            else:
                continue
    if s[-1] == ',':
        t=s[0:len(s)-1]
    print type(t),t
    print type(s),s
    """
    sql="select username from user where username='tcw'"
    print DB().get(sql)
