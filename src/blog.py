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
msg = {}

# 用户密码加密函数
md5 = lambda pwd:hashlib.md5(pwd).hexdigest()

# 用户上传文件验证类型
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# BLOG Index Page View
@app.route('/')
def index():
    sql="select title,author,time,content,tag from blog"
    data=mysql.get(sql)
    tags=[ d.get('tag') for d in data if d.get('tag') ]
    logger.debug(data)
    return render_template('index.html', username=username, blogs=data, tags=tags)

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
        return render_template('home.html', data=data, profile=shows, username=username, msg=msg)
    else:
        return redirect(url_for('index'))

# Time Page View
@app.route('/time')
def time():
    return render_template('time.html')

# Blog and Upload
@app.route('/home/blog/create')
def create_blog():
    if session.get('loggin_in'):
        return render_template('blog.html', username=username)
    else:
       return redirect(url_for('index'))

@app.route('/upload', methods=['GET','POST','OPTIONS'])
def upload():
    """UEditor文件上传接口

    config 配置文件
    result 返回结果
    """
    mimetype = 'application/json'
    result = {}
    action = request.args.get('action')

    # 解析JSON格式的配置文件
    with open(os.path.join(app.static_folder, 'ueditor', 'php',
                           'config.json')) as fp:
        try:
            # 删除 `/**/` 之间的注释
            CONFIG = json.loads(re.sub(r'\/\*.*\*\/', '', fp.read()))
        except:
            CONFIG = {}

    if action == 'config':
        # 初始化时，返回配置文件给客户端
        result = CONFIG

    elif action in ('uploadimage', 'uploadfile', 'uploadvideo'):
        # 图片、文件、视频上传
        if action == 'uploadimage':
            fieldName = CONFIG.get('imageFieldName')
            config = {
                "pathFormat": CONFIG['imagePathFormat'],
                "maxSize": CONFIG['imageMaxSize'],
                "allowFiles": CONFIG['imageAllowFiles']
            }
        elif action == 'uploadvideo':
            fieldName = CONFIG.get('videoFieldName')
            config = {
                "pathFormat": CONFIG['videoPathFormat'],
                "maxSize": CONFIG['videoMaxSize'],
                "allowFiles": CONFIG['videoAllowFiles']
            }
        else:
            fieldName = CONFIG.get('fileFieldName')
            config = {
                "pathFormat": CONFIG['filePathFormat'],
                "maxSize": CONFIG['fileMaxSize'],
                "allowFiles": CONFIG['fileAllowFiles']
            }

        if fieldName in request.files:
            field = request.files[fieldName]
            uploader = Uploader(field, config, app.static_folder)
            result = uploader.getFileInfo()
        else:
            result['state'] = '上传接口出错'

    elif action in ('uploadscrawl'):
        # 涂鸦上传
        fieldName = CONFIG.get('scrawlFieldName')
        config = {
            "pathFormat": CONFIG.get('scrawlPathFormat'),
            "maxSize": CONFIG.get('scrawlMaxSize'),
            "allowFiles": CONFIG.get('scrawlAllowFiles'),
            "oriName": "scrawl.png"
        }
        if fieldName in request.form:
            field = request.form[fieldName]
            uploader = Uploader(field, config, app.static_folder, 'base64')
            result = uploader.getFileInfo()
        else:
            result['state'] = '上传接口出错'

    elif action in ('catchimage'):
        config = {
            "pathFormat": CONFIG['catcherPathFormat'],
            "maxSize": CONFIG['catcherMaxSize'],
            "allowFiles": CONFIG['catcherAllowFiles'],
            "oriName": "remote.png"
        }
        fieldName = CONFIG['catcherFieldName']

        if fieldName in request.form:
            # 这里比较奇怪，远程抓图提交的表单名称不是这个
            source = []
        elif '%s[]' % fieldName in request.form:
            # 而是这个
            source = request.form.getlist('%s[]' % fieldName)

        _list = []
        for imgurl in source:
            uploader = Uploader(imgurl, config, app.static_folder, 'remote')
            info = uploader.getFileInfo()
            _list.append({
                'state': info['state'],
                'url': info['url'],
                'original': info['original'],
                'source': imgurl,
            })

        result['state'] = 'SUCCESS' if len(_list) > 0 else 'ERROR'
        result['list'] = _list

    else:
        result['state'] = '请求地址出错'

    result = json.dumps(result)

    if 'callback' in request.args:
        callback = request.args.get('callback')
        if re.match(r'^[\w_]+$', callback):
            result = '%s(%s)' % (callback, result)
            mimetype = 'application/javascript'
        else:
            result = json.dumps({'state': 'callback参数不合法'})

    res = make_response(result)
    res.mimetype = mimetype
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Headers'] = 'X-Requested-With,X_Requested_With'
    return res


# Login
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

@app.route('/json',methods=['GET','POST'])
def ajax():
    if session.get('loggin_in'):
        return json.dumps({'code':0, 'msg':'success'})
    else:
        return json.dumps({'code':1, 'msg':u'权限拒绝'})

@app.route('/ajax.html')
def note():
    return render_template('ajax.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html')

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
