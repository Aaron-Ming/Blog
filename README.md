# SICBlog
SIC团队博客

## 功能描述

> 1. 定下模板，前后端分开，后端用API返回带有样式的数据内容，前端调用。
> 2. API列表：

获取日志：GET    /api/blog
创建日志：POST   /api/blog
修改日志：PUT    /api/blog/:blog_id
删除日志：DELETE /api/blog/:blog_id/
创建用户：POST   /api/user
获取用户：GET    /api/user

> 3. 前端页面

首页:   GET /
注册页：GET /signup
登录页：GET /signin
注销页：GET /signout
日志详情页：GET /blog/:blog_id

