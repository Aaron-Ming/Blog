# -*- coding:utf8 -*-

#全局配置端
GLOBAL={

#"Environment": "dev",
"Environment": "product",
#  1. The meaning of the representative is the application of the environment, the value of dev, product;
#  2. When the value is dev, only exec app.run() with flask.
#  3. When the value is product, will start server with tornado or gevent.
#  3. When the value is "super debug", will start tuning mode.

"Host": "0.0.0.0",
#  Application run network address, you can set it `0.0.0.0`, `127.0.0.1`, ``, `None`;
#  Default run on all network interfaces.

"Port": 10000,
#  Application run port, default port;

"Debug": True,
#  Open debug mode?
#  The development environment is open, the production environment is closed, which is also the default configuration.

"LogLevel": "DEBUG",
#  应用程序写日志级别，目前有DEBUG，INFO，WARNING，ERROR，CRITICAL

}


#生产环境配置段
PRODUCT={

"ProcessName": "SIC.Blog",
#  Custom process, you can see it with "ps aux|grep ProcessName".

"ProductType": "gevent",
#  生产环境启动方法，可选`gevent`与`tornado`,其中tornado log level是WARNNING，也就是低于WARN级别的日志不会打印或写入日志中。
}


#数据库配置段
MYSQL={

"MySQLConnection": {
    "Host": "127.0.0.1",
    "Port": 3306,
    "Database": "blog",
    "User": "root",
    "Passwd": "123456",
    "Charset": "utf8",
    "Timezone": "+8:00"}
    #  MySQL连接信息，格式可包括在()、[]、{}内，分别填写主机名或IP、端口、数据库、用户、密码、字符集、时区等，其中port默认3306、字符集默认utf8、时区默认东八区，注意必须写在一行内！
}


#博客配置段
BLOG={

"NominateID": (1, 2, 3),
#推荐文章的ID号，展示在首页顶部。

"AdminGroup": ("admin", "taochengwei"),
#管理员组成员配置

"AboutContent": u"我对茶情有独钟，买什么都喜欢带有淡淡的茶香味，在袅袅的茶气中，泡着茶，提壶、注水、出汤、品尝，自然平静，俨然与茶浑然一体。泡茶和喝茶重要的是用心，只要用心，不一定是昂贵的茶叶，不一定要精雕细刻的茶具，也不需要>复杂多变的手法，一样能够泡出清香四溢、韵味十足的好茶。若是感到心烦意乱、孤独寂寞、茫然无助，就为自己泡茶。淡>而入心，唯有茶也。"
#关于我内容配置
}

