#!/usr/bin/python -O
# -*- coding:utf-8 -*-

__version__ = '0.1'
__doc__ = 'Python Blog System for SIC(Team).'
__author__ = 'Tao Chengwei <staugurtcw@gmail.com>'

import os
import json
import hashlib
from Tools.DB import DB
from Tools.LOG import Syslog
from flask import Flask, request, session, render_template, redirect, url_for

# Init Flask App and Global Args
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Define || Get something data
mysql = DB()
logger = Syslog.getLogger()
username = None

def md5(s):
    if not isinstance(s, (str, int, unicode)): raise
    return hashlib.md5(s).hexdigest()

# BLOG Index Page View
@app.route('/')
def index():
    return render_template('index.html', username=username)

# User Home Page View
@app.route('/home/<username>')
def home(username):
    if session.get('loggin_in'):
        sql="select * from user where username='%s'" % username
        logger.debug(mysql.get(sql))
        return render_template('user/home.html', data=mysql.get(sql), username=username)
    else:
        return redirect(url_for('index'))

# Time Page View
@app.route('/time')
def time():
    return render_template('time.html')

# User Login Page View
@app.route('/login', methods = ["GET","POST"])
def login():
    error=None
    global username
    if request.method == "GET":
        if session.get('loggin_in'):
            return redirect('/')
        else:
            return render_template('login.html')
    elif request.method == "POST":
        _user = request.form.get('username')
        _pass = request.form.get('password')
        if _user == None or _pass == None:
            error = 'Invalid username or password'
        else:
            sql = 'select * from user where username="%s"' % _user
            data = mysql.get(sql)
            if data == None:
                error = 'Invalid username'
            else:
                username = data.get('username')
                password = data.get('password')
                if md5(_pass) == password:
                    if _user == username:
                        session['loggin_in'] = True
                        return redirect('/')
                    else:
                        error = 'Invalid username'
                else:
                    error = 'Invaild password'
        if error:
            return render_template('login.html', error=error)
        else:
           return redirect(url_for('index'))

# Logout System Page View
@app.route('/logout')
def logout():
    try:
        session.pop('loggin_in')
    except Exception:
        pass
    return redirect(url_for('index'))

# API System
# 用户API(Please add a class override default, return json)

#获取用户列表或具体用户
@app.route('/api/user/get/<username>')
def user_get(username):
    code=1
    data=None
    if request.method == 'GET':
        try:
            username = request.json.get('username')
        except Exception:
            username = request.form.get('username')
        sql="select * from user where username='%s'" % username
        data=mysql.get(sql)
        if data:
            code=0
    return json.dumps({'code':code, 'data':data})

#创建用户
@app.route('/api/user/create/<username>', methods = ["GET", "POST"])
def user_create(username):
    code=1
    data=None
    if request.method == 'POST':
        try:
            username = request.json.get('username')
            password = request.json.get('password')
        except Exception:
            username = request.form.get('username')
            passport = request.form.get('passport')

        if mysql.get("select * from user where username='%s'" % username):
            code, data = 126, "User already exists"
        else:
            sql="insert into user (username, password) values('%s', '%s')" %(username, md5(password))
            try:
                mysql.insert(sql)
            except Exception, e:
                logger.error(e)
                code, data = 127, "用户注册失败"
            code, data = 0, username
    return json.dumps({'code':code, 'data':data})

#更新用户
@app.route('/api/user/update/<username>', methods = ["GET", "POST"])
def user_update(username):
    if request.method == 'POST':
        cname = request.form.get('cname',None)
        email = request.form.get('email',None)
        motto = request.form.get('motto',None)
        url   = request.form.get('url',None)
        extra = request.form.get('extra',None)
        r={"cname":cname, 'email':email, 'motto':motto, 'url':url, 'extra':extra}
        s=''
        L=len(r)
        for k,v in r.iteritems():
            L-=1
            if not v:
                continue
            if L == 0:
                s+="%s='%s'" %(k,v)
            else:
                s+="%s='%s'," %(k,v)
        sql="update user set %s where username='%s'" %(s, username)
        logger.info(sql)
        try:
            mysql.update(sql)
        except Exception, e:
            logger.error(e)
    return redirect(url_for('home',username=username))

#删除用户
@app.route('/api/user/update/<username>', methods = ["GET", "DELETE"])
def user_del(username):
    code=1
    data=None
    if request.method == 'DELETE':
        try:
            username = request.json.get('username')
        except Exception:
            username = request.form.get('username')

        if not username:
            return json.dumps({'code':1, 'msg':'No such username'})
        else:
            sql="delete from usser where username='%s'" % username
            mysql.delete(sql)
            return json.dumps({'code':0, 'username':username, 'state':'deleted'})
    else:
        pass

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

if __name__ == '__main__':
    # Start in dev and test environment
    from Tools.config import Host, Port, Environment, Debug
    if Environment == "dev":
        app.run(host=Host, port=int(Port), debug=Debug)
    elif Environment == "super debug":
        from werkzeug.contrib.profiler import ProfilerMiddleware
        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [30])
        app.run(debug=Debug, host=Host, port=int(Port))
