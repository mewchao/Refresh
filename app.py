from datetime import datetime, timedelta
from tkinter import Image
from PIL import Image
from flask import request, session, jsonify
import http.client
import json
import urllib
import jwt
import numpy as np
import tensorflow as tf
import my_token
from sql_class import app, Role, Users, Projects, db, SECRET_KEY, Session


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
            # 生成token 5 小时内有效
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
    return jsonify({'code': '200', 'msg': '退出登录成功'})


# 用户界面
@app.route('/user/index')
def api_user_profile():
    # 如果已登录，得到用户名
    if 'username' in session:
        username = session.get('username')
        # 从数据库中获取用户信息
        user = Users.query.filter_by(username=username).all()[0]
        # 将 Python 对象转换成 JSON 格式并返回
        return json.dumps({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'integral': user.integral})
    else:
        return json.dumps({"code": 404, "msg": "请先进行登录"})


# 定义项目列表的API路由
# 添加项目的路由
@app.route('/index/projects', methods=['POST'])
def add_project():
    token = request.headers.get('token')

    if my_token.is_token_valid(token, SECRET_KEY):
        # 从请求中获取项目信息
        project_data = request.json
        print(project_data)

        project_name = project_data.get('project_name')
        project_description = project_data.get('project_description')
        project_image_filename = project_data.get('project_image_filename')
        project_image_url = project_data.get('project_image_url')

        # 创建新的项目对象
        new_project = Projects(
            project_name=project_name,
            project_description=project_description,
            project_image_filename=project_image_filename,
            project_image_url=project_image_url,
            project_datetime=datetime.utcnow()  # 设置当前日期和时间
        )
        # 设置项目的创建时间和星期信息
        new_project.set_weekday()

        # 将项目添加到数据库
        db.session.add(new_project)
        db.session.commit()

        return json.dumps({"code": 200, "msg": "success"})
    else:
        return json.dumps({"code": 404, "msg": "请先进行登录"})


# 获取项目的路由
@app.route('/index/projects', methods=['GET'])
def get_projects():
    # 查询所有项目
    projects = Projects.query.all()

    # 构建项目列表
    project_list = []
    for project in projects:
        project_data = {
            'project_id': project.project_id,
            'project_name': project.project_name,
            'project_description': project.project_description,
            'project_image_filename': project.project_image_filename,
            'project_image_url': project.project_image_url,
            'project_datetime': project.project_datetime,
            'project_weekday': project.project_weekday,
        }
        project_list.append(project_data)

    # 返回项目列表
    return jsonify(project_list)


# 文字识别并且返回识别结果
@app.route('/api/app/text_classification', methods=['POST'])
def text_classification():
    # 调用api
    if request.method == 'POST':
        word = request.form.get('word')
        key = "6b8c7b0e789eeea19781760728d72be9"
        token = request.headers.get('token')

    if my_token.is_token_valid(token, SECRET_KEY):
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
    else:
        return json.dumps({"code": 404, "msg": "请先进行登录"})


@app.route('/app/picture_classification', methods=['POST'])
def predict():
    # 打开JSON文件
    with open('classify_rule.json', 'r', encoding='utf-8') as f:
        # 读取JSON数据
        data = json.load(f)
    token = request.headers.get('token')

    if my_token.is_token_valid(token, SECRET_KEY):
        # 加载模型
        my_model_drop = tf.keras.models.load_model('my_model2')

        # 读取图片数据
        img_file = request.files['image']

        # 读取待识别的图片
        image = Image.open(img_file.stream)

        # 将图片转换为28x28的灰度图像
        image = image.convert('L').resize((180, 180))

        # 这行代码的作用是将图像数据转换为 NumPy 数组，并将其形状重塑为 (1, 180, 180)。
        # 其中，1 表示批次大小，28 表示图像高度，28 表示图像宽度。同时，将数组中的所有值除以 255.0，以将它们缩放到 [0, 1] 的范围内。

        image_array = np.array(image.getdata()).reshape((image.size[1], image.size[0]))
        input_image = image_array.reshape((1, 180, 180)) / 255.0

        # 假设您的输入张量是 `input_tensor`
        input_tensor = tf.expand_dims(input_image, axis=-1)  # 在最后一个轴上添加通道维度
        input_tensor = tf.repeat(input_tensor, 3, axis=-1)  # 复制通道维度
        # 现在，`input_tensor` 是一个四维张量，形状为 `(None, 180, 180, 3)`

        # print(input_image)
        predictions = my_model_drop.predict(input_tensor)[0]

        # 获取预测结果的标签
        label = np.argmax(predictions)

        # 输出预测结果
        # print(predictions)
        # print(np.argmax(predictions))

        # 返回预测结果
        return jsonify({'garbage': str(data[str(label)])})
    else:
        return json.dumps({"code": 404, "msg": "请先进行登录"})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True)
