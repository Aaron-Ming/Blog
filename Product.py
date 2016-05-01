#!/usr/bin/python -O
#product environment start application with `tornado IOLoop` and `gevent server`

from src.api import app
from src.Tools.LOG import Syslog
from src.config import GLOBAL,PRODUCT

Host = str(GLOBAL.get('Host'))
Port = GLOBAL.get('Port')
Environment = GLOBAL.get('Environment')
ProcessName = PRODUCT.get('ProcessName')
ProductType = PRODUCT.get('ProductType')
logger = Syslog.getLogger()

try:
    import setproctitle
    if ProcessName:
        setproctitle.setproctitle(ProcessName)
        logger.info("The process is %s" % ProcessName)
except ImportError, e:
    ProcessName = None
    logger.warn("%s, try to pip install setproctitle, otherwise, you can't use the process to customize the function" %e)

if Environment != 'product':
    logger.error("%s isn't product, exit." % Environment)
    exit(128)  

try:
    logger.info('%s has been launched, %s:%d' %(ProcessName, Host, Port))
    if ProductType == 'gevent':
        from gevent.wsgi import WSGIServer
        http_server = WSGIServer((Host, Port), app)
        http_server.serve_forever()

    elif ProductType == 'tornado':
        from tornado.wsgi import WSGIContainer
        from tornado.httpserver import HTTPServer
        from tornado.ioloop import IOLoop
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(Port)
        IOLoop.instance().start()

    else:
        logger.error('Start the program does not support with %s, abnormal exit!' %ProductType)
        exit(127)

except Exception,e:
    print e
    logger.error(e)
