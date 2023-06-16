from datetime import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.session import Session

app = Flask(__name__)

app.config['SECRET_KEY'] = "sjbdhajshuaikf56a9dsuadhusjhvdsada4789dsaugsaucsc979s6a1ds"

SECRET_KEY = "sjbdhajshuaikf56a9dsuadhusjhvdsada4789dsaugsaucsc979s6a1ds"

# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://账号:密码@数据库ip地址:端口号/数据库名"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://root:123456@127.0.0.1:3306/winter"

# 关闭数据库修改跟踪操作[提高性能]，可以设置为True，这样可以跟踪操作：
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 开启输出底层执行的sql语句
app.config['SQLALCHEMY_ECHO'] = True

# 开启数据库的自动提交功能[一般不使用]
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = False

# 创建了一个 SQLAlchemy 对象 db
db = SQLAlchemy(app)

# Session 是 SQLAlchemy 中的一个类，用于管理数据库会话和事务
Session = Session(db)


# 数据库的模型，继承
class Role(db.Model):
    # 定义表名
    __tablename__ = "roles"

    # 定义字段
    id = db.Column(db.Integer, primary_key=True, index=True)  # 设置主键, 默认自增
    name = db.Column(db.String(16), unique=True)


class Users(db.Model):
    # 用户表格
    __tablename__ = "users"
    # 用户id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # 用户名
    username = db.Column(db.String(16), unique=True)
    # 密码
    password = db.Column(db.String(128), nullable=False)
    # 邮箱
    email = db.Column(db.String(255), unique=True, index=True)
    # 积分值
    integral = db.Column(db.Integer, default=0)
    # 外键 需要传参-ForeignKey,表名.id
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))


# 定义项目模型类
class Projects(db.Model):
    # 项目id
    project_id = db.Column(db.Integer, primary_key=True)
    # 项目名称
    project_name = db.Column(db.String(100), nullable=False)
    # 项目描述
    project_description = db.Column(db.String(255))
    # 项目图片文件名
    project_image_filename = db.Column(db.String(100))
    # 项目图片URL
    project_image_url = db.Column(db.String(200))
    # 项目创建时间
    project_datetime = db.Column(db.DateTime, default=datetime.utcnow)
    # 项目创建时间的星期信息
    project_weekday = db.Column(db.Integer)

    def set_weekday(self):
        # 通过调用created_at.weekday()方法获取星期信息
        if self.project_datetime is not None:
            self.project_weekday = self.project_datetime.weekday()
