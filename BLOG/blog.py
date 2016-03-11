#!/usr/bin/python -O
# -*- coding:utf-8 -*-

__version__ = '0.1'
__doc__ = 'Python Blog System for SIC(Team).'
__author__ = 'Tao Chengwei <staugurtcw@gmail.com>'

import os
import time
import json
import hashlib
from functools import wraps
from Tools.DB import DB
from Tools.LOG import Syslog
from flask import Flask, request, session, render_template, redirect, url_for

# Init Flask App and Global Args
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Define || Get something data
mysql = DB()
logger = Syslog.getLogger()

def loggin_required(func):
    @wraps(func)
    def check():
        if session.get('loggin_in'):
            func()
        else:
            return redirect(url_for('login'))
    return check

def md5(s):
    if not isinstance(s, (str, int, unicode)): raise
    return hashlib.md5(s).hexdigest()

# BLOG Index Page View
@app.route('/', methods = ['GET', 'POST'])
def index():
    error = None
    if request.method == "GET":
        return render_template('index.html')
    elif request.method == "POST":
        _user = request.form.get('username')
        _pass = request.form.get('password')
        if _user == None or _pass == None:
            error = 'Invalid username or password'
            return render_template('index.html', error=error)
        sql = 'select * from user where username="%s"' % _user
        data = mysql.get(sql)
        if data == None:
            error = 'Invalid username'
        else:
            if md5(_pass) == data.get('password'):
                if _user == data.get('username'):
                    session['loggin_in'] = True
                    return redirect('/')
                else:
                    error = 'Invalid username'
            else:
                error = 'Invaild password'

    return render_template('index.html', error=error)

# User Home Page View
@app.route('/home')
@loggin_required
def home():
    return render_template('home.html', year=time.strftime("%Y"))

# Logout System
@app.route('/logout')
def logout():
    try:
        session.pop('loggin_in')
    except Exception:
        pass
    return redirect('/')

# API System

# 用户API(Please add a class override default, return json)
@app.route('/api/user/<username>', methods = ['GET', 'POST', 'PUT', 'DELETE'])
def register(username, all=False):
    #获取用户列表或具体用户
    if request.method == 'GET':
        try:
            username = request.json.get('username')
        except Exception:
            username = request.form.get('username')
        if request.args.get('all', False):
            sql="select * from user"
        else:
            sql="select * from user where username='%s'" % username
        return json.dumps({'code':0, 'msg':mysql.get(sql)})
    #创建用户
    elif request.method == 'POST':
        try:
            username = request.json.get('username')
            password= request.json.get('password')
        except Exception:
            username = request.form.get('username')
            passport = request.form.get('passport')

        if mysql.get("select * from user where username='%s'" % username):
            return json.dumps({'code':1, 'msg':'User already exists'})
        else:
            sql="insert into user (username, password) values('%s', '%s')" %(username, md5(password))
            mysql.insert(sql)
            return json.dumps({'code':0, 'username':username, 'state':'added'})
    #更新用户
    elif request.method == 'PUT':
        pass
    #删除用户
    elif request.method == 'DELETE':
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

"""
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')
"""

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
