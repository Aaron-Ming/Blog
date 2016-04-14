#!/usr/bin/python -O
#product environment start application with `tornado IOLoop` and `gevent server`

from src.blog import app
from src.Tools.LOG import Syslog
from src.Tools.Config import GLOBAL,PRODUCT

Host = str(GLOBAL.get('Host'))
Port = int(GLOBAL.get('Port'))
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
    logger.warn("%s, try to pip install setproctitle, otherwise, you can't use the process to customize the function" %e)

if Environment == 'product':

    if ProductType == 'gevent':
        from gevent.wsgi import WSGIServer
        http_server = WSGIServer((Host, Port), app)
        logger.info('Blog has been launched, %s:%d' %(Host, Port))
        http_server.serve_forever()

    elif ProductType == 'tornado':
        from tornado.wsgi import WSGIContainer
        from tornado.httpserver import HTTPServer
        from tornado.ioloop import IOLoop
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(Port)
        logger.info('Blog has been launched, %s:%d' %(Host, Port))
        IOLoop.instance().start()

    else:
        logger.error('Start the program does not support with %s, abnormal exit!' %ProductType)
        exit(127)
else:
    logger.error("%s isn't product, exit." % Environment)
