#!/usr/bin/python -O
#product environment start application with `tornado IOLoop` and `gevent server`

from BLOG.blog import app
from BLOG.Tools import LOG
from BLOG.Tools.config import Host, Port, Environment, ProcessName, ProductType

logger = LOG.Syslog.getLogger()

try:
    import setproctitle
    if ProcessName:
        setproctitle.setproctitle(ProcessName)
        logger.info("RedisMI is the process called %s" % ProcessName)
except ImportError, e:
    logger.error('%s, try to pip install setproctitle' %e)

if Environment == 'product':

    if ProductType == 'gevent':
        from gevent.wsgi import WSGIServer
        http_server = WSGIServer((Host, Port), app)
        logger.info('RedisMI has been launched, %s:%d' %(Host, Port))
        http_server.serve_forever()

    elif ProductType == 'tornado':
        from tornado.wsgi import WSGIContainer
        from tornado.httpserver import HTTPServer
        from tornado.ioloop import IOLoop
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(Port)
        logger.info('RedisMI has been launched, %s:%d' %(Host, Port))
        IOLoop.instance().start()
    else:
        logger.error('Start the program does not support with %s, abnormal exit!' %ProductType)
        exit(127)
else:
    logger.warn("%s isn't product, exit." % Environment)
