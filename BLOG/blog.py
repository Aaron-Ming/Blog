#!/usr/bin/python -O
# -*- coding:utf-8 -*-

__version__ = '0.1'
__doc__ = 'Python Blog System for SIC(Team).'
__author__ = 'Tao Chengwei <staugurtcw@gmail.com>'

import os
import time
import json
from Tools.DB import DB
from Tools.LOG import Syslog
from flask import Flask, request, session, render_template, redirect, make_response, abort

# Init Flask App and Global Args
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Define || Get something data
mysql = DB()
logger = Syslog.getLogger()

def md5(s):
    if not isinstance(s, (str)): raise
    import hashlib
    return hashlib.md5(s).hexdigest()

# BLOG UI
@app.route('/')
def index():
    return render_template('index.html')

# User Home Page View
@app.route('/home')
def home():
    if session.get('loggin_in'):
        return render_template('home.html', year=time.strftime("%Y"))
    else:
        return redirect('/')

# BLOG Admin System
@app.route('/admin')
def admin():
    return render_template('admin/index.html')

# Login Auth
@app.route('/login', methods = ["GET","POST"])
def login():
    error = None
    global username
    if request.method == "POST":
        _user = request.form.get('username')
        _pass = request.form.get('password')
        _sql = 'select * from user where username="%s"' % _username
        _data = mysql.get(sql)
        if md5(_pass) == _data.get('password'):
            if _user == _data.get('username'):
                session['loggin_in'] = True
                return redirect('/')
            else:
                error = 'Invalid username'
        else:
            error = 'Invaild password'
    return render_template('login.html', error=error)

# Logout System
@app.route('/logout')
def logout():
    try:
        session.pop('loggin_in')
    except Exception:
        pass
    return redirect('/')

# API
@app.route('/api/register', methods = ['POST'])
def register():
    if request.method == 'POST':
        if not request.json or not 'username' in request.json or not 'password' in request.json:
            abort(400)
        username = request.json.get('username')
        password= request.json.get('password')
        logger.debug(request.json)
        if mysql.get("select * from user where username='%s'" % username):
            return json.dumps({'Error': 'User already exists'})
        else:
            sql="insert into user (username, password, email) values('%s', '%s', '')" %(username, md5(password))
            mysql.insert(sql)
            return json.dumps({'Result':'SUCCESS', 'username':username})

@app.route('/api/delete/<username>', methods = ['POST'])
def delete(username):
    if request.methods == 'POST':
        if not username:
            abort(400)
        sql="delete from usser where username='%s'" % username
        mysql.delete(sql)

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

if __name__ == '__main__':
    # Start in dev environment
    from Tools.config import Host, Port, Environment, Debug
    if Environment == "dev":
        app.run(host=Host, port=int(Port), debug=Debug)
    elif Environment == "super debug":
        from werkzeug.contrib.profiler import ProfilerMiddleware
        app.config['PROFILE'] = True
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [30])
        app.run(debug=Debug, host=Host, port=int(Port))
