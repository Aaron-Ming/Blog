#-*- coding:utf8 -*-
#Supports configuration files for Python data types, including variables, lists, dictionaries, etc.

Environment = "dev"
#Environment = "product"
"""
Environment:
  1. The meaning of the representative is the application of the environment, the value of dev, product;
  2. When the value is dev, only exec app.run() with flask.
  3. When the value is product, will start server with tornado or gevent.
  3. When the value is "super debug", will start tuning mode.
"""

Host = "0.0.0.0"
"""
Host:
    Application run network address, you can set it `0.0.0.0`, `127.0.0.1`, ``, `None`;
    Default run on all network interfaces.
"""

Port = 8000
"""
Port:
    Application run port, default is 5000;
"""

ProcessName = "Blog"
"""
ProcessName:
    Custom process, you can see it with "ps aux|grep ProcessName".
"""

Debug = True
"""
Debug:
    Open debug mode?
    The development environment is open, the production environment is closed, which is also the default configuration.
"""

LogLevel = "DEBUG"
"""
LogLevel:
    应用程序写日志级别，目前有DEBUG，INFO，WARNING，ERROR，CRITICAL
"""

ProductType = "tornado"
"""
ProductType:
    生产环境启动方法，可选`gevent`与`tornado`,其中tornado log level是WARNNING，也就是低于WARN级别的日志不会打印或写入日志中。
"""

ApplicationHome = "/data/wwwroot/Blog"
"""
ApplicationHome:
    应用代码存在目录，包含启动服务的脚本，生产环境配置。
"""

MySQLConnection = {
    "Host": '127.0.0.1',
    "Port": 3306,
    "Database": 'blog',
    "User": 'root',
    "Passwd": '123456',
    "Charset": 'utf8',
    "Timezone": '+8:00'
}

