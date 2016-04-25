# -*- coding:utf-8 -*-

import re
from blog import app,logger,mysql
from flask import Flask, request, make_response
from flask.ext.restful import Api, Resource, reqparse, abort

#app=Flask(__name__)
api = Api(app)

class Blog(Resource):
    def get(self):
        try:
            num = int(request.args.get('num', 10))
        except ValueError,e:
            logger.warn(e)
            return {"code":126, "msg": "num is not integer"}
        #num, 限制列出数据数量，默认值10，不参与优先级
        listBlogId = request.args.get('list', False) #列出博客所有id，优先级1
        id = request.args.get('id', None)           #查看某个id的博客数据，优先级2
        if id != None:
            try:
                id=int(id)
            except ValueError,e:
                logger.debug(type(id)+id)
                return {"code":126, "msg": "id is invaild"}

        if listBlogId == True or listBlogId == 'true':
            sql="SELECT id FROM blog LIMIT %d" %num
        else:
            if id:
                sql="SELECT * FROM blog WHERE id='%s'" % id
            else:
                sql="SELECT * FROM blog LIMIT %d" % num
        try:
            data=mysql.get(sql)
            logger.info(sql)
            code=0
        except Exception,e:
            logger.error(e)
            code=127
        _result={'code':code, 'msg':'Get Blogs', 'data':data}
        logger.info(_result)
        return _result

class User(Resource):
    def get(self):
        #参数：num, id
        try:
            num = int(request.args.get('num', 10))
            #num, 限制列出数据数量，默认值5，不参与优先级
        except ValueError,e:
            logger.warn(e)
            return {"code":126, "msg": "num is not integer"}

        id = request.args.get('id', None) #查看某个id的用户数据，优先级3
        if id != None:
            try:
                id=int(id)
            except ValueError,e:
                logger.debug(type(id)+id)
                return {"code":126, "msg": "id is invaild"}

        sql="SELECT username FROM user LIMIT %d" %num

        if id:
            sql="SELECT id,username,cname,email,motto,url,extra FROM user WHERE id='%s' LIMIT %d" % (id, num)
        else:
            sql="SELECT id,username FROM user LIMIT %d" % num
        try:
            data=mysql.get(sql)
            logger.info(sql)
            code=0
        except Exception,e:
            logger.error(e)
            code=127
        _result={'code':code, 'msg':'Get Users', 'data':data}
        logger.info(_result)
        return _result

    def post(self):
        if True:
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


api.add_resource(Blog, '/api/blog', '/api/blog/', endpoint='api_blog')
api.add_resource(User, '/api/user', '/api/user/', endpoint='api_user')

if __name__ == '__main__':
    from Tools.Config import GLOBAL
    Host = GLOBAL.get('Host')
    Port = GLOBAL.get('Port')
    Environment = GLOBAL.get('Environment')
    Debug = GLOBAL.get('Debug')

    if Environment == "dev":
        app.run(host=Host, port=int(Port), debug=Debug)
    elif Environment == "super debug":
        from werkzeug.contrib.profiler import ProfilerMiddleware
        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [30])
        app.run(debug=Debug, host=Host, port=int(Port))
