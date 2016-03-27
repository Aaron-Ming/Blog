# -*- coding:utf-8 -*-

__version__ = '0.1'
__doc__ = 'Python Blog System for SIC(Team).'
__author__ = 'Tao Chengwei <staugurtcw@gmail.com>'

import os
import json
import hashlib
from Tools.DB import DB
from Tools.LOG import Syslog
from werkzeug import secure_filename
from flask import Flask, request, session, render_template, redirect, url_for, send_from_directory

# Init Flask App and Global Args
app = Flask(__name__)
# This is session secret
app.secret_key = os.urandom(24)
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
# Limit file is 2M.
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])

# Define || Get something data
mysql = DB()
logger = Syslog.getLogger()
username = None
msg = None

# 用户密码加密函数
md5 = lambda pwd:hashlib.md5(pwd).hexdigest()

# 用户上传文件验证类型
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# BLOG Index Page View
@app.route('/')
def index():
    return render_template('index.html', username=username)

# User Home Page View
@app.route('/home/<username>')
def home(username):
    if session.get('loggin_in'):
        sql="select * from user where username='%s'" % username
        data=mysql.get(sql)
        shows={"cname":u"姓名", "url":u"网址", "motto":u"座右铭", "email":u"邮箱", "extra":u"个人介绍"}
        #pk=[ x for x in map(change, [ k for k in data.keys() if k in shows ]) if x ]
        #pv=[ data.get(y) for y in shows.keys() if y ]
        logger.debug(data)
        return render_template('user/home.html', data=data, profile=shows, username=username, msg=msg)
    else:
        return redirect(url_for('index'))

# Time Page View
@app.route('/time')
def time():
    return render_template('time.html')

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
#创建用户
@app.route('/api/user/create/<username>', methods = ["GET", "POST"])
def user_create(username):
    global msg
    if request.method == 'POST':
        new_username = request.form.get('new_username')
        new_password = request.form.get('new_password')

        if mysql.get("select username from user where username='%s'" % new_username):
            msg = "Fail: User already exists!"
        else:
            logger.warn(type(new_password))
            logger.warn(new_password)
            sql="insert into user (username, password) values('%s', '%s')" %(new_username, md5(new_password))
            try:
                mysql.insert(sql)
            except Exception, e:
                logger.error(e)
            msg="Success: Create User %s!" % new_username
    return redirect(url_for('home',username=username,action='create'))

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
    return redirect(url_for('home',username=username))

#删除用户
@app.route('/api/user/delete/<username>', methods = ["GET", "POST"])
def user_del(username):
    global msg
    if request.method == 'POST':
        try:
            del_username = request.json.get('del_username')
        except Exception:
            del_username = request.form.get('del_username')
        if del_username == "admin":
            msg="Fail: Not Allow admin"
        else:
            sql="delete from user where username='%s'" % del_username
            try:
                mysql.delete(sql)
            except Exception,e:
                logger.error(e)
            else:
                msg="Success: Deleted User %s" % del_username
    return redirect(url_for('home',username=username,action='delete'))

@app.route('/api/user/list/<username>')
def user_list(username):
    sql="select * from user where username='%s'" % (username)
    try:
        data=mysql.get(sql)
    except Exception,e:
        logger.error(e)
    return json.dumps({"code":0, "data":data})


@app.route('/ajax.html')
def ajax():
    return render_template('ajax.html')

@app.route('/note.xml')
def note():
    return render_template('note.xml')

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
