# -*- coding:utf-8 -*-

import re
import json
from blog import *
from flask import Flask, request, make_response
from flask.ext.restful import Api, Resource, reqparse, abort

api = Api(app)

#创建博客
@app.route('/api/blog/create/<username>', methods = ["GET", "POST"])
def blog_create(username):
    return redirect(url_for('home', username=username, action='blog_create'))


#创建用户
@app.route('/api/user/create/<username>', methods = ["GET", "POST"])
def user_create(username):
    global msg
    if request.method == 'POST':
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')

        if mysql.get("select username from user where username='%s'" % new_username):
            msg = {"action":"create", "msg":"Fail: User already exists!"}
        else:
            logger.warn(type(new_password))
            logger.warn(new_password)
            sql="insert into user (username, password) values('%s', '%s')" %(new_username, md5(new_password))
            try:
                mysql.insert(sql)
            except Exception, e:
                logger.error(e)
            msg = {"action":"create", "msg":"Success: Create User %s!" % new_username}
    return redirect(url_for('home', username=username, action='create'))

#更新用户
@app.route('/api/user/update/<username>', methods = ["GET", "POST"])
def user_update(username):
    if request.method == 'POST':
        d={"cname": request.form.get('cname',None),
           "email": request.form.get('email',None),
           "motto": request.form.get('motto',None),
           "url":   request.form.get('url',None),
           "extra": request.form.get('extra',None)}
        s=""
        L=len(d)
        logger.debug(d)
        for k,v in d.iteritems():
            L-=1
            if not v:
                continue
            if L == 0:
                s+="%s='%s'" %(k,v)
            else:
                s+="%s='%s'," %(k,v)
        if s[-1] == ',':
            s=s[0:len(s)-1]
        sql="update user set %s where username='%s'" %(s, username)
        logger.info(sql)
        try:
            mysql.update(sql)
        except Exception, e:
            logger.error(e)
    return redirect(url_for('home',username=username))

#用户上传文件更新头像
@app.route('/api/user/upload/<username>', methods=['GET','POST'])
def user_upload(username):
    if request.method == 'POST':
        f = request.files['file']
        # Check if the file is one of the allowed types/extensions
        if f and allowed_file(f.filename):
            # Make the filename safe, remove unsupported chars
            fname = secure_filename(f.filename)
            # Move the file form the temporal folder to the upload folder we setup
            fnameurl=os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
            if not os.path.exists(fnameurl):
                try:
                    os.mkdir(fnameurl)
                except OSError,e:
                    logger.error(e)
            f.save(os.path.join(fnameurl, fname))
            # return user home and write avatar url into mysql db.
            sql="update user set avatar='%s' where username='%s'" %(os.path.join('/', app.config['UPLOAD_FOLDER'], fname), username)
            logger.info(sql)
            try:
                mysql.update(sql)
            except Exception,e:
                logger.error(e)
    return redirect(url_for('home', username=username))

#访问用户上传
#@app.route('/uploads/<filename>')
#def uploaded_file(filename):
#    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)#

#修改密码
@app.route('/api/user/passwd/<username>', methods = ["GET", "POST"])
def user_passwd(username):
    global msg
    #需要输入当前密码，与客户端交互。
    if session.get('loggin_in'):
        if request.method == 'POST':
            pwdnew = request.form.get('password')
            sql="update user set password='%s' where username='%s'" %(md5(pwdnew), username)
            logger.info(sql)
            try:
                mysql.update(sql)
            except Exception, e:
                logger.error(e)
                msg = {"action":"passwd","msg":"Modify password failed!"}
            else:
                msg = {"action":"passwd","msg":"Modify password success!"}
    return redirect(url_for('home',username=username,action='passwd'))

#删除用户
@app.route('/api/user/delete/<username>', methods = ["GET", "POST"])
def user_del(username):
    global msg
    if request.method == 'POST':
        try:
            del_username = request.json.get('del_username')
        except Exception:
            del_username = request.form.get('del_username')
        sql="select * from user where username='%s'" % (del_username)
        if del_username == "admin":
            msg = {"action":"delete","msg":"Fail: Not Allow admin"}
        elif mysql.get(sql) == None:
            msg = {"action":"delete","msg":"Fail: No username"}
        else:
            sql="delete from user where username='%s'" % del_username
            try:
                mysql.delete(sql)
            except Exception,e:
                logger.error(e)
            else:
                msg = {"action":"delete", "msg":"Success: Deleted User %s" % del_username}
    return redirect(url_for('home', username=username, action='delete'))

#用户列表
@app.route('/api/user/list/<username>', methods=['GET','POST'])
def user_list(username):
    global msg
    sql="select username from user"
    try:
        data=mysql.get(sql)
    except Exception,e:
        logger.error(e)
        msg={"action":"list", "msg":e}
    else:
        msg={"action":"list", "msg":data}
    return json.dumps(msg)
    return redirect(url_for('home', username=username, action='list'))


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

