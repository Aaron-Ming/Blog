# -*- coding:utf-8 -*-

import os
import re
import json
import hashlib
import random
import datetime
from Tools.DB import DB
from Tools.LOG import Syslog
from config import BLOG
from werkzeug import secure_filename
from flask import Flask, request, session, render_template, redirect, url_for, send_from_directory, Response

__version__ = '0.3'
__doc__ = 'Python Blog System for SIC(Team).'
__author__ = 'Mr.Tao <staugurtcw@gmail.com>'

# Init Flask App and Global Args
app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'static/upload/'
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg', 'gif'])

mysql = DB()
logger = Syslog.getLogger()
username = None
msg = {}

# 用户密码加密函数
md5 = lambda pwd:hashlib.md5(pwd).hexdigest()

# 获取今天的日期
today = lambda :datetime.datetime.now().strftime("%Y-%m-%d")

# 用户上传文件验证类型
allowed_file = lambda filename:'.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# 文本编辑器上传定义随机命名
gen_rnd_filename = lambda :"%s%s" %(datetime.datetime.now().strftime('%Y%m%d%H%M%S'), str(random.randrange(1000, 10000)))

"""
#基于调度的方法
#http://docs.jinkan.org/docs/flask/views.html
from flask.views import MethodView
class UserAPI(MethodView):
    def get(self):
        users = User.query.all()
        ...
    def post(self):
        user = User.from_form_data(request.form)
        ...
app.add_url_rule('/users/', view_func=UserAPI.as_view('users'))
"""


def NIT():
    Nominate={}
    html = re.compile(r'<[^>]+>',re.S)
    for nid in BLOG.get('NominateID', (1, 2, 3))[:3]:
        #根据推荐id导出博客信息
        sql="SELECT id,title,content FROM blog WHERE id=%d" %nid
        try:
            data=mysql.get(sql)
            content=html.sub('', data.get('content')[:35])
            Nominate[nid]={"nid":nid, "title":data.get('title'), "content":content}
        except Exception,e:
            logger.error(e)
        else:
            logger.debug({"nid":nid, "title":data.get('title'), "content":content})
    logger.info(Nominate)
    return Nominate

@app.before_request
def before_request():
    logger.info(json.dumps({
        "AccessLog": {
            "login_user": session.get('username', None),
            "status_code": Response.default_status,
            "method": request.method,
            "ip": request.headers.get('X-Real-Ip', request.remote_addr),
            "url": request.url,
            "referer": request.headers.get('Referer'),
            "agent": request.headers.get("User-Agent"),
            }
        }
    ))

# BLOG Index Page View
@app.route('/')
def index():
    sql="SELECT id,title,author,time,content,tag,class FROM blog LIMIT %d" %int(BLOG.get('IndexPageNum', 5))
    logger.info(sql)
    data=mysql.get(sql)
    tags=list(set([ d.get('tag').replace("'", "") for d in data if d.get('tag') ]))
    logger.debug({"tags": tags})

    sql="SELECT ClassName FROM class"
    logger.info(sql)
    types=mysql.get(sql)
    classes=[ _type.get('ClassName') for _type in types if _type.get('ClassName') ]
    logger.debug({"classes": classes})

    return render_template('index/index.html', username=username, blogs=data, tags=tags, classes=classes, Nominate=NIT().values(), teammotto=BLOG.get('TeamMotto'))

# Google check for Search Console, robots.txt, sitemap
@app.route('/google32fd52b6c900160b.html')
def google_search_console():
    return render_template('public/google32fd52b6c900160b.html')

@app.route('/robots.txt')
def robots():
    return render_template('public/robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return render_template('public/sitemap.xml')

# About Us
@app.route('/about.html')
def about():
    return render_template('index/about.html', AboutContent=BLOG.get('AboutContent'))

@app.route('/link')
def link():
    return render_template('index/link.html')

# Friend Links
@app.route('/blog/<int:bid>.html')
def blog(bid):
    sql="SELECT title,author,time,content,tag,class FROM blog where id=%d" %int(bid)
    try:
        data=mysql.get(sql)
        logger.info({"func:blog:SQL":sql})
    except Exception,e:
        logger.error(e)
    return render_template('index/link.html', bid=bid, blog=data)

# User Home Page View
@app.route('/home/<username>')
def home(username):
    if session.get('loggin_in'):
        sql="select * from user where username='%s'" % username
        data=mysql.get(sql)
        shows={"cname":u"姓名", "url":u"网址", "motto":u"座右铭", "email":u"邮箱", "extra":u"个人介绍"}
        logger.debug(data)
        return render_template('user/home.html', data=data, profile=shows, username=username, msg=msg)
    else:
        return redirect(url_for('login'))

# Blog and Upload
@app.route('/home/blog/create', methods=['GET','POST'])
def create_blog():
    if session.get('loggin_in'):
        #user persion data
        sql="select * from user where username='%s'" % username
        logger.info(sql)
        userdata=mysql.get(sql)
        logger.debug(userdata)

        #blog class types
        sql="SELECT ClassName FROM class"
        logger.info(sql)
        types=mysql.get(sql)
        classdata = {}.fromkeys([ _type.get('ClassName') for _type in types if _type.get('ClassName') ]).keys()
        logger.debug(classdata)

        if request.method == "POST":
            #get form data
            #blogdata=request.form.items()
            #logger.info(blogdata)
            #blogdata=blogdata[0]
            title     = request.form.get('title')
            author    = username
            time      = today()
            content   = request.form.get('ckeditor')
            tag       = request.form.get('tag')
            classtype = request.form.get('type')
            sql="insert into blog (title,author,time,content,tag,class) values('%s','%s','%s','%s','%s','%s')" %(title,author,time,content,tag,classtype)
            logger.info(sql)
            #此处需要重写DB类的insert方法，用(sql, arg1, arg2, ...)插入数据库中避免错误
            try:
                mysql.insert(sql)
            except AttributeError:
                mysql.execute(sql)
            except Exception,e:
                logger.error(e)
        return render_template('user/blog.html', username=username, data=userdata, types=classdata)
    else:
        return redirect(url_for('index'))

# Login
@app.route('/login', methods = ["GET","POST"])
def login():
    error=None
    global username
    if request.method == "GET":
        if session.get('loggin_in'):
	    #Now should get request url and return that.
            return redirect(url_for('index'))
        else:
            return render_template('user/login.html')
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
                        session['username'] = username
                        return redirect(url_for('index'))
                    else:
                        error = 'Invalid username'
                else:
                    error = 'Invaild password'
        if error:
            return render_template('user/login.html', error=error)
        else:
            return redirect(url_for('index'))

# Logout System Page View
@app.route('/logout')
def logout():
    try:
        session.pop('loggin_in')
        session.pop('username')
    except Exception:
        pass
    return redirect(url_for('index'))

# API System

#创建博客
@app.route('/home/blog/create/<username>', methods = ["GET", "POST"])
def blog_create(username):
    return redirect(url_for('home', username=username, action='blog_create'))

#创建用户
@app.route('/home/user/create/<username>', methods = ["GET", "POST"])
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
@app.route('/home/user/update/<username>', methods = ["GET", "POST"])
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
@app.route('/home/user/upload/<username>', methods=['GET','POST'])
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
@app.route('/home/user/passwd/<username>', methods = ["GET", "POST"])
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
@app.route('/home/user/delete/<username>', methods = ["GET", "POST"])
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
@app.route('/home/user/list/<username>', methods=['GET','POST'])
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

@app.errorhandler(404)
def not_found(error):
    return render_template('public/404.html')

if __name__ == '__main__':
    print u"请运行api.py启动"
