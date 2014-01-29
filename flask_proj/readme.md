# flask 总结
[官方文档](http://flask.pocoo.org/docs/)

### Jinja2模板
1. 在项目中，可以先把网站骨架写成一个__基类__, 如：base.html
2. 然后要用的时候，可以__继承__{% extends 'base.html' %}
3. 只能是__单一__继承，但可以层级继承

> [详细Jinja2官方文档](http://jinja.pocoo.org/docs/)

### Werkzeug
> [源码列表](https://github.com/mitsuhiko/werkzeug/tree/master/examples/shortly)
> [Werkzeug文档](http://werkzeug.pocoo.org/docs/)