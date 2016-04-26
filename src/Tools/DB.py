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
            logger.warn(e)
            data=self.dbc.query(sql)
        return data

    def insert(self, sql):
        return self.dbc.insert(sql)

    def delete(self, sql):
        return self.dbc.execute(sql)

    def update(self, sql):
        return self.dbc.update(sql)

    def execute(self, sql):
        return self.dbc.execute(sql)

if __name__ == "__main__":
    s= r"""<h1>mysql的Data truncation: Data too long for column &#39;path&#39; at row 1怎么解决?</h1>

<p><ins>&nbsp;<em>分享</em>|&nbsp;</ins>2014-05-24 11:20<a href="http://www.baidu.com/p/datong370?from=zhidao" target="_blank">datong370</a>&nbsp;|&nbsp;浏览 6120 次</p>

<p>&nbsp;<a href="http://zhidao.baidu.com/list?tag=%CA%FD%BE%DD%BF%E2" target="_blank">数据库</a></p>

<p><a href="http://d.hiphotos.baidu.com/zhidao/pic/item/37d12f2eb9389b50745692a58735e5dde6116e9f.jpg" target="_blank"><img src="http://d.hiphotos.baidu.com/zhidao/wh%3D600%2C800/sign=c34896c7b8a1cd1105e37a268922e4c4/37d12f2eb9389b50745692a58735e5dde6116e9f.jpg" /></a></p>

<p><a href="http://d.hiphotos.baidu.com/zhidao/pic/item/37d3d539b6003af32912ae97372ac65c1138b698.jpg" target="_blank"><img src="http://d.hiphotos.baidu.com/zhidao/wh%3D600%2C800/sign=afa41ba736a85edffad9f6257964251b/37d3d539b6003af32912ae97372ac65c1138b698.jpg" /></a>怎么办呢?</p>

<p>2014-05-24 12:40提问者采纳</p>

<pre>
1、扩展字段
2、路径处理一下再存</pre>

<p>追问：</p>

<pre>
我这个字段是200字节,而要存的东西一共70个字,但是还是会报错,按照网上说的将编码集改成utf-8也还是不行啊</pre>

<p>追答：</p>

<pre>
你跟踪一下，前面看到的是70个字，传到数据库中时，是否还是70个字？我估计是超长了</pre>

<p>追问：</p>

<pre>
怎么追踪?是在java文件里面打印有多少个字符吗?</pre>

<p>追答：</p>

<pre>
对，在java程序发往数据的时候，即数据访问的时候</pre>"""
    s = s.replace('\t',r'&nbsp&;').replace('\n',r'&enter&;').replace(' ','').replace('\"', '\'')
    sql = 'insert into blog (title,author,time,content,tag,class) values("%s", "%s", "%s", "%s", "%s", "%s")' %('test8','admin','2016-04-26',s,'tag', 'class')
    print sql
    DB().insert(sql)
