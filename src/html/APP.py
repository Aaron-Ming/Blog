#coding:utf8
from flask import Flask,render_template
app=Flask(__name__)

@app.route('/')
def index():
    test=u"<p>这是测试文章内容</p>"
    return render_template('index.html',test=test)

if __name__ == '__main__':
    app.run(debug=True)