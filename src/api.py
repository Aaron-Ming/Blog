import re
import blog
import json
from flask import Flask, request, make_response
from flask.ext.restful import Api, Resource, reqparse, abort

__author__ = blog.__author__
__doc__    = blog.__doc__
__version__= blog.__version__

app = blog.app
api = Api(app)
logger = blog.logger
mysql = blog.mysql
md5 = blog.md5

# User Sing Up/In System.
class UserSignUp(Resource):
    def post(self):
        try:
            username = request.json.get('username', None)
            password = request.json.get('password', None)
            email    = request.json.get('email', 'NULL')
            extra    = request.json.get('extra', 'NULL')
        except Exception:
            username = request.form.get('username', None)
            password = request.form.get('password', None)
            email    = request.form.get('email', 'NULL')
            extra    = request.form.get('extra', 'NULL')
        if username == None or password == None:
            abort(400, message="username or password is empty!")
        if re.match(r'([0-9a-zA-Z\_*\.*\-*]+)@([a-zA-Z0-9\-*\_*\.*]+)\.([a-zA-Z]+$)', email) == None:
            abort(400, message="email format error")
        sql = "select username from user where username='%s'" % username
        logger.info(sql)
        if mysql.select(sql):
            data = {'code':1024, 'msg':'User already exists'}
            logger.warn(data)
        else:
            sql = "insert into user (username, password, email, extra) values('%s', '%s', '%s', '%s')" % (username, md5(password), email, extra)
            try:
                if hasattr(mysql, 'insert'):
                    mysql.insert(sql)
                else:
                    mysql.execute(sql)
                logger.info(sql)
            except Exception, e:
                data = {'code':1025, 'msg':'Sign up failed'}
                logger.error(data)
            else:
                data = {'code':0, 'msg':'Sign up success', 'data':{'username':username, 'email':email}}
                logger.info(data)
        return data

class UserDelete(Resource):
    def delete(self,username):
        if username == None:
            abort(400, message="username is empty!")
        sql = "select username from user where username='%s'" % username
        logger.info(sql)
        if mysql.select(sql):
            sql = "delete from user where username='%s'" % username
            try:
                if hasattr(mysql, 'delete'):
                    mysql.delete(sql)
                else:
                    mysql.execute(sql)
                logger.info(sql)
            except Exception, e:
                data = {'code':1026, 'msg':'Delete user failed'}
                logger.error(data)
            else:
                data = {'code':0, 'msg':'Delete success', 'data':{'username':username}}
                logger.info(data)
        else:
            data = {'code':0, 'msg':'No found username'}
        return data


#version = __version__.strip('v')
api.add_resource(Index, '/')
api.add_resource(Help, '/api/help')
api.add_resource(UserSignUp, '/api/user/reg')
api.add_resource(UserDelete, '/api/user/del/<username>')
api.add_resource(OverView, '/api/redis/overview')
api.add_resource(RedisList, '/api/redis/list')
api.add_resource(RedisDetail, '/api/redis/detail/<node>')


if __name__ == '__blog._':
    from config import Host, Port, Environment, Debug
    if Environment == "dev":
        app.run(host=Host, port=int(Port), debug=Debug)
    elif Environment == "super debug":
        from werkzeug.contrib.profiler import ProfilerMiddleware
        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
        app.run(debug=Debug, host=Host, port=int(Port))

