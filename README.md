# SICBlog
SIC团队博客

## 功能描述

> 1.定下模板，前后端分开，后端用API返回带有样式的数据内容，前端调用。

> 2.API列表：

获取日志：GET    /api/blog

创建日志：POST   /api/blog

修改日志：PUT    /api/blog/:blog_id

删除日志：DELETE /api/blog/:blog_id/

创建用户：POST   /api/user/:username

获取用户：GET    /api/user:username

删除用户：DELETE /api/user:username

> 3.前端页面

首页:   GET /

登录页：GET /login

注销页：GET /logout

时间轴：GET /time

日志详情页：GET /blog/:blog_id(通过API获取日志内容)

## 协议

MIT
