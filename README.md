# chexi-blog

my blog,built with django\bootstrap

##网站基于`python 3`,使用的包为：


- Django==1.9.3
- Markdown==2.6.5
- PyMySQL==0.6.7
- Pygments==2.0.2
- python-social-auth

<br>

##数据库使用mysql

Python 2.x 上连接MySQL的库倒是不少的，其中比较著名就是MySQLdb.不过，目前MySQLdb并不支持python3.x,不过仍然可以在python 3上使用 mysql

安装PyMySQL

	pip3 install PyMySQL

然后配置MySQL数据库用户名、密码。
在 django `settings.py` 文件开头加上

	import pymysql
	
	pymysql.install_as_MySQLdb()

修改`settings.py`中的

	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.mysql',
	        'NAME': 'your database name', #your database name
	        'USER': 'your database username', #your database username
	        'PASSWORD': 'your database password', #your database password
	
	    }
	}

##网站注册、登录、修改密码、修改用户名，支持第三方qq、Google、git登录
<br>
Google登录利用[`python-social-auth`](https://github.com/omab/python-social-auth "python-social-auth github").`Python Social Auth`是一个支持多种框架（包括Django、
Flask、Pyramid、Webpy、Tornado）且易于使用的实现数十种第三方登录的包，前身是django-social-auth

网站注册、登录、修改密码、修改用户名，第三方qq、git登录是自己实现的。

<br>

## 发布、编辑、分享文章

文章支持markdown语法，代码高亮

1、安装 markdown 模块

	pip install markdown

使用的编辑器为[免费编辑器](https://github.com/lepture/editor "")

后台程序是 python ，使用 `Pygments` 进行代码高亮。
<br><br>

2、安装 Pygments

	pip install Pygments

Pygments css样式可以从这里选[Pygments css](https://github.com/richleland/pygments-css "Pygments css")

比如你喜欢[Pygments css](https://github.com/richleland/pygments-css "Pygments css")里的github.css。下载之后放入 static/css 目录；
然后在 <head> 标签中添加：

	<link rel="stylesheet" href="{% static 'css/github.css' %}">

##发表评论

评论框支持高度自动伸长<br><br>
评论支持回复缩进，即像下面这样

	------
	| a的 | a说-----------------
	| 头像|---------------------
	------
	      ------
		  | b的 | b回复a----------------
		  | 头像|---------------------
		  ------
