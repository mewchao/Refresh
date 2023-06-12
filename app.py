from tkinter import Image
import numpy as np
from flask import Flask, request, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.session import Session
import http.client, urllib, json
import jwt
import model
from datetime import datetime, timedelta

app = Flask(__name__)

app.config['SECRET_KEY'] = '"sjbdhajshuaikf56a9dsuadhusjhvdsada4789dsaugsaucsc979s6a1ds"'

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



@app.route('/user/register', methods=['POST'])
def register():
    if request.method == 'POST':

        param = request.form.to_dict()  # 字典param
        username = param.get('username')
        password = param.get('password')
        email = param.get('email')

        # 检查参数是否符合要求
        if len(username) > 16:
            return jsonify({'code': '400', 'msg': '用户名长度不能超过16个字符'})

        if len(password) < 6 or not any(char.isdigit() for char in password) or not any(
                char.isalpha() for char in password):
            return jsonify({'code': '400', 'msg': '密码必须包含至少6个字符，且包含数字和字母'})

        # 查询数据库，判断用户名是否已经存在
        user = Users.query.filter_by(username=username).first()
        if user is not None:
            return jsonify({'code': '400', 'msg': '用户名已经存在'})

        # 查询数据库，判断邮箱是否已经存在
        user = Users.query.filter_by(email=email).first()
        if user is not None:
            return jsonify({'code': '400', 'msg': '该邮箱已经被注册'})

        # 创建新用户
        user = Users(username=username, password=password, email=email)
        Session.add(user)
        Session.commit()

        db.session.rollback()
        return jsonify({'code': '200', 'msg': '注册成功'})


@app.route('/user/login', methods=['POST'])
def login():
    # 输入用户名和密码
    username = request.values.get('username')
    password = request.values.get('password')
    # 查询数据库是否有此用户
    data = Session.query(Users).filter(
        Users.username == username, Users.password == password).all()
    # 回滚
    db.session.rollback()
    # 都不为空
    if username and password:
        # 查询到此用户
        if len(data) >= 1:

            # 生成token 5小时内有效
            payload = {'username': username, 'exp': datetime.utcnow() + timedelta(hours=5)}
            secret_key = 'sjbdhajshuaikf56a9dsuadhusjhvdsada4789dsaugsaucsc979s6a1ds'
            algorithm = 'HS256'
            token = jwt.encode(payload, secret_key, algorithm=algorithm)

            # 登录成功->使用 Session 来存储用户登录状态和个人信息
            session['username'] = request.form['username']

            return jsonify({'code': '200', 'msg': '登录成功', 'token': token})
        return jsonify({'code': '401', 'msg': '账号或密码不正确'})
    return jsonify({'code': '404', 'msg': '账号或密码为空'})

@app.route('/user/logout')
def logout():
    # 清除Session
    session.pop('username', None)

# 用户界面
@app.route('/user/index')
def api_user_profile():
    # 如果已登录，得到用户名
    if 'username' in session:
        username = session.get('username')
    # 从数据库中获取用户信息
    user = Users.query.filter_by(name=username).all()
    # 将 Python 对象转换成 JSON 格式并返回
    return jsonify(user)

# 文字识别并且返回识别结果
@app.route('/api/app/text_classification', methods=['POST'])
def text_classification():
    # 调用api
    if request.method == 'POST':
        word = request.form.get('word')
        key = request.form.get('key')
    conn = http.client.HTTPSConnection('apis.tianapi.com')  # 接口域名
    params = urllib.parse.urlencode({'key': key, 'word': word})
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    conn.request('POST', '/lajifenlei/index', params, headers)
    tianapi = conn.getresponse()
    result = tianapi.read()
    data = result.decode('utf-8')
    # 获取的返回字典
    dict_data = json.loads(data)

    code = dict_data['code']
    msg = dict_data['msg']
    list_data = dict_data['result']['list']  # 获取'result'中的'list'列表.一个包含一个字典元素的列表
    new_list_data = []

    for item in list_data:
        name = item['name']  # 提取'name'键对应的值
        type = item['type']  # 提取'type'键对应的值
        # 根据对应的值给出类型
        if type == 0:
            type_transform = "可回收"
        if type == 1:
            type_transform = "有害"
        if type == 2:
            type_transform = "厨余(湿)"
        if type == 3:
            type_transform = "其他(干)"
        explain = item['explain']  # 提取'explain'键对应的值K
        contain = item['contain']  # 提取'contain'键对应的值
        tip = item['tip']  # 提取'tip'键对应的值
        # 新增键值：
        item.update({"type_name": type_transform})
        new_list_data.append(item)
    try:
        new_list_data = {"code": code, "msg": msg, "result": new_list_data}
        return json.dumps(new_list_data)
    except ValueError as e:
        return json.dumps({'error': str(e)})

@app.route('/app/picture_classification', methods=['POST'])
def predict():
    # 读取图片数据
    img_file = request.files['image']
    img = Image.open(img_file.stream)
    img = img.resize((150, 150))
    img = np.array(img) / 255.0
    img = np.expand_dims(img, axis=0)

    # 进行预测
    pred = model.predict(img)[0]
    label = np.argmax(pred)

    # 返回预测结果
    return jsonify({'label': str(label)})


if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True)
